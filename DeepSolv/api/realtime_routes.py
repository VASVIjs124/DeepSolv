"""
Real-time Shopify Store Analysis API Endpoints
FastAPI routes for real-time store analysis and insights
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict, Any
from datetime import datetime
import asyncio
import logging

from database.dependencies import get_db
from services.realtime_analyzer import RealtimeStoreAnalyzer

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/realtime", tags=["Real-time Analysis"])

# Initialize analyzer
analyzer = RealtimeStoreAnalyzer()

# Request/Response Models
class StoreAnalysisRequest(BaseModel):
    url: str
    save_to_database: bool = True
    include_recommendations: bool = True

class BulkAnalysisRequest(BaseModel):
    urls: List[str]
    save_to_database: bool = True
    max_concurrent: int = 3

class ComparisonRequest(BaseModel):
    urls: List[str]
    include_detailed_metrics: bool = True

class StoreAnalysisResponse(BaseModel):
    success: bool
    brand_id: Optional[int] = None
    brand_name: str
    website_url: str
    analysis_timestamp: str
    data_quality_score: float
    insights: Dict[str, Any]
    competitive_metrics: Dict[str, Any]
    recommendations: List[Dict[str, str]]
    saved_to_database: bool
    error: Optional[str] = None

@router.post("/analyze", response_model=StoreAnalysisResponse)
async def analyze_store(request: StoreAnalysisRequest):
    """
    Analyze a single Shopify store in real-time
    
    This endpoint fetches comprehensive data from any given Shopify store including:
    - Products, collections, and pricing
    - SEO analysis and performance metrics
    - Social media presence and contact information
    - Shopify-specific features (theme, apps, etc.)
    - Competitive analysis and recommendations
    """
    try:
        logger.info(f"🔍 Starting real-time analysis for: {request.url}")
        
        # Perform analysis
        result = await analyzer.analyze_and_store_shop(
            url=request.url,
            save_to_db=request.save_to_database
        )
        
        if not result['success']:
            raise HTTPException(status_code=400, detail=result.get('error', 'Analysis failed'))
        
        logger.info(f"✅ Analysis completed for: {result['brand_name']}")
        
        # Return the result directly since it matches the expected format
        return result
        
    except Exception as e:
        logger.error(f"❌ Error analyzing {request.url}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.post("/analyze/bulk")
async def bulk_analyze_stores(request: BulkAnalysisRequest):
    """
    Analyze multiple Shopify stores in bulk
    
    Processes multiple store URLs concurrently and provides:
    - Individual analysis results for each store
    - Bulk analysis summary with aggregate metrics
    - Success rate and quality metrics across all stores
    """
    try:
        if len(request.urls) > 50:
            raise HTTPException(status_code=400, detail="Maximum 50 URLs allowed per bulk request")
        
        logger.info(f"🔄 Starting bulk analysis of {len(request.urls)} stores")
        
        # Perform bulk analysis
        result = analyzer.bulk_analyze_stores(
            urls=request.urls,
            save_to_db=request.save_to_database
        )
        
        logger.info(f"🎉 Bulk analysis completed: {result['successful_analyses']}/{result['total_stores']} successful")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Bulk analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Bulk analysis failed: {str(e)}")

@router.post("/compare")
async def compare_stores(request: ComparisonRequest):
    """
    Compare multiple Shopify stores without saving to database
    
    Provides real-time comparison analysis including:
    - Performance metrics comparison
    - Product catalog comparison
    - SEO and social media presence comparison
    - Competitive positioning insights
    """
    try:
        if len(request.urls) < 2:
            raise HTTPException(status_code=400, detail="At least 2 URLs required for comparison")
        
        if len(request.urls) > 10:
            raise HTTPException(status_code=400, detail="Maximum 10 URLs allowed for comparison")
        
        logger.info(f"⚖️  Starting comparison of {len(request.urls)} stores")
        
        # Perform comparison
        result = analyzer.get_real_time_comparison(request.urls)
        
        logger.info(f"✅ Comparison completed for {result['stores_compared']} stores")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Comparison error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Comparison failed: {str(e)}")

@router.get("/quick-check")
async def quick_store_check(
    url: str = Query(..., description="Store URL to check"),
    check_shopify: bool = Query(True, description="Verify if it's a Shopify store")
):
    """
    Quick check to verify if a URL is a Shopify store
    
    Lightweight endpoint for validation before full analysis
    """
    try:
        logger.info(f"🔍 Quick check for: {url}")
        
        # Clean URL
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Quick Shopify check
        is_shopify = analyzer.fetcher.is_shopify_store(url) if check_shopify else True
        
        # Basic info fetch
        basic_info = analyzer.fetcher.fetch_store_basic_info(url)
        
        result = {
            'url': url,
            'is_shopify_store': is_shopify,
            'accessible': basic_info.get('status_code', 0) == 200,
            'brand_name': basic_info.get('brand_name', 'Unknown'),
            'title': basic_info.get('title', ''),
            'has_products_json': analyzer.fetcher._test_endpoint(url.rstrip('/') + '/products.json'),
            'check_timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"✅ Quick check completed: {result['brand_name']} ({'Shopify' if is_shopify else 'Not Shopify'})")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Quick check error for {url}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Quick check failed: {str(e)}")

@router.get("/analyze/{brand_id}/refresh")
async def refresh_brand_analysis(brand_id: int):
    """
    Refresh analysis for an existing brand in the database
    """
    try:
        # Import here to avoid circular imports
        from database.dependencies import get_db_session
        from database.crud import BrandCRUD
        
        with get_db_session() as session:
            brand = BrandCRUD.get_brand_by_id(session, brand_id)
            if not brand:
                raise HTTPException(status_code=404, detail="Brand not found")
            
            logger.info(f"🔄 Refreshing analysis for brand {brand_id}: {brand.brand_name}")
            
            # Perform fresh analysis
            result = await analyzer.analyze_and_store_shop(
                url=brand.website_url,
                save_to_db=True
            )
            
            logger.info(f"✅ Refresh completed for: {result['brand_name']}")
            
            return result
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error refreshing brand {brand_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Refresh failed: {str(e)}")

@router.get("/status")
async def analyzer_status():
    """
    Get status and health check of the real-time analyzer
    """
    try:
        # Test basic functionality
        test_result = analyzer.fetcher.is_shopify_store("https://shopify.com")
        
        return {
            'status': 'operational',
            'analyzer_ready': True,
            'last_check': datetime.now().isoformat(),
            'capabilities': {
                'single_analysis': True,
                'bulk_analysis': True,
                'store_comparison': True,
                'database_integration': True,
                'recommendation_engine': True
            },
            'limits': {
                'max_bulk_urls': 50,
                'max_comparison_urls': 10,
                'timeout_seconds': 30
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Status check failed: {str(e)}")
        return {
            'status': 'error',
            'analyzer_ready': False,
            'error': str(e),
            'last_check': datetime.now().isoformat()
        }

@router.get("/insights/trending")
async def get_trending_insights():
    """
    Get trending insights from recent analyses
    """
    try:
        # Import database dependencies
        from database.dependencies import get_db_session
        from database.crud import BrandCRUD
        
        with get_db_session() as session:
            # Get recent brands (last 100)
            recent_brands = BrandCRUD.get_brands(session, skip=0, limit=100)
            
            if not recent_brands:
                return {'message': 'No recent analyses found'}
            
            # Analyze trends
            themes = {}
            apps = {}
            countries = {}
            
            for brand in recent_brands:
                # Theme analysis
                theme = getattr(brand, 'shopify_theme', 'Unknown')
                if theme and theme != 'Unknown':
                    themes[theme] = themes.get(theme, 0) + 1
                
                # Apps analysis (if available)
                apps_detected = getattr(brand, 'apps_detected', '')
                if apps_detected:
                    for app in apps_detected.split(', '):
                        if app.strip():
                            apps[app.strip()] = apps.get(app.strip(), 0) + 1
            
            # Sort by popularity
            trending_themes = sorted(themes.items(), key=lambda x: x[1], reverse=True)[:10]
            trending_apps = sorted(apps.items(), key=lambda x: x[1], reverse=True)[:10]
            
            return {
                'analysis_timestamp': datetime.now().isoformat(),
                'total_recent_analyses': len(recent_brands),
                'trending_insights': {
                    'popular_themes': [{'name': theme, 'usage_count': count} for theme, count in trending_themes],
                    'popular_apps': [{'name': app, 'usage_count': count} for app, count in trending_apps],
                    'analysis_summary': {
                        'unique_themes': len(themes),
                        'unique_apps': len(apps),
                        'most_popular_theme': trending_themes[0][0] if trending_themes else 'None',
                        'most_popular_app': trending_apps[0][0] if trending_apps else 'None'
                    }
                }
            }
            
    except Exception as e:
        logger.error(f"❌ Error getting trending insights: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get insights: {str(e)}")

# Background task for async analysis
async def background_analysis(urls: List[str], save_to_db: bool = True):
    """Background task for processing large bulk analyses"""
    try:
        result = analyzer.bulk_analyze_stores(urls, save_to_db)
        logger.info(f"🎉 Background analysis completed: {result['successful_analyses']}/{result['total_stores']} successful")
        return result
    except Exception as e:
        logger.error(f"❌ Background analysis error: {str(e)}")
        return {'error': str(e)}

@router.post("/analyze/background")
async def start_background_analysis(
    background_tasks: BackgroundTasks,
    request: BulkAnalysisRequest
):
    """
    Start a background bulk analysis task for large datasets
    
    For processing 25+ stores, this endpoint starts the analysis in the background
    and returns immediately with a task ID for status checking
    """
    if len(request.urls) < 25:
        raise HTTPException(
            status_code=400, 
            detail="Use regular bulk analysis endpoint for less than 25 URLs"
        )
    
    if len(request.urls) > 200:
        raise HTTPException(
            status_code=400, 
            detail="Maximum 200 URLs allowed for background analysis"
        )
    
    # Generate task ID
    task_id = f"bulk_{int(datetime.now().timestamp())}"
    
    # Add to background tasks
    background_tasks.add_task(
        background_analysis,
        request.urls,
        request.save_to_database
    )
    
    logger.info(f"🚀 Started background analysis task {task_id} for {len(request.urls)} URLs")
    
    return {
        'task_id': task_id,
        'status': 'started',
        'urls_count': len(request.urls),
        'started_at': datetime.now().isoformat(),
        'estimated_completion_minutes': len(request.urls) * 0.5  # Rough estimate
    }

# Export router
__all__ = ['router']
