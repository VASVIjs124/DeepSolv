"""
Main FastAPI application for Shopify Store Insights Fetcher
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
import logging
import traceback
from contextlib import asynccontextmanager

from api import router
from api.realtime_routes import router as realtime_router
from database.dependencies import init_database
from config import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Set up templates
templates = Jinja2Templates(directory="templates")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager
    """
    # Startup
    logger.info("Starting Shopify Store Insights Fetcher application")
    if settings.DATABASE_URL:
        init_database()
        logger.info("Database initialized")
    yield
    # Shutdown
    logger.info("Shutting down application")


app = FastAPI(
    title="Shopify Store Insights Fetcher",
    description="A comprehensive API for extracting insights from Shopify stores through web scraping",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Global exception handler for unhandled exceptions
    """
    logger.error(f"Unhandled exception: {str(exc)}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "detail": str(exc) if settings.DEBUG else "An unexpected error occurred"
        }
    )


# HTTP exception handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    Handle HTTP exceptions
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "status_code": exc.status_code
        }
    )


# Include API routes
app.include_router(router)
app.include_router(realtime_router)


# Root endpoint - serve HTML interface
@app.get("/", tags=["Root"], response_class=HTMLResponse)
async def root(request: Request):
    """
    Serve the HTML interface for website analysis
    """
    return templates.TemplateResponse("index.html", {"request": request})


# API info endpoint  
@app.get("/info", tags=["Root"])
async def api_info():
    """
    API information endpoint
    """
    return {
        "message": "Welcome to Shopify Store Insights Fetcher API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/api/v1/health",
        "features": [
            "Brand Analysis",
            "Product Extraction", 
            "Hero Products",
            "Policies",
            "FAQs",
            "Social Media",
            "Contact Information",
            "Competitor Finding"
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
