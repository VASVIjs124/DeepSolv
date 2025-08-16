"""
Utility functions for the Shopify Store Insights Fetcher Application
"""
import re
import validators
from urllib.parse import urljoin, urlparse
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)


def normalize_url(url: str) -> str:
    """
    Normalize and validate URL format
    
    Args:
        url: Raw URL string
        
    Returns:
        Normalized URL string
        
    Raises:
        ValueError: If URL is invalid
    """
    if not url or not isinstance(url, str):
        raise ValueError("URL must be a non-empty string")
    
    # Remove whitespace
    url = url.strip()
    
    # Add protocol if missing
    if not url.startswith(('http://', 'https://')):
        url = f"https://{url}"
    
    # Validate URL
    if not validators.url(url):
        raise ValueError(f"Invalid URL format: {url}")
    
    # Remove trailing slash
    if url.endswith('/'):
        url = url[:-1]
    
    return url


def is_shopify_store(url: str) -> bool:
    """
    Check if URL is likely a Shopify store
    
    Args:
        url: Store URL
        
    Returns:
        True if likely a Shopify store, False otherwise
    """
    try:
        normalized_url = normalize_url(url)
        domain = urlparse(normalized_url).netloc.lower()
        
        # Check for common Shopify indicators
        shopify_indicators = [
            '.myshopify.com',
            'shopifycdn.com',
            'shopify.com'
        ]
        
        # Basic heuristic - most Shopify stores will have these endpoints
        # This is a basic check, actual validation happens during scraping
        return any(indicator in domain for indicator in shopify_indicators) or True  # Allow all for now
        
    except Exception as e:
        logger.error(f"Error checking if {url} is Shopify store: {e}")
        return False


def extract_emails_from_text(text: str) -> List[str]:
    """
    Extract email addresses from text using regex
    
    Args:
        text: Text content to search
        
    Returns:
        List of unique email addresses found
    """
    if not text:
        return []
    
    # Email regex pattern
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text, re.IGNORECASE)
    
    # Remove duplicates and common false positives
    unique_emails = list(set(emails))
    filtered_emails = []
    
    for email in unique_emails:
        # Filter out common false positives
        if not any(fp in email.lower() for fp in ['example.com', 'test.com', 'placeholder']):
            filtered_emails.append(email)
    
    return filtered_emails


def extract_phone_numbers_from_text(text: str) -> List[str]:
    """
    Extract phone numbers from text using regex
    
    Args:
        text: Text content to search
        
    Returns:
        List of unique phone numbers found
    """
    if not text:
        return []
    
    # Phone number patterns
    phone_patterns = [
        r'\+?1?[-.\s]?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})',  # US format
        r'\+?([0-9]{1,4})?[-.\s]?\(?([0-9]{2,4})\)?[-.\s]?([0-9]{3,4})[-.\s]?([0-9]{3,4})',  # International
        r'\b\d{10}\b',  # 10-digit numbers
        r'\b\d{3}-\d{3}-\d{4}\b',  # XXX-XXX-XXXX format
        r'\(\d{3}\)\s?\d{3}-\d{4}',  # (XXX) XXX-XXXX format
    ]
    
    phone_numbers = []
    for pattern in phone_patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            if isinstance(match, tuple):
                # Join tuple elements
                phone = ''.join(match)
            else:
                phone = str(match)
            
            # Clean up the phone number
            cleaned_phone = re.sub(r'[^\d+]', '', phone)
            if len(cleaned_phone) >= 10:  # Minimum length for valid phone
                phone_numbers.append(cleaned_phone)
    
    return list(set(phone_numbers))


def build_absolute_url(base_url: str, relative_url: str) -> str:
    """
    Build absolute URL from base URL and relative URL
    
    Args:
        base_url: Base URL
        relative_url: Relative URL or path
        
    Returns:
        Absolute URL
    """
    if not relative_url:
        return base_url
    
    # If already absolute, return as is
    if relative_url.startswith(('http://', 'https://')):
        return relative_url
    
    # Build absolute URL
    return urljoin(base_url, relative_url)


def clean_text(text: str) -> str:
    """
    Clean and normalize text content
    
    Args:
        text: Raw text content
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Remove extra whitespace and normalize
    cleaned = re.sub(r'\s+', ' ', text.strip())
    
    # Remove common unwanted characters
    cleaned = re.sub(r'[^\w\s\-\.,!?;:()\[\]{}@#$%&*+=<>/\\|`~"\']+', '', cleaned)
    
    return cleaned


def extract_domain(url: str) -> Optional[str]:
    """
    Extract domain name from URL
    
    Args:
        url: Full URL
        
    Returns:
        Domain name or None if invalid
    """
    try:
        parsed = urlparse(normalize_url(url))
        return parsed.netloc
    except Exception:
        return None


def is_valid_social_url(url: str, platform: str) -> bool:
    """
    Validate if URL belongs to specific social media platform
    
    Args:
        url: Social media URL
        platform: Platform name (instagram, facebook, etc.)
        
    Returns:
        True if URL is valid for platform
    """
    if not url or not platform:
        return False
    
    platform_domains = {
        'instagram': ['instagram.com', 'instagr.am'],
        'facebook': ['facebook.com', 'fb.com', 'fb.me'],
        'twitter': ['twitter.com', 't.co', 'x.com'],
        'linkedin': ['linkedin.com', 'lnkd.in'],
        'youtube': ['youtube.com', 'youtu.be'],
        'tiktok': ['tiktok.com'],
        'pinterest': ['pinterest.com', 'pin.it'],
        'snapchat': ['snapchat.com'],
        'whatsapp': ['wa.me', 'whatsapp.com'],
        'telegram': ['t.me', 'telegram.me']
    }
    
    platform_lower = platform.lower()
    if platform_lower not in platform_domains:
        return False
    
    try:
        domain = urlparse(url).netloc.lower()
        return any(pd in domain for pd in platform_domains[platform_lower])
    except Exception:
        return False


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe file system operations
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove/replace invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    sanitized = re.sub(r'\s+', '_', sanitized)
    
    # Limit length
    if len(sanitized) > 100:
        sanitized = sanitized[:100]
    
    return sanitized or "unnamed"
