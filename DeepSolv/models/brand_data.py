"""
Pydantic models for brand data validation and serialization
"""
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class PolicyType(str, Enum):
    """Policy types"""
    PRIVACY = "privacy"
    REFUND = "refund"
    RETURN = "return"
    TERMS = "terms"
    SHIPPING = "shipping"


class LinkType(str, Enum):
    """Important link types"""
    CONTACT = "contact"
    ABOUT = "about"
    BLOG = "blog"
    CAREERS = "careers"
    PRESS = "press"
    ORDER_TRACKING = "order_tracking"
    SIZE_GUIDE = "size_guide"
    SHIPPING = "shipping"
    RETURNS = "returns"
    FAQ = "faq"


class SocialPlatform(str, Enum):
    """Social media platforms"""
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    PINTEREST = "pinterest"
    SNAPCHAT = "snapchat"
    WHATSAPP = "whatsapp"
    TELEGRAM = "telegram"


class ProductVariant(BaseModel):
    """Product variant model"""
    id: Optional[int] = None
    title: Optional[str] = None
    option1: Optional[str] = None
    option2: Optional[str] = None
    option3: Optional[str] = None
    sku: Optional[str] = None
    requires_shipping: Optional[bool] = None
    taxable: Optional[bool] = None
    featured_image: Optional[str] = None
    available: Optional[bool] = None
    price: Optional[str] = None
    grams: Optional[int] = None
    compare_at_price: Optional[str] = None
    position: Optional[int] = None
    product_id: Optional[int] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class Product(BaseModel):
    """Product model"""
    id: Optional[str] = None
    title: Optional[str] = None
    handle: Optional[str] = None
    vendor: Optional[str] = None
    product_type: Optional[str] = None
    price: Optional[float] = None
    compare_at_price: Optional[float] = None
    available: Optional[bool] = None
    tags: List[str] = Field(default_factory=list)
    images: List[str] = Field(default_factory=list)
    variants: List[ProductVariant] = Field(default_factory=list)
    description: Optional[str] = None
    url: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class HeroProduct(BaseModel):
    """Hero product model"""
    title: Optional[str] = None
    price: Optional[str] = None
    image_url: Optional[str] = None
    product_url: Optional[str] = None
    description: Optional[str] = None


class Policy(BaseModel):
    """Policy model"""
    type: PolicyType
    title: Optional[str] = None
    content: Optional[str] = None
    url: Optional[str] = None


class FAQ(BaseModel):
    """FAQ model"""
    question: str
    answer: str
    category: Optional[str] = None


class SocialHandle(BaseModel):
    """Social media handle model"""
    platform: str
    username: Optional[str] = None
    url: str
    followers_count: Optional[int] = None


class ContactInfo(BaseModel):
    """Contact information model"""
    emails: List[str] = Field(default_factory=list)
    phone_numbers: List[str] = Field(default_factory=list)
    addresses: List[str] = Field(default_factory=list)
    support_hours: Optional[str] = None


class ImportantLink(BaseModel):
    """Important link model"""
    title: str
    url: str
    type: str  # Using str instead of LinkType for flexibility


class BrandContext(BaseModel):
    """Main brand context model - the complete response"""
    brand_name: Optional[str] = None
    website_url: str
    favicon_url: Optional[str] = None
    
    # Products
    product_catalog: List[Product] = Field(default_factory=list)
    products: List[Product] = Field(default_factory=list, description="Legacy products field for backward compatibility")
    hero_products: List[HeroProduct] = Field(default_factory=list)
    product_count: int = 0
    
    # Policies and content
    policies: List[Policy] = Field(default_factory=list)
    faqs: List[FAQ] = Field(default_factory=list)
    
    # Social and contact
    social_handles: List[SocialHandle] = Field(default_factory=list)
    contact_info: Optional[ContactInfo] = None
    
    # Brand information
    brand_description: Optional[str] = None
    about_us: Optional[str] = None
    brand_story: Optional[str] = None
    
    # Navigation and structure
    important_links: List[ImportantLink] = Field(default_factory=list)
    
    # Competitor information
    competitors: List[Dict[str, Any]] = Field(default_factory=list, description="List of detailed competitor information")
    competitor_urls: List[str] = Field(default_factory=list, description="List of competitor URLs (legacy)")
    
    # Technical metadata
    shopify_theme: Optional[str] = None
    apps_detected: List[str] = Field(default_factory=list)
    
    # Analysis metadata
    analysis_date: Optional[datetime] = None
    analysis_duration: Optional[float] = None
    pages_analyzed: int = 0

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class APIRequest(BaseModel):
    """API request model"""
    website_url: str = Field(..., description="Shopify store URL to analyze")
    force_refresh: bool = Field(default=False, description="Force fresh scrape ignoring cache")


class APIResponse(BaseModel):
    """API response model"""
    success: bool
    data: Optional[BrandContext] = None
    message: Optional[str] = None
    timestamp: Optional[datetime] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ErrorResponse(BaseModel):
    """Error response model"""
    success: bool = False
    error: str
    details: Optional[str] = None
    timestamp: Optional[datetime] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class CompetitorRequest(BaseModel):
    """Competitor analysis request model"""
    website_url: str = Field(..., description="Main store URL to find competitors for")
    limit: int = Field(default=5, ge=1, le=10, description="Maximum number of competitors to analyze")
    force_refresh: bool = Field(default=False, description="Force fresh analysis ignoring cache")


class CompetitorAnalysis(BaseModel):
    """Competitor analysis response model"""
    main_store: BrandContext
    competitors: List[BrandContext] = Field(default_factory=list)
    total_competitors_found: int = 0
    total_competitors_analyzed: int = 0
    analysis_summary: Optional[Dict[str, Any]] = None


class CompetitorResponse(BaseModel):
    """Competitor analysis API response"""
    success: bool
    data: Optional[CompetitorAnalysis] = None
    message: Optional[str] = None
    timestamp: Optional[datetime] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# Request/Response models for API
class BrandAnalysisRequest(BaseModel):
    """Request model for brand analysis"""
    website_url: str = Field(..., description="Website URL to analyze")
    force_refresh: bool = Field(default=False, description="Force refresh of cached data")
    include_competitors: bool = Field(default=False, description="Include competitor analysis")
    include_policies: bool = Field(default=True, description="Include policies parsing")
    include_about: bool = Field(default=True, description="Include about page parsing")
    include_faqs: bool = Field(default=True, description="Include FAQs parsing")
    max_competitors: int = Field(default=5, ge=1, le=20, description="Maximum competitors to find")


class BrandAnalysisResponse(BaseModel):
    """Response model for brand analysis"""
    success: bool
    brand_data: Optional[BrandContext] = None
    analysis_time: datetime
    cached: bool = False
    error: Optional[str] = None


class CompetitorSearchRequest(BaseModel):
    """Request model for competitor search"""
    website_url: str = Field(..., description="Website URL to find competitors for")
    limit: int = Field(default=5, ge=1, le=20, description="Maximum competitors to return")


class CompetitorSearchResponse(BaseModel):
    """Response model for competitor search"""
    success: bool
    competitors: List[Dict[str, Any]] = []
    total_found: int = 0
    search_time: datetime
    error: Optional[str] = None


# Export all models
__all__ = [
    "Product", "HeroProduct", "Policy", "FAQ", "SocialHandle", 
    "ImportantLink", "ContactInfo", "BrandContext",
    "CompetitorAnalysis",
    "BrandAnalysisRequest", "BrandAnalysisResponse",
    "CompetitorSearchRequest", "CompetitorSearchResponse"
]
