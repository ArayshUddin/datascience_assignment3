"""
Search Router
Endpoints for searching similar articles
"""
from typing import List, Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException
from services.search import ArticleSearch
from services.csv_handler import CSVHandler
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/search", tags=["search"])

search_service = ArticleSearch()
csv_handler = CSVHandler()


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Search query (text or keywords)")
    top_k: int = Field(10, ge=1, le=50, description="Number of top results to return")


class ArticleResult(BaseModel):
    url: str
    title: str
    subtitle: Optional[str] = None
    author_name: Optional[str] = None
    claps: int
    reading_time: Optional[str] = None


class SearchResponse(BaseModel):
    query: str
    results: List[ArticleResult]
    total_found: int


@router.post("/similar", response_model=SearchResponse)
async def search_similar_articles(request: SearchRequest):
    """
    Search for similar articles based on text/keywords
    
    Returns top K articles (sorted by similarity and claps) with URL and Title.
    Results are sorted by a combination of similarity score and claps.
    """
    try:
        # Load all articles from CSV
        articles = csv_handler.load_articles()
        
        if not articles:
            raise HTTPException(
                status_code=404, 
                detail="No articles found in database. Please scrape some articles first."
            )
        
        # Search for similar articles
        results = search_service.search_similar_articles(
            query=request.query,
            articles=articles,
            top_k=request.top_k
        )
        
        # Format results (only URL and Title as per requirements)
        formatted_results = []
        for article in results:
            # Helper function to safely get string values (handle NaN)
            def safe_str(value, default=''):
                if value is None:
                    return default
                # Check for float NaN
                if isinstance(value, float):
                    if pd.isna(value):
                        return default
                    # Convert float to string if it's a valid number
                    return str(int(value)) if value == int(value) else str(value)
                # Check for string 'nan'
                if isinstance(value, str) and value.lower() == 'nan':
                    return default
                # Return string representation, or default if empty
                result = str(value).strip() if value else default
                return result if result and result.lower() != 'nan' else default
            
            # Helper function to safely get int values
            def safe_int(value, default=0):
                try:
                    if value is None or (isinstance(value, float) and pd.isna(value)):
                        return default
                    return int(value) if value else default
                except:
                    return default
            
            formatted_results.append(ArticleResult(
                url=safe_str(article.get('url'), ''),
                title=safe_str(article.get('title'), 'No Title'),
                subtitle=safe_str(article.get('subtitle')) or None,
                author_name=safe_str(article.get('author_name')) or None,
                claps=safe_int(article.get('claps'), 0),
                reading_time=safe_str(article.get('reading_time')) or None
            ))
        
        return SearchResponse(
            query=request.query,
            results=formatted_results,
            total_found=len(formatted_results)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in search: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")


@router.get("/top-clapped", response_model=SearchResponse)
async def get_top_clapped_articles(top_k: int = 10):
    """
    Get top K most clapped articles
    
    Returns articles sorted by claps in descending order
    """
    try:
        # Load all articles from CSV
        articles = csv_handler.load_articles()
        
        if not articles:
            raise HTTPException(
                status_code=404, 
                detail="No articles found in database. Please scrape some articles first."
            )
        
        # Sort by claps
        sorted_articles = sorted(
            articles, 
            key=lambda x: x.get('claps', 0), 
            reverse=True
        )[:top_k]
        
        # Format results
        formatted_results = []
        for article in sorted_articles:
            # Helper function to safely get string values (handle NaN)
            def safe_str(value, default=''):
                # Handle None
                if value is None:
                    return default
                # Handle float NaN
                if isinstance(value, float):
                    if pd.isna(value):
                        return default
                    # Convert float to string if it's a valid number
                    return str(int(value)) if value == int(value) else str(value)
                # Handle string 'nan'
                if isinstance(value, str):
                    if value.lower() == 'nan' or value.lower() == 'none':
                        return default
                    return value.strip() if value.strip() else default
                # Convert to string and check
                result = str(value).strip()
                return result if result and result.lower() != 'nan' else default
            
            # Helper function to safely get int values
            def safe_int(value, default=0):
                try:
                    if value is None or (isinstance(value, float) and pd.isna(value)):
                        return default
                    return int(value) if value else default
                except:
                    return default
            
            formatted_results.append(ArticleResult(
                url=safe_str(article.get('url'), ''),
                title=safe_str(article.get('title'), 'No Title'),
                subtitle=safe_str(article.get('subtitle')) or None,
                author_name=safe_str(article.get('author_name')) or None,
                claps=safe_int(article.get('claps'), 0),
                reading_time=safe_str(article.get('reading_time')) or None
            ))
        
        return SearchResponse(
            query="top clapped",
            results=formatted_results,
            total_found=len(formatted_results)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting top clapped: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

