"""
Configuration settings for the Shopify Store Insights Fetcher Application
"""
import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    
    # Database configuration
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "sqlite:///./shopify_insights.db"
    )
    
    # API configuration
    API_VERSION: str = "1.0.0"
    API_TITLE: str = "Shopify Store Insights Fetcher API"
    API_DESCRIPTION: str = "Extract structured data from Shopify stores"
    
    # OpenAI configuration (optional)
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    
    # Web scraping configuration
    USER_AGENT: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    REQUEST_TIMEOUT: int = 30
    MAX_RETRIES: int = 3
    RATE_LIMIT_DELAY: float = 1.0
    MAX_CONCURRENT_REQUESTS: int = 5
    
    # Application settings
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
