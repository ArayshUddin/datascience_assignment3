"""
Scraper Router
Endpoints for scraping articles
"""
from typing import List, Optional, Dict
from pydantic import BaseModel, Field, HttpUrl
from fastapi import APIRouter, HTTPException, BackgroundTasks, UploadFile, File
from services.scraper import MediumScraper
from services.csv_handler import CSVHandler
from services.url_reader import read_urls_from_excel
from services.progress_tracker import progress_tracker
import os
import uuid
import tempfile
import logging
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/scraper", tags=["scraper"])

scraper = MediumScraper()
csv_handler = CSVHandler()


class ScrapeURLsRequest(BaseModel):
    urls: List[str] = Field(..., description="List of Medium article URLs to scrape")
    delay: float = Field(1.0, ge=0.1, le=10.0, description="Delay between requests in seconds")


class ScrapeExcelRequest(BaseModel):
    file_path: str = Field(..., description="Path to Excel file containing URLs")
    column_name: Optional[str] = Field(None, description="Column name containing URLs (uses first column if not specified)")
    delay: float = Field(1.0, ge=0.1, le=10.0, description="Delay between requests in seconds")


class ScrapeResponse(BaseModel):
    message: str
    total_urls: int
    successful: int
    failed: int
    saved_to_csv: bool


class ScrapeStatusResponse(BaseModel):
    status: str
    total_articles: int
    message: str


class ProgressResponse(BaseModel):
    job_id: str
    total: int
    completed: int
    successful: int
    failed: int
    percentage: float
    status: str
    description: str
    estimated_seconds_remaining: Optional[float] = None
    current_url: Optional[str] = None
    recent_completed: List[Dict] = []


@router.post("/scrape-urls", response_model=dict)
async def scrape_urls(request: ScrapeURLsRequest, background_tasks: BackgroundTasks):
    """
    Scrape Medium articles from provided URLs
    
    This endpoint accepts a list of URLs and scrapes them.
    Returns a job_id for progress tracking.
    Results are saved to scrapping_results.csv
    """
    try:
        if not request.urls:
            raise HTTPException(status_code=400, detail="No URLs provided")
        
        # Filter out URLs that already exist
        new_urls = [url for url in request.urls if not csv_handler.article_exists(url)]
        
        if not new_urls:
            return {
                "job_id": None,
                "message": "All URLs have already been scraped",
                "total_urls": len(request.urls),
                "skipped": len(request.urls)
            }
        
        logger.info(f"Scraping {len(new_urls)} URLs (skipped {len(request.urls) - len(new_urls)} already scraped)")
        
        # Create job ID for progress tracking
        job_id = str(uuid.uuid4())
        progress_tracker.start_job(job_id, len(new_urls), f"Scraping {len(new_urls)} URLs")
        
        # Run scraping in background
        def scrape_background():
            try:
                # Progress callback (not needed since we pass job_id)
                def progress_callback(successful, url):
                    pass  # Progress is tracked via job_id
                
                # Scrape articles with progress tracking
                results = scraper.scrape_multiple(new_urls, delay=request.delay, progress_callback=progress_callback, job_id=job_id)
                
                # Save to CSV
                if results:
                    csv_handler.save_articles(results, append=True)
                
                # Mark job as completed
                progress_tracker.complete_job(job_id)
            except Exception as e:
                logger.error(f"Error in background scraping: {str(e)}")
                progress_tracker.fail_job(job_id, str(e))
        
        # Start background task
        background_tasks.add_task(scrape_background)
        
        return {
            "job_id": job_id,
            "message": f"Scraping started for {len(new_urls)} URLs",
            "total_urls": len(new_urls),
            "skipped": len(request.urls) - len(new_urls)
        }
        
    except Exception as e:
        logger.error(f"Error in scrape_urls: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Scraping error: {str(e)}")


@router.post("/scrape-excel", response_model=ScrapeResponse)
async def scrape_excel(request: ScrapeExcelRequest):
    """
    Scrape Medium articles from URLs in an Excel file (file path)
    
    Reads URLs from the specified Excel file and scrapes them.
    Results are saved to scrapping_results.csv
    """
    try:
        # Check if file exists
        if not os.path.exists(request.file_path):
            raise HTTPException(status_code=404, detail=f"File not found: {request.file_path}")
        
        # Read URLs from Excel
        urls = read_urls_from_excel(request.file_path, request.column_name)
        
        if not urls:
            raise HTTPException(status_code=400, detail="No valid URLs found in Excel file")
        
        # Filter out URLs that already exist
        new_urls = [url for url in urls if not csv_handler.article_exists(url)]
        
        if not new_urls:
            return ScrapeResponse(
                message="All URLs from Excel have already been scraped",
                total_urls=len(urls),
                successful=0,
                failed=0,
                saved_to_csv=False
            )
        
        logger.info(f"Scraping {len(new_urls)} URLs from Excel (skipped {len(urls) - len(new_urls)} already scraped)")
        
        # Create job ID for progress tracking
        job_id = str(uuid.uuid4())
        progress_tracker.start_job(job_id, len(new_urls), f"Scraping {len(new_urls)} URLs from Excel")
        
        # Progress callback (not needed since we pass job_id)
        def progress_callback(successful, url):
            pass  # Progress is tracked via job_id
        
        # Scrape articles with progress tracking
        results = scraper.scrape_multiple(new_urls, delay=request.delay, progress_callback=progress_callback, job_id=job_id)
        
        # Mark job as completed
        progress_tracker.complete_job(job_id)
        
        # Save to CSV
        saved = False
        if results:
            saved = csv_handler.save_articles(results, append=True)
        
        successful = len(results)
        failed = len(new_urls) - successful
        
        return ScrapeResponse(
            message=f"Scraped {successful} articles from Excel successfully",
            total_urls=len(urls),
            successful=successful,
            failed=failed,
            saved_to_csv=saved
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in scrape_excel: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Scraping error: {str(e)}")


@router.post("/scrape-excel-upload", response_model=dict)
async def scrape_excel_upload(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    delay: float = 1.0,
    column_name: Optional[str] = None
):
    """
    Scrape Medium articles from uploaded Excel file
    
    Upload an Excel file containing URLs and scrape them.
    Returns a job_id for progress tracking.
    """
    try:
        # Validate file type
        if not file.filename.endswith(('.xlsx', '.xls')):
            raise HTTPException(status_code=400, detail="File must be an Excel file (.xlsx or .xls)")
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        try:
            # Read URLs from Excel
            urls = read_urls_from_excel(tmp_path, column_name)
            
            if not urls:
                raise HTTPException(status_code=400, detail="No valid URLs found in Excel file")
            
            # Filter out URLs that already exist
            new_urls = [url for url in urls if not csv_handler.article_exists(url)]
            
            if not new_urls:
                return {
                    "job_id": None,
                    "message": "All URLs from Excel have already been scraped",
                    "total_urls": len(urls),
                    "skipped": len(urls)
                }
            
            # Create job ID for progress tracking
            job_id = str(uuid.uuid4())
            progress_tracker.start_job(job_id, len(new_urls), f"Scraping {len(new_urls)} URLs from {file.filename}")
            
            # Run scraping in background
            def scrape_background():
                try:
                    # Progress callback (not needed since we pass job_id)
                    def progress_callback(successful, url):
                        pass  # Progress is tracked via job_id
                    
                    # Scrape articles with progress tracking
                    results = scraper.scrape_multiple(new_urls, delay=delay, progress_callback=progress_callback, job_id=job_id)
                    
                    # Save to CSV
                    if results:
                        csv_handler.save_articles(results, append=True)
                    
                    # Mark job as completed
                    progress_tracker.complete_job(job_id)
                except Exception as e:
                    logger.error(f"Error in background scraping: {str(e)}")
                    progress_tracker.fail_job(job_id, str(e))
            
            # Start background task
            background_tasks.add_task(scrape_background)
            
            return {
                "job_id": job_id,
                "message": f"Scraping started for {len(new_urls)} URLs",
                "total_urls": len(new_urls),
                "skipped": len(urls) - len(new_urls)
            }
        finally:
            # Clean up temporary file
            try:
                os.unlink(tmp_path)
            except:
                pass
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in scrape_excel_upload: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Scraping error: {str(e)}")


@router.get("/progress/{job_id}", response_model=ProgressResponse)
async def get_progress(job_id: str):
    """Get progress for a scraping job"""
    progress = progress_tracker.get_progress(job_id)
    
    if not progress:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return ProgressResponse(
        job_id=job_id,
        total=progress['total'],
        completed=progress['completed'],
        successful=progress['successful'],
        failed=progress['failed'],
        percentage=progress['percentage'],
        status=progress['status'],
        description=progress['description'],
        estimated_seconds_remaining=progress.get('estimated_seconds_remaining'),
        current_url=progress.get('current_url'),
        recent_completed=progress.get('recent_completed', [])
    )


@router.get("/status", response_model=ScrapeStatusResponse)
async def get_scrape_status():
    """
    Get status of scraped data
    
    Returns total number of articles in CSV
    """
    try:
        count = csv_handler.get_article_count()
        return ScrapeStatusResponse(
            status="success",
            total_articles=count,
            message=f"Total articles in database: {count}"
        )
    except Exception as e:
        logger.error(f"Error getting status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

