
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from api.routers.scraper import router as scraper_router
from api.routers.search import router as search_router

# Environment configuration
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
API_VERSION = os.getenv("API_VERSION", "1.0.0")
ALLOWED_ORIGINS_STR = os.getenv("ALLOWED_ORIGINS", "*")
ALLOWED_ORIGINS = (
    [origin.strip() for origin in ALLOWED_ORIGINS_STR.split(",")]
    if ALLOWED_ORIGINS_STR and ALLOWED_ORIGINS_STR != "*"
    else ["*"]
)

# Create FastAPI app
app = FastAPI(
    title="Article Scraping & Search API",
    description="API for scraping articles and searching through scraped data by keywords/text.",
    version=API_VERSION,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    base_url = os.getenv("BASE_URL", "http://localhost:8000")
    is_railway = os.getenv("RAILWAY_ENVIRONMENT", "") != ""
    return {
        "message": "Article Scraping & Search API",
        "version": API_VERSION,
        "environment": ENVIRONMENT,
        "base_url": base_url,
        "deployment": "Railway" if is_railway else "Local",
        "docs": f"{base_url}/docs",
        "health": f"{base_url}/health",
        "scraper_routes": {
            "scrape_urls": f"{base_url}/scraper/scrape-urls",
            "scrape_excel": f"{base_url}/scraper/scrape-excel",
            "status": f"{base_url}/scraper/status",
        },
        "search_routes": {
            "similar": f"{base_url}/search/similar",
            "top_clapped": f"{base_url}/search/top-clapped",
        },
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "medium-scraping-api",
        "version": API_VERSION,
        "environment": ENVIRONMENT,
    }


# Mount routers
app.include_router(scraper_router)
app.include_router(search_router)

# Serve frontend static files
frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")
    
    @app.get("/frontend")
    async def serve_frontend():
        """Serve the frontend HTML"""
        index_path = os.path.join(frontend_path, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        return {"message": "Frontend not found"}


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True, log_level="info")
