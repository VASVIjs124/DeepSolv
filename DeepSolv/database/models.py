"""
SQLAlchemy ORM models for database schema
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Brand(Base):
    """Main brand table"""
    __tablename__ = "brands"
    
    id = Column(Integer, primary_key=True, index=True)
    website_url = Column(String(500), unique=True, index=True, nullable=False)
    brand_name = Column(String(255))
    favicon_url = Column(String(500))
    
    # Brand content
    brand_description = Column(Text)
    about_us = Column(Text)
    brand_story = Column(Text)
    
    # Technical metadata
    shopify_theme = Column(String(255))
    apps_detected = Column(JSON)
    
    # Analysis metadata
    analysis_date = Column(DateTime, default=datetime.utcnow)
    analysis_duration = Column(Float)
    pages_analyzed = Column(Integer, default=0)
    last_fetched = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    products = relationship("Product", back_populates="brand", cascade="all, delete-orphan")
    hero_products = relationship("HeroProduct", back_populates="brand", cascade="all, delete-orphan")
    policies = relationship("Policy", back_populates="brand", cascade="all, delete-orphan")
    faqs = relationship("FAQ", back_populates="brand", cascade="all, delete-orphan")
    social_handles = relationship("SocialHandle", back_populates="brand", cascade="all, delete-orphan")
    important_links = relationship("ImportantLink", back_populates="brand", cascade="all, delete-orphan")
    contact_details = relationship("ContactDetail", back_populates="brand", cascade="all, delete-orphan")


class Product(Base):
    """Product table"""
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False)
    
    # Product identifiers
    shopify_id = Column(String(50))
    title = Column(String(500))
    handle = Column(String(255))
    vendor = Column(String(255))
    product_type = Column(String(255))
    
    # Pricing
    price = Column(Float)
    compare_at_price = Column(Float)
    currency = Column(String(10), default="USD")
    
    # Availability and status
    available = Column(Boolean, default=True)
    
    # Content
    description = Column(Text)
    tags = Column(JSON)  # Store as JSON array
    images = Column(JSON)  # Store as JSON array
    variants = Column(JSON)  # Store variants as JSON
    
    # URLs
    product_url = Column(String(500))
    
    # Timestamps
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    scraped_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    brand = relationship("Brand", back_populates="products")


class HeroProduct(Base):
    """Hero products table"""
    __tablename__ = "hero_products"
    
    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False)
    
    title = Column(String(500))
    price = Column(String(100))
    image_url = Column(String(500))
    product_url = Column(String(500))
    description = Column(Text)
    position = Column(Integer)  # Order on homepage
    
    scraped_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    brand = relationship("Brand", back_populates="hero_products")


class Policy(Base):
    """Policies table"""
    __tablename__ = "policies"
    
    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False)
    
    policy_type = Column(String(50), nullable=False)  # privacy, refund, return, terms, shipping
    title = Column(String(500))
    content = Column(Text)
    url = Column(String(500))
    
    scraped_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    brand = relationship("Brand", back_populates="policies")


class FAQ(Base):
    """FAQs table"""
    __tablename__ = "faqs"
    
    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False)
    
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    category = Column(String(255))
    position = Column(Integer)  # Order in FAQ section
    
    scraped_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    brand = relationship("Brand", back_populates="faqs")


class SocialHandle(Base):
    """Social media handles table"""
    __tablename__ = "social_handles"
    
    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False)
    
    platform = Column(String(50), nullable=False)
    username = Column(String(255))
    url = Column(String(500), nullable=False)
    followers_count = Column(Integer)
    
    scraped_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    brand = relationship("Brand", back_populates="social_handles")


class ImportantLink(Base):
    """Important links table"""
    __tablename__ = "important_links"
    
    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False)
    
    title = Column(String(255), nullable=False)
    url = Column(String(500), nullable=False)
    link_type = Column(String(50))  # contact, about, blog, etc.
    
    scraped_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    brand = relationship("Brand", back_populates="important_links")


class ContactDetail(Base):
    """Contact details table"""
    __tablename__ = "contact_details"
    
    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False)
    
    contact_type = Column(String(50), nullable=False)  # email, phone, address
    value = Column(String(500), nullable=False)
    label = Column(String(255))  # Optional label like "Support", "Sales"
    
    scraped_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    brand = relationship("Brand", back_populates="contact_details")
