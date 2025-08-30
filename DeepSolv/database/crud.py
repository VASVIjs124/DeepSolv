"""
CRUD operations for database interactions
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional, List
from datetime import datetime, timezone
import logging

from .models import (
    Brand, Product, HeroProduct, Policy, FAQ, 
    SocialHandle, ImportantLink, ContactDetail
)
from models.brand_data import BrandContext, ContactInfo

logger = logging.getLogger(__name__)


class BrandCRUD:
    """CRUD operations for Brand and related data"""
    
    @staticmethod
    def get_brand_by_url(db: Session, website_url: str) -> Optional[Brand]:
        """
        Get brand by website URL
        
        Args:
            db: Database session
            website_url: Website URL
            
        Returns:
            Brand instance or None
        """
        return db.query(Brand).filter(Brand.website_url == website_url).first()
    
    @staticmethod
    def get_brand_by_id(db: Session, brand_id: int) -> Optional[Brand]:
        """
        Get brand by ID
        
        Args:
            db: Database session
            brand_id: Brand ID
            
        Returns:
            Brand instance or None
        """
        return db.query(Brand).filter(Brand.id == brand_id).first()
    
    @staticmethod
    def get_brands(db: Session, skip: int = 0, limit: int = 100) -> List[Brand]:
        """
        Get list of brands with pagination
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of Brand instances
        """
        return db.query(Brand).offset(skip).limit(limit).all()
    
    @staticmethod
    def delete_brand(db: Session, brand_id: int) -> bool:
        """
        Delete brand and all related data
        
        Args:
            db: Database session
            brand_id: Brand ID
            
        Returns:
            True if deleted, False if not found
        """
        brand = db.query(Brand).filter(Brand.id == brand_id).first()
        if not brand:
            return False
        
        db.delete(brand)
        db.commit()
        return True
    
    @staticmethod
    def create_or_update_brand(db: Session, brand_data: BrandContext) -> Brand:
        """
        Create or update brand and all related data
        
        Args:
            db: Database session
            brand_data: Brand context data
            
        Returns:
            Brand instance
        """
        try:
            # Check if brand exists
            existing_brand = BrandCRUD.get_brand_by_url(db, brand_data.website_url)
            
            if existing_brand:
                # Update existing brand
                brand = BrandCRUD._update_brand(db, existing_brand, brand_data)
                logger.info(f"Updated existing brand: {brand_data.website_url}")
            else:
                # Create new brand
                brand = BrandCRUD._create_brand(db, brand_data)
                logger.info(f"Created new brand: {brand_data.website_url}")
            
            db.commit()
            db.refresh(brand)
            return brand
            
        except Exception as e:
            logger.error(f"Error creating/updating brand {brand_data.website_url}: {e}")
            db.rollback()
            raise
    
    @staticmethod
    def _create_brand(db: Session, brand_data: BrandContext) -> Brand:
        """Create new brand with all related data"""
        # Create brand
        brand = Brand(
            website_url=brand_data.website_url,
            brand_name=brand_data.brand_name,
            favicon_url=brand_data.favicon_url,
            brand_description=brand_data.brand_description,
            about_us=brand_data.about_us,
            brand_story=brand_data.brand_story,
            shopify_theme=brand_data.shopify_theme,
            apps_detected=brand_data.apps_detected,
            analysis_date=brand_data.analysis_date.replace(tzinfo=None) if brand_data.analysis_date else datetime.now(),
            analysis_duration=brand_data.analysis_duration,
            pages_analyzed=brand_data.pages_analyzed,
            last_fetched=datetime.now()
        )
        
        db.add(brand)
        db.flush()  # To get the ID
        
        # Add related data
        BrandCRUD._add_related_data(db, brand, brand_data)
        
        return brand
    
    @staticmethod
    def _update_brand(db: Session, existing_brand: Brand, brand_data: BrandContext) -> Brand:
        """Update existing brand with new data"""
        # Update brand fields
        existing_brand.brand_name = brand_data.brand_name
        existing_brand.favicon_url = brand_data.favicon_url
        existing_brand.brand_description = brand_data.brand_description
        existing_brand.about_us = brand_data.about_us
        existing_brand.brand_story = brand_data.brand_story
        existing_brand.shopify_theme = brand_data.shopify_theme
        existing_brand.apps_detected = brand_data.apps_detected
        existing_brand.analysis_date = brand_data.analysis_date.replace(tzinfo=None) if brand_data.analysis_date else datetime.now()
        existing_brand.analysis_duration = brand_data.analysis_duration
        existing_brand.pages_analyzed = brand_data.pages_analyzed
        existing_brand.last_fetched = datetime.now()
        
        # Clear existing related data
        BrandCRUD._clear_related_data(db, existing_brand)
        
        # Add new related data
        BrandCRUD._add_related_data(db, existing_brand, brand_data)
        
        return existing_brand
    
    @staticmethod
    def _add_related_data(db: Session, brand: Brand, brand_data: BrandContext):
        """Add all related data to brand"""
        # Products - Fixed to work with Product objects from parser
        for product_data in brand_data.product_catalog:
            product = Product(  # Using Product model from database
                brand_id=brand.id,
                shopify_id=product_data.id if hasattr(product_data, 'id') else None,
                title=product_data.title if hasattr(product_data, 'title') else None,
                handle=product_data.handle if hasattr(product_data, 'handle') else None,
                vendor=product_data.vendor if hasattr(product_data, 'vendor') else None,
                product_type=product_data.product_type if hasattr(product_data, 'product_type') else None,
                price=product_data.price if hasattr(product_data, 'price') else None,
                compare_at_price=product_data.compare_at_price if hasattr(product_data, 'compare_at_price') else None,
                available=product_data.available if hasattr(product_data, 'available') else True,
                description=product_data.description if hasattr(product_data, 'description') else None,
                tags=product_data.tags if hasattr(product_data, 'tags') else [],
                images=product_data.images if hasattr(product_data, 'images') else [],
                variants=[v.dict() if hasattr(v, 'dict') else v for v in (product_data.variants if hasattr(product_data, 'variants') else [])],
                product_url=product_data.url if hasattr(product_data, 'url') else None,
                created_at=datetime.fromisoformat(product_data.created_at.replace('Z', '+00:00')) if (hasattr(product_data, 'created_at') and product_data.created_at) else None,
                updated_at=datetime.fromisoformat(product_data.updated_at.replace('Z', '+00:00')) if (hasattr(product_data, 'updated_at') and product_data.updated_at) else None,
                scraped_at=datetime.now()
            )
            db.add(product)
            logger.info(f"Added product: {product_data.title}")
        
        logger.info(f"Added {len(brand_data.product_catalog)} products to database")
        
        # Hero products
        for hero_data in brand_data.hero_products:
            hero_product = HeroProduct(
                brand_id=brand.id,
                title=hero_data.title,
                price=hero_data.price,
                image_url=hero_data.image_url,
                product_url=hero_data.product_url,
                description=hero_data.description
            )
            db.add(hero_product)
        
        # Policies
        for policy_data in brand_data.policies:
            policy = Policy(
                brand_id=brand.id,
                policy_type=policy_data.type.value,
                title=policy_data.title,
                content=policy_data.content,
                url=policy_data.url
            )
            db.add(policy)
        
        # FAQs
        for faq_data in brand_data.faqs:
            faq = FAQ(
                brand_id=brand.id,
                question=faq_data.question,
                answer=faq_data.answer,
                category=faq_data.category
            )
            db.add(faq)
        
        # Social handles
        for social_data in brand_data.social_handles:
            social = SocialHandle(
                brand_id=brand.id,
                platform=social_data.platform,
                username=social_data.username,
                url=social_data.url,
                followers_count=social_data.followers_count
            )
            db.add(social)
        
        # Important links
        for link_data in brand_data.important_links:
            link = ImportantLink(
                brand_id=brand.id,
                title=link_data.title,
                url=link_data.url,
                link_type=link_data.type
            )
            db.add(link)
        
        # Contact details
        if brand_data.contact_info:
            # Emails
            for email in brand_data.contact_info.emails:
                contact = ContactDetail(
                    brand_id=brand.id,
                    contact_type="email",
                    value=email
                )
                db.add(contact)
            
            # Phone numbers
            for phone in brand_data.contact_info.phone_numbers:
                contact = ContactDetail(
                    brand_id=brand.id,
                    contact_type="phone",
                    value=phone
                )
                db.add(contact)
            
            # Addresses
            for address in brand_data.contact_info.addresses:
                contact = ContactDetail(
                    brand_id=brand.id,
                    contact_type="address",
                    value=address
                )
                db.add(contact)
    
    @staticmethod
    def _clear_related_data(db: Session, brand: Brand):
        """Clear all related data for brand"""
        # Delete in reverse order of dependencies
        db.query(ContactDetail).filter(ContactDetail.brand_id == brand.id).delete()
        db.query(ImportantLink).filter(ImportantLink.brand_id == brand.id).delete()
        db.query(SocialHandle).filter(SocialHandle.brand_id == brand.id).delete()
        db.query(FAQ).filter(FAQ.brand_id == brand.id).delete()
        db.query(Policy).filter(Policy.brand_id == brand.id).delete()
        db.query(HeroProduct).filter(HeroProduct.brand_id == brand.id).delete()
        db.query(Product).filter(Product.brand_id == brand.id).delete()
    
    @staticmethod
    def get_brand_context(db: Session, website_url: str) -> Optional[BrandContext]:
        """
        Get complete brand context from database
        
        Args:
            db: Database session
            website_url: Website URL
            
        Returns:
            BrandContext instance or None
        """
        brand = BrandCRUD.get_brand_by_url(db, website_url)
        if not brand:
            return None
        
        try:
            # Get all related data separately to avoid lazy loading issues
            products = db.query(Product).filter(Product.brand_id == brand.id).all()
            hero_products = db.query(HeroProduct).filter(HeroProduct.brand_id == brand.id).all()
            policies = db.query(Policy).filter(Policy.brand_id == brand.id).all()
            faqs = db.query(FAQ).filter(FAQ.brand_id == brand.id).all()
            social_handles = db.query(SocialHandle).filter(SocialHandle.brand_id == brand.id).all()
            important_links = db.query(ImportantLink).filter(ImportantLink.brand_id == brand.id).all()
            
            # Build contact info
            contact_details = db.query(ContactDetail).filter(ContactDetail.brand_id == brand.id).all()
            contact_info = ContactInfo(
                emails=[cd.value for cd in contact_details if cd.contact_type == "email"],
                phone_numbers=[cd.value for cd in contact_details if cd.contact_type == "phone"],
                addresses=[cd.value for cd in contact_details if cd.contact_type == "address"]
            )
            
            # Build brand context
            products_list = [BrandCRUD._product_to_dict(p) for p in products]
            brand_context = BrandContext(
                brand_name=brand.brand_name,
                website_url=brand.website_url,
                favicon_url=brand.favicon_url,
                product_catalog=products_list,
                products=products_list,  # Backward compatibility
                hero_products=[BrandCRUD._hero_product_to_dict(hp) for hp in hero_products],
                product_count=len(products),
                policies=[BrandCRUD._policy_to_dict(p) for p in policies],
                faqs=[BrandCRUD._faq_to_dict(f) for f in faqs],
                social_handles=[BrandCRUD._social_to_dict(s) for s in social_handles],
                contact_info=contact_info,
                brand_description=brand.brand_description,
                about_us=brand.about_us,
                brand_story=brand.brand_story,
                important_links=[BrandCRUD._link_to_dict(l) for l in important_links],
                shopify_theme=brand.shopify_theme,
                apps_detected=brand.apps_detected or [],
                analysis_date=brand.analysis_date or datetime.now(),
                analysis_duration=brand.analysis_duration,
                pages_analyzed=brand.pages_analyzed or 0
            )
            
            return brand_context
            
        except Exception as e:
            logger.error(f"Error building brand context for {website_url}: {e}")
            return None
    
    @staticmethod
    def _product_to_dict(product: Product):
        """Convert Product model to dict"""
        from models.brand_data import Product as ProductModel, ProductVariant
        
        # Convert variants
        variants = []
        if product.variants:
            for variant_data in product.variants:
                if isinstance(variant_data, dict):
                    variants.append(ProductVariant(**variant_data))
        
        return ProductModel(
            id=product.shopify_id,
            title=product.title,
            handle=product.handle,
            vendor=product.vendor,
            product_type=product.product_type,
            price=product.price,
            compare_at_price=product.compare_at_price,
            available=product.available,
            tags=product.tags or [],
            images=product.images or [],
            variants=variants,
            description=product.description,
            url=product.product_url,
            created_at=product.created_at.isoformat() if product.created_at else None,
            updated_at=product.updated_at.isoformat() if product.updated_at else None
        )
    
    @staticmethod
    def _hero_product_to_dict(hero_product: HeroProduct):
        """Convert HeroProduct model to dict"""
        from models.brand_data import HeroProduct as HeroProductModel
        
        return HeroProductModel(
            title=hero_product.title,
            price=hero_product.price,
            image_url=hero_product.image_url,
            product_url=hero_product.product_url,
            description=hero_product.description
        )
    
    @staticmethod
    def _policy_to_dict(policy: Policy):
        """Convert Policy model to dict"""
        from models.brand_data import Policy as PolicyModel, PolicyType
        
        return PolicyModel(
            type=PolicyType(policy.policy_type),
            title=policy.title,
            content=policy.content,
            url=policy.url
        )
    
    @staticmethod
    def _faq_to_dict(faq: FAQ):
        """Convert FAQ model to dict"""
        from models.brand_data import FAQ as FAQModel
        
        return FAQModel(
            question=faq.question,
            answer=faq.answer,
            category=faq.category
        )
    
    @staticmethod
    def _social_to_dict(social: SocialHandle):
        """Convert SocialHandle model to dict"""
        from models.brand_data import SocialHandle as SocialHandleModel
        
        return SocialHandleModel(
            platform=social.platform,
            username=social.username,
            url=social.url,
            followers_count=social.followers_count
        )
    
    @staticmethod
    def _link_to_dict(link: ImportantLink):
        """Convert ImportantLink model to dict"""
        from models.brand_data import ImportantLink as ImportantLinkModel
        
        return ImportantLinkModel(
            title=link.title,
            url=link.url,
            type=link.link_type
        )
