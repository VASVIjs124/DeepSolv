"""
API routes for the Shopify Store Insights application
"""
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.orm import Session
import logging
from datetime import datetime

from database.dependencies import get_db
from database.crud import BrandCRUD
from services.scraper import WebScraper
from services.parser import ShopifyParser  
from services.realtime_analyzer import RealtimeStoreAnalyzer
from services.competitor_finder import get_competitor_finder
from models.brand_data import (
    BrandContext, 
    BrandAnalysisRequest, 
    BrandAnalysisResponse,
    CompetitorSearchRequest,
    CompetitorSearchResponse,
    ContactInfo
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1", tags=["Brand Analysis"])

# Initialize services  
# parser will be initialized per request with the specific URL
competitor_finder = get_competitor_finder()


@router.post(
    "/analyze",
    response_model=BrandAnalysisResponse,
    summary="Analyze a Shopify store",
    description="Analyze a Shopify store and return comprehensive brand insights"
)
async def analyze_brand(
    request: BrandAnalysisRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Analyze a Shopify store and return comprehensive insights
    
    Args:
        request: Brand analysis request containing URL and options
        background_tasks: FastAPI background tasks
        db: Database session
        
    Returns:
        BrandAnalysisResponse with comprehensive brand data
    """
    try:
        logger.info(f"Starting analysis for {request.website_url}")
        
        # Normalize URL for consistent database lookup
        normalized_url = request.website_url
        if not normalized_url.startswith(('http://', 'https://')):
            normalized_url = f"https://{normalized_url}"
        
        # Initialize CRUD operations
        # BrandCRUD uses static methods, no instantiation needed
        
        # Check if analysis already exists
        if not request.force_refresh:
            existing_brand = BrandCRUD.get_brand_by_url(db, normalized_url)
            if existing_brand:
                logger.info(f"Returning cached analysis for {normalized_url}")
                brand_context = BrandCRUD.get_brand_context(db, normalized_url)
                return BrandAnalysisResponse(
                    success=True,
                    brand_data=brand_context,
                    analysis_time=datetime.now(),
                    cached=True
                )
        
        # Use RealtimeStoreAnalyzer for comprehensive analysis
        logger.info(f"Starting comprehensive analysis using RealtimeStoreAnalyzer for {request.website_url}")
        
        analyzer = RealtimeStoreAnalyzer()
        analysis_result = await analyzer.analyze_and_store_shop(
            url=request.website_url, 
            save_to_db=True
        )
        
        if not analysis_result['success']:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Analysis failed: {analysis_result.get('error', 'Unknown error')}"
            )
        
        # Get the saved brand context from database
        brand_context = BrandCRUD.get_brand_context(db, normalized_url)
        if not brand_context:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Brand data not found after analysis: {normalized_url}"
            )
        
        # Schedule competitor analysis in background if requested  
        # (Competitors are already analyzed by RealtimeStoreAnalyzer)
        
        logger.info(f"Analysis completed for {request.website_url}")
        
        return BrandAnalysisResponse(
            success=True,
            brand_data=brand_context,
            analysis_time=datetime.now(),
            cached=False
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing {request.website_url}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )


@router.post(
    "/analyze-store",
    response_model=Dict[str, Any],
    summary="Analyze Shopify Store - Assignment Endpoint",
    description="Main assignment endpoint that expects website_url and returns Brand Context JSON response"
)
async def analyze_store(
    request: BrandAnalysisRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Assignment-specific endpoint: Analyze a Shopify store and return Brand Context JSON
    
    This is the main endpoint required by the GenAI Developer Assignment:
    - Accepts website_url parameter
    - Returns structured JSON response with Brand Context
    - Handles error codes (401 if website not found, 500 for internal errors)
    
    Args:
        request: Contains website_url to analyze
        background_tasks: Background tasks
        db: Database session
        
    Returns:
        JSON response with Brand Context object or error response
    """
    try:
        logger.info(f"Assignment endpoint - Starting analysis for {request.website_url}")
        
        # Normalize URL
        normalized_url = request.website_url
        if not normalized_url.startswith(('http://', 'https://')):
            normalized_url = f"https://{normalized_url}"
        
        # Check if website exists and is accessible
        try:
            import requests
            response = requests.head(normalized_url, timeout=10, allow_redirects=True)
            if response.status_code == 404:
                raise HTTPException(
                    status_code=401,  # Assignment specifies 401 if website not found
                    detail="Website not found"
                )
        except requests.RequestException:
            raise HTTPException(
                status_code=401,
                detail="Website not found or not accessible"
            )
        
        # Check if brand already exists in database
        existing_brand = BrandCRUD.get_brand_by_url(db, normalized_url)
        
        if existing_brand:
            # Return cached data if available
            logger.info(f"Returning cached data for {normalized_url}")
            brand_context = BrandCRUD.get_brand_context(db, normalized_url)
            if brand_context:
                # Helper function to get policy content by type
                def get_policy_content(policy_type: str) -> str:
                    for policy in brand_context.policies:
                        if policy.type == policy_type:
                            return policy.content or ""
                    return ""
                
                return {
                    "brand_name": brand_context.brand_name,
                    "website_url": brand_context.website_url,
                    "brand_description": brand_context.brand_description,
                    "about_us": brand_context.about_us,
                    "product_catalog": [product.model_dump() for product in brand_context.product_catalog],
                    "hero_products": [product.model_dump() for product in brand_context.hero_products],
                    "privacy_policy": get_policy_content("privacy"),
                    "return_refund_policies": {
                        "return_policy": get_policy_content("return"),
                        "refund_policy": get_policy_content("refund")
                    },
                    "faqs": [faq.model_dump() for faq in brand_context.faqs],
                    "social_handles": [handle.model_dump() for handle in brand_context.social_handles] if brand_context.social_handles else [],
                    "contact_details": brand_context.contact_info.model_dump() if brand_context.contact_info else {},
                    "brand_text_context": brand_context.brand_story,
                    "important_links": [link.model_dump() for link in brand_context.important_links] if brand_context.important_links else [],
                    "competitors": brand_context.competitors,
                    "analysis_timestamp": datetime.now().isoformat(),
                    "cached": True
                }
        
        # Perform new analysis using RealtimeStoreAnalyzer
        logger.info(f"Starting fresh analysis using RealtimeStoreAnalyzer for {normalized_url}")
        
        analyzer = RealtimeStoreAnalyzer()
        analysis_result = await analyzer.analyze_and_store_shop(
            url=normalized_url, 
            save_to_db=True
        )
        
        if not analysis_result['success']:
            raise HTTPException(
                status_code=500,
                detail=f"Analysis failed: {analysis_result.get('error', 'Unknown error')}"
            )
        
        # Get the brand context from database after analysis
        brand_context = BrandCRUD.get_brand_context(db, normalized_url)
        if not brand_context:
            raise HTTPException(
                status_code=500,
                detail="Brand data not found after analysis"
            )
        
        logger.info(f"Assignment endpoint - Analysis completed for {normalized_url}")
        
        # Helper function to get policy content by type
        def get_policy_content(policy_type: str) -> str:
            for policy in brand_context.policies:
                if policy.type == policy_type:
                    return policy.content or ""
            return ""
        
        # Return structured JSON response as required by assignment
        return {
            "brand_name": brand_context.brand_name,
            "website_url": brand_context.website_url,
            "brand_description": brand_context.brand_description,
            "about_us": brand_context.about_us,
            "product_catalog": [product.model_dump() for product in brand_context.product_catalog],
            "hero_products": [product.model_dump() for product in brand_context.hero_products],
            "privacy_policy": get_policy_content("privacy"),
            "return_refund_policies": {
                "return_policy": get_policy_content("return"),
                "refund_policy": get_policy_content("refund")
            },
            "faqs": [faq.model_dump() for faq in brand_context.faqs],
            "social_handles": [handle.model_dump() for handle in brand_context.social_handles] if brand_context.social_handles else [],
            "contact_details": brand_context.contact_info.model_dump() if brand_context.contact_info else {},
            "brand_text_context": brand_context.brand_story,
            "important_links": [link.model_dump() for link in brand_context.important_links] if brand_context.important_links else [],
            "competitors": brand_context.competitors,
            "analysis_timestamp": datetime.now().isoformat(),
            "cached": False
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Assignment endpoint - Error analyzing {request.website_url}: {str(e)}")
        raise HTTPException(
            status_code=500,  # Assignment specifies 500 for internal errors
            detail=f"Internal server error: {str(e)}"
        )


@router.post(
    "/competitors",
    response_model=CompetitorSearchResponse,
    summary="Find competitors for a brand",
    description="Find and analyze competitors for a given brand"
)
async def find_competitors(
    request: CompetitorSearchRequest,
    db: Session = Depends(get_db)
):
    """
    Find competitors for a brand
    
    Args:
        request: Competitor search request
        db: Database session
        
    Returns:
        CompetitorSearchResponse with competitor data
    """
    try:
        logger.info(f"Finding competitors for {request.website_url}")
        
        # Find competitors with detailed information
        competitor_data = await competitor_finder.find_competitors(
            website_url=request.website_url,
            limit=request.limit
        )
        
        if not competitor_data:
            return CompetitorSearchResponse(
                success=True,
                competitors=[],
                total_found=0,
                search_time=datetime.now()
            )
        
        # Convert competitor data to expected format
        competitors = []
        for comp_info in competitor_data:
            competitors.append({
                'url': comp_info.get('url', ''),
                'domain': comp_info.get('domain', ''),
                'title': comp_info.get('title', ''),
                'description': comp_info.get('description', ''),
                'category': comp_info.get('category', ''),
                'strength': comp_info.get('strength', ''),
                'market_position': comp_info.get('market_position', ''),
                'source': comp_info.get('source', ''),
                'insights': {
                    'domain': comp_info.get('domain', ''),
                    'category': comp_info.get('category', ''),
                    'strength': comp_info.get('strength', ''),
                    'market_position': comp_info.get('market_position', ''),
                    'source': comp_info.get('source', '')
                }
            })
        
        return CompetitorSearchResponse(
            success=True,
            competitors=competitors,
            total_found=len(competitors),
            search_time=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"Error finding competitors for {request.website_url}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Competitor search failed: {str(e)}"
        )


@router.get(
    "/brands",
    summary="List analyzed brands",
    description="Get a list of all analyzed brands"
)
async def list_brands(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    List all analyzed brands
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
        
    Returns:
        List of analyzed brands
    """
    try:
        brands = BrandCRUD.get_brands(db, skip=skip, limit=limit)
        
        return {
            "success": True,
            "brands": [
                {
                    "id": brand.id,
                    "website_url": brand.website_url,
                    "brand_name": brand.brand_name,
                    "analysis_date": brand.analysis_date,
                    "last_fetched": brand.last_fetched,
                    "pages_analyzed": brand.pages_analyzed
                }
                for brand in brands
            ],
            "total": len(brands)
        }
        
    except Exception as e:
        logger.error(f"Error listing brands: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list brands: {str(e)}"
        )


@router.get(
    "/brands/{brand_id}",
    response_model=BrandContext,
    summary="Get brand details",
    description="Get detailed information for a specific brand"
)
async def get_brand(
    brand_id: int,
    db: Session = Depends(get_db)
):
    """
    Get detailed brand information
    
    Args:
        brand_id: Brand ID
        db: Database session
        
    Returns:
        Detailed brand context
    """
    try:
        brand = BrandCRUD.get_brand_by_id(db, brand_id)
        if not brand:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Brand with ID {brand_id} not found"
            )
        
        brand_website_url = getattr(brand, 'website_url', '')
        brand_context = BrandCRUD.get_brand_context(db, brand_website_url)
        
        if not brand_context:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Brand with ID {brand_id} not found"
            )
        
        return brand_context
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting brand {brand_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get brand: {str(e)}"
        )


@router.delete(
    "/brands/{brand_id}",
    summary="Delete a brand",
    description="Delete a brand and all associated data"
)
async def delete_brand(
    brand_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a brand and all associated data
    
    Args:
        brand_id: Brand ID
        db: Database session
        
    Returns:
        Success message
    """
    try:
        success = BrandCRUD.delete_brand(db, brand_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Brand with ID {brand_id} not found"
            )
        
        return {"success": True, "message": f"Brand {brand_id} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting brand {brand_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete brand: {str(e)}"
        )


# Health check endpoint
@router.get(
    "/health",
    summary="Health check",
    description="Check the health of the API"
)
async def health_check():
    """
    Health check endpoint
    
    Returns:
        Health status information
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "version": "1.0.0",
        "service": "Shopify Store Insights API"
    }


# Helper functions

async def _parse_brand_content(
    main_url: str,
    scraped_content: Dict[str, Any],
    parser: ShopifyParser,
    include_competitors: bool = False,
    max_competitors: int = 5
) -> BrandContext:
    """
    Parse all scraped content into a BrandContext object
    
    Args:
        main_url: Main website URL
        scraped_content: Dictionary of scraped content
        parser: ShopifyParser instance
        include_competitors: Whether to include competitor analysis
        max_competitors: Maximum number of competitors to find
        
    Returns:
        BrandContext with all parsed data
    """
    # Get main page content
    main_content = scraped_content.get(main_url, {})
    main_html = main_content.get('content', '')
    
    # Parse products from JSON
    products_url = f"{main_url.rstrip('/')}/products.json"
    products_data = scraped_content.get(products_url, {})
    products_json = products_data.get('json', {}) if products_data else {}
    
    # Parse different content types
    products = parser.parse_products_json(products_json) if products_json else []
    hero_products = parser.parse_hero_products_from_html(main_html) if main_html else []
    policies = []  # Policies are parsed separately from policy pages
    social_handles = parser.parse_social_handles_from_html(main_html) if main_html else []
    contact_info = parser.parse_contact_info_from_html(main_html) if main_html else ContactInfo()
    brand_info = parser.parse_brand_info_from_html(main_html) if main_html else {}
    important_links = parser.parse_important_links_from_html(main_html) if main_html else []
    
    # Parse FAQs from dedicated pages
    faqs = []
    faq_urls = [
        f"{main_url.rstrip('/')}/pages/faq",
        f"{main_url.rstrip('/')}/pages/help",
        f"{main_url.rstrip('/')}/pages/support"
    ]
    for faq_url in faq_urls:
        if faq_url in scraped_content:
            faq_content = scraped_content[faq_url].get('content', '')
            if faq_content:
                page_faqs = parser.parse_faqs_from_html(faq_content)
                faqs.extend(page_faqs)
    
    # Find competitors if requested
    competitors = []
    if include_competitors:
        try:
            competitor_urls = await competitor_finder.find_competitors(
                website_url=main_url,
                limit=max_competitors
            )
            competitors = [url for url in competitor_urls]
        except Exception as e:
            logger.error(f"Error finding competitors: {e}")
    
    # Create BrandContext
    brand_context = BrandContext(
        website_url=main_url,
        brand_name=brand_info.get('name', ''),
        brand_description=brand_info.get('description', ''),
        about_us=brand_info.get('about', ''),
        brand_story=brand_info.get('story', ''),
        product_catalog=products,
        hero_products=hero_products,
        policies=policies,
        faqs=faqs,
        social_handles=social_handles,
        contact_info=contact_info,
        important_links=important_links,
        competitors=competitors
    )
    
    return brand_context


async def _analyze_competitors_background(
    brand_id: int,
    competitors: List[str],
    db: Session
):
    """
    Background task to analyze competitors
    
    Args:
        brand_id: Brand ID
        competitors: List of competitor URLs
        db: Database session
    """
    try:
        logger.info(f"Starting background competitor analysis for brand {brand_id}")
        
        # This would perform detailed competitor analysis
        # For now, just log the competitors
        for competitor_url in competitors:
            logger.info(f"Would analyze competitor: {competitor_url}")
            
        logger.info(f"Completed background competitor analysis for brand {brand_id}")
        
    except Exception as e:
        logger.error(f"Error in background competitor analysis: {e}")
