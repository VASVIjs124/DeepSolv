"""
Parser service for extracting structured data from HTML and JSON content
"""
import re
import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup, NavigableString, Tag
from datetime import datetime

from models.brand_data import (
    Product, HeroProduct, Policy, FAQ, SocialHandle, 
    ContactInfo, ImportantLink, PolicyType, ProductVariant
)
from utils.helpers import (
    extract_emails_from_text, extract_phone_numbers_from_text,
    build_absolute_url, clean_text, is_valid_social_url
)

logger = logging.getLogger(__name__)


class ShopifyParser:
    """
    Parser class for extracting structured data from Shopify stores
    """
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.domain = urlparse(base_url).netloc
    
    def parse_products_json(self, products_data: Dict[str, Any]) -> List[Product]:
        """
        Parse products from /products.json endpoint
        
        Args:
            products_data: JSON data from products endpoint
            
        Returns:
            List of Product objects
        """
        products = []
        
        try:
            if not products_data or 'products' not in products_data:
                logger.warning("No products data found")
                return products
            
            for product_data in products_data.get('products', []):
                try:
                    # Parse variants
                    variants = []
                    for variant_data in product_data.get('variants', []):
                        variant = ProductVariant(
                            id=variant_data.get('id'),
                            title=variant_data.get('title'),
                            option1=variant_data.get('option1'),
                            option2=variant_data.get('option2'),
                            option3=variant_data.get('option3'),
                            sku=variant_data.get('sku'),
                            requires_shipping=variant_data.get('requires_shipping'),
                            taxable=variant_data.get('taxable'),
                            featured_image=variant_data.get('featured_image'),
                            available=variant_data.get('available'),
                            price=variant_data.get('price'),
                            grams=variant_data.get('grams'),
                            compare_at_price=variant_data.get('compare_at_price'),
                            position=variant_data.get('position'),
                            product_id=variant_data.get('product_id'),
                            created_at=variant_data.get('created_at'),
                            updated_at=variant_data.get('updated_at')
                        )
                        variants.append(variant)
                    
                    # Extract images
                    images = []
                    for image_data in product_data.get('images', []):
                        if isinstance(image_data, dict):
                            image_url = image_data.get('src')
                        else:
                            image_url = str(image_data)
                        
                        if image_url:
                            images.append(build_absolute_url(self.base_url, image_url))
                    
                    # Get primary variant pricing
                    price = None
                    compare_at_price = None
                    if variants:
                        first_variant = variants[0]
                        try:
                            price = float(first_variant.price) if first_variant.price else None
                            compare_at_price = float(first_variant.compare_at_price) if first_variant.compare_at_price else None
                        except (ValueError, TypeError):
                            pass
                    
                    product = Product(
                        id=str(product_data.get('id', '')),
                        title=product_data.get('title'),
                        handle=product_data.get('handle'),
                        vendor=product_data.get('vendor'),
                        product_type=product_data.get('product_type'),
                        price=price,
                        compare_at_price=compare_at_price,
                        available=any(v.available for v in variants) if variants else True,
                        tags=product_data.get('tags', []),
                        images=images,
                        variants=variants,
                        description=clean_text(product_data.get('body_html', '')),
                        url=build_absolute_url(self.base_url, f"/products/{product_data.get('handle', '')}"),
                        created_at=product_data.get('created_at'),
                        updated_at=product_data.get('updated_at')
                    )
                    
                    products.append(product)
                    
                except Exception as e:
                    logger.error(f"Error parsing product {product_data.get('id', 'unknown')}: {e}")
                    continue
            
            logger.info(f"Parsed {len(products)} products")
            
        except Exception as e:
            logger.error(f"Error parsing products JSON: {e}")
        
        return products
    
    def parse_hero_products_from_html(self, html_content: str) -> List[HeroProduct]:
        """
        Parse hero products from homepage HTML
        
        Args:
            html_content: Homepage HTML content
            
        Returns:
            List of HeroProduct objects
        """
        hero_products = []
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Common selectors for hero products
            hero_selectors = [
                '[data-section-type="hero"]',
                '.hero-product',
                '.featured-product',
                '.hero-banner',
                '.slideshow-slide',
                '.banner-item',
                '.hero-section'
            ]
            
            for selector in hero_selectors:
                elements = soup.select(selector)
                
                for element in elements[:5]:  # Limit to first 5
                    try:
                        hero_product = self._extract_hero_product_from_element(element)
                        if hero_product and hero_product.title:
                            hero_products.append(hero_product)
                    except Exception as e:
                        logger.debug(f"Error extracting hero product from element: {e}")
                        continue
            
            # Remove duplicates based on title
            seen_titles = set()
            unique_heroes = []
            for hero in hero_products:
                if hero.title and hero.title not in seen_titles:
                    seen_titles.add(hero.title)
                    unique_heroes.append(hero)
            
            logger.info(f"Found {len(unique_heroes)} hero products")
            
        except Exception as e:
            logger.error(f"Error parsing hero products: {e}")
        
        return unique_heroes[:10]  # Return max 10 hero products
    
    def _extract_hero_product_from_element(self, element: Tag) -> Optional[HeroProduct]:
        """Extract hero product data from HTML element"""
        try:
            # Try to find product title
            title_selectors = ['h1', 'h2', 'h3', '.product-title', '.hero-title', '[data-product-title]']
            title = None
            
            for selector in title_selectors:
                title_elem = element.select_one(selector)
                if title_elem:
                    title = clean_text(title_elem.get_text())
                    break
            
            if not title:
                return None
            
            # Try to find price
            price_selectors = ['.price', '.product-price', '[data-price]', '.money']
            price = None
            
            for selector in price_selectors:
                price_elem = element.select_one(selector)
                if price_elem:
                    price_text = clean_text(price_elem.get_text())
                    # Extract numeric price
                    price_match = re.search(r'[\d,]+\.?\d*', price_text)
                    if price_match:
                        price = price_match.group(0)
                        break
            
            # Try to find image
            image_url = None
            img_elem = element.select_one('img')
            if img_elem:
                image_url = img_elem.get('src') or img_elem.get('data-src')
                if image_url:
                    image_url = build_absolute_url(self.base_url, image_url)
            
            # Try to find product URL
            product_url = None
            link_elem = element.select_one('a[href*="/products/"]')
            if link_elem:
                href = link_elem.get('href')
                if href:
                    product_url = build_absolute_url(self.base_url, href)
            
            return HeroProduct(
                title=title,
                price=price,
                image_url=image_url,
                product_url=product_url,
                description=None
            )
            
        except Exception as e:
            logger.debug(f"Error extracting hero product: {e}")
            return None
    
    def parse_policies_from_html(self, html_content: str, policy_type: str) -> Optional[Policy]:
        """
        Parse policy content from HTML
        
        Args:
            html_content: Policy page HTML
            policy_type: Type of policy (privacy, refund, etc.)
            
        Returns:
            Policy object or None
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract title
            title = None
            title_selectors = ['h1', 'title', '.page-title', '.policy-title']
            for selector in title_selectors:
                title_elem = soup.select_one(selector)
                if title_elem:
                    title = clean_text(title_elem.get_text())
                    break
            
            # Extract content
            content = None
            content_selectors = ['.page-content', '.policy-content', '.rte', 'main', 'article', '.content']
            
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    # Remove scripts and styles
                    for script in content_elem(["script", "style"]):
                        script.decompose()
                    
                    content = clean_text(content_elem.get_text())
                    break
            
            if not content:
                # Fallback: get all text content
                for script in soup(["script", "style", "header", "footer", "nav"]):
                    script.decompose()
                content = clean_text(soup.get_text())
            
            if content and len(content) > 100:  # Minimum content length
                return Policy(
                    type=PolicyType(policy_type),
                    title=title or f"{policy_type.title()} Policy",
                    content=content,
                    url=f"{self.base_url}/policies/{policy_type}"
                )
            
        except Exception as e:
            logger.error(f"Error parsing {policy_type} policy: {e}")
        
        return None
    
    def parse_faqs_from_html(self, html_content: str) -> List[FAQ]:
        """
        Parse FAQs from HTML content
        
        Args:
            html_content: HTML content containing FAQs
            
        Returns:
            List of FAQ objects
        """
        faqs = []
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Method 1: Look for FAQ-specific structures
            faq_containers = soup.select('.faq, .accordion, .qa-section, [data-faq]')
            
            for container in faq_containers:
                faqs.extend(self._extract_faqs_from_container(container))
            
            # Method 2: Look for alternating question/answer patterns
            if not faqs:
                faqs.extend(self._extract_faqs_from_headings(soup))
            
            # Method 3: Look for definition lists
            if not faqs:
                faqs.extend(self._extract_faqs_from_dl(soup))
            
            logger.info(f"Found {len(faqs)} FAQs")
            
        except Exception as e:
            logger.error(f"Error parsing FAQs: {e}")
        
        return faqs[:20]  # Limit to 20 FAQs
    
    def _extract_faqs_from_container(self, container: Tag) -> List[FAQ]:
        """Extract FAQs from a container element"""
        faqs = []
        
        # Look for question-answer pairs
        qa_pairs = container.select('.qa-pair, .faq-item, .accordion-item')
        
        for pair in qa_pairs:
            try:
                question_elem = pair.select_one('.question, .faq-question, .accordion-header, h3, h4, h5')
                answer_elem = pair.select_one('.answer, .faq-answer, .accordion-content, .faq-content')
                
                if question_elem and answer_elem:
                    question = clean_text(question_elem.get_text())
                    answer = clean_text(answer_elem.get_text())
                    
                    if question and answer and len(question) > 5 and len(answer) > 10:
                        faqs.append(FAQ(question=question, answer=answer))
            
            except Exception as e:
                logger.debug(f"Error extracting FAQ from pair: {e}")
                continue
        
        return faqs
    
    def _extract_faqs_from_headings(self, soup: BeautifulSoup) -> List[FAQ]:
        """Extract FAQs from heading and following content pattern"""
        faqs = []
        
        # Look for headings that look like questions
        headings = soup.find_all(['h3', 'h4', 'h5'], string=re.compile(r'\?|How|What|When|Where|Why|Can|Is|Do|Does'))
        
        for heading in headings:
            try:
                question = clean_text(heading.get_text())
                
                # Find next sibling with content
                answer_elem = heading.find_next_sibling(['p', 'div'])
                if answer_elem:
                    answer = clean_text(answer_elem.get_text())
                    
                    if question and answer and len(answer) > 10:
                        faqs.append(FAQ(question=question, answer=answer))
            
            except Exception as e:
                logger.debug(f"Error extracting FAQ from heading: {e}")
                continue
        
        return faqs
    
    def _extract_faqs_from_dl(self, soup: BeautifulSoup) -> List[FAQ]:
        """Extract FAQs from definition lists"""
        faqs = []
        
        dls = soup.find_all('dl')
        for dl in dls:
            dts = dl.find_all('dt')
            dds = dl.find_all('dd')
            
            # Match questions with answers
            for dt, dd in zip(dts, dds):
                try:
                    question = clean_text(dt.get_text())
                    answer = clean_text(dd.get_text())
                    
                    if question and answer and len(answer) > 10:
                        faqs.append(FAQ(question=question, answer=answer))
                
                except Exception as e:
                    logger.debug(f"Error extracting FAQ from dl: {e}")
                    continue
        
        return faqs
    
    def parse_social_handles_from_html(self, html_content: str) -> List[SocialHandle]:
        """
        Parse social media handles from HTML
        
        Args:
            html_content: HTML content
            
        Returns:
            List of SocialHandle objects
        """
        social_handles = []
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Platform patterns
            platforms = {
                'instagram': ['instagram.com', 'instagr.am'],
                'facebook': ['facebook.com', 'fb.com'],
                'twitter': ['twitter.com', 'x.com'],
                'linkedin': ['linkedin.com'],
                'youtube': ['youtube.com', 'youtu.be'],
                'tiktok': ['tiktok.com'],
                'pinterest': ['pinterest.com'],
                'snapchat': ['snapchat.com'],
                'whatsapp': ['wa.me', 'whatsapp.com'],
                'telegram': ['t.me', 'telegram.me']
            }
            
            # Find all links
            links = soup.find_all('a', href=True)
            
            seen_urls = set()
            for link in links:
                href = link.get('href', '').lower()
                
                if not href or href in seen_urls:
                    continue
                
                seen_urls.add(href)
                
                # Check each platform
                for platform, domains in platforms.items():
                    if any(domain in href for domain in domains):
                        # Build full URL
                        full_url = href if href.startswith('http') else build_absolute_url(self.base_url, href)
                        
                        # Extract username if possible
                        username = self._extract_social_username(full_url, platform)
                        
                        social_handle = SocialHandle(
                            platform=platform,
                            username=username,
                            url=full_url,
                            followers_count=None
                        )
                        
                        social_handles.append(social_handle)
                        break
            
            # Remove duplicates
            unique_handles = []
            seen_platforms = set()
            
            for handle in social_handles:
                key = f"{handle.platform}_{handle.url}"
                if key not in seen_platforms:
                    seen_platforms.add(key)
                    unique_handles.append(handle)
            
            logger.info(f"Found {len(unique_handles)} social handles")
            
        except Exception as e:
            logger.error(f"Error parsing social handles: {e}")
        
        return unique_handles
    
    def _extract_social_username(self, url: str, platform: str) -> Optional[str]:
        """Extract username from social media URL"""
        try:
            parsed = urlparse(url)
            path = parsed.path.strip('/')
            
            if platform == 'instagram':
                # Instagram: instagram.com/username
                if path and not path.startswith(('p/', 'reel/', 'tv/', 'explore/')):
                    return path.split('/')[0]
            
            elif platform == 'twitter':
                # Twitter: twitter.com/username
                if path and not path.startswith(('i/', 'search', 'hashtag')):
                    return path.split('/')[0]
            
            elif platform == 'facebook':
                # Facebook: facebook.com/username or facebook.com/pages/name/id
                if path and not path.startswith(('pages/', 'groups/', 'events/')):
                    return path.split('/')[0]
            
            elif platform == 'youtube':
                # YouTube: youtube.com/c/channel or youtube.com/user/username
                if '/c/' in path or '/user/' in path or '/channel/' in path:
                    return path.split('/')[-1]
                elif path and not path.startswith(('watch', 'playlist')):
                    return path.split('/')[0]
            
            elif platform == 'tiktok':
                # TikTok: tiktok.com/@username
                if path.startswith('@'):
                    return path
            
        except Exception as e:
            logger.debug(f"Error extracting username from {url}: {e}")
        
        return None
    
    def parse_contact_info_from_html(self, html_content: str) -> ContactInfo:
        """
        Parse contact information from HTML
        
        Args:
            html_content: HTML content
            
        Returns:
            ContactInfo object
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Get all text content
            all_text = soup.get_text()
            
            # Extract emails and phones
            emails = extract_emails_from_text(all_text)
            phones = extract_phone_numbers_from_text(all_text)
            
            # Look for addresses (basic pattern)
            addresses = self._extract_addresses_from_text(all_text)
            
            contact_info = ContactInfo(
                emails=emails[:5],  # Limit to 5 emails
                phone_numbers=phones[:3],  # Limit to 3 phones
                addresses=addresses[:2]  # Limit to 2 addresses
            )
            
            logger.info(f"Found {len(emails)} emails, {len(phones)} phones, {len(addresses)} addresses")
            
            return contact_info
            
        except Exception as e:
            logger.error(f"Error parsing contact info: {e}")
            return ContactInfo()
    
    def _extract_addresses_from_text(self, text: str) -> List[str]:
        """Extract physical addresses from text"""
        addresses = []
        
        try:
            # Simple address pattern (US format)
            address_pattern = r'\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln|Boulevard|Blvd|Way|Place|Pl)\s*,?\s*[A-Za-z\s]+,?\s*[A-Z]{2}\s+\d{5}'
            
            matches = re.findall(address_pattern, text, re.IGNORECASE)
            for match in matches:
                cleaned_address = clean_text(match)
                if len(cleaned_address) > 20:  # Minimum address length
                    addresses.append(cleaned_address)
            
        except Exception as e:
            logger.debug(f"Error extracting addresses: {e}")
        
        return list(set(addresses))  # Remove duplicates
    
    def parse_brand_info_from_html(self, html_content: str) -> Dict[str, Optional[str]]:
        """
        Parse brand information from HTML
        
        Args:
            html_content: HTML content
            
        Returns:
            Dictionary with brand information
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract brand name
            brand_name = None
            brand_selectors = ['title', 'h1', '.site-title', '.brand-name', '.logo-text']
            for selector in brand_selectors:
                elem = soup.select_one(selector)
                if elem:
                    text = clean_text(elem.get_text())
                    if text and len(text) < 100:  # Reasonable brand name length
                        brand_name = text
                        break
            
            # Extract description/about
            description = None
            desc_selectors = [
                '.about', '.brand-description', '.company-description',
                'meta[name="description"]', '.hero-text', '.intro-text'
            ]
            
            for selector in desc_selectors:
                if selector.startswith('meta'):
                    elem = soup.select_one(selector)
                    if elem:
                        description = elem.get('content')
                        break
                else:
                    elem = soup.select_one(selector)
                    if elem:
                        description = clean_text(elem.get_text())
                        break
            
            # Extract favicon
            favicon_url = None
            favicon_elem = soup.select_one('link[rel*="icon"]')
            if favicon_elem:
                favicon_href = favicon_elem.get('href')
                if favicon_href:
                    favicon_url = build_absolute_url(self.base_url, favicon_href)
            
            return {
                'brand_name': brand_name,
                'description': description,
                'favicon_url': favicon_url
            }
            
        except Exception as e:
            logger.error(f"Error parsing brand info: {e}")
            return {}
    
    def parse_important_links_from_html(self, html_content: str) -> List[ImportantLink]:
        """
        Parse important navigation links from HTML
        
        Args:
            html_content: HTML content
            
        Returns:
            List of ImportantLink objects
        """
        important_links = []
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Link categories and their keywords
            link_categories = {
                'contact': ['contact', 'contact us', 'get in touch', 'reach out'],
                'about': ['about', 'about us', 'our story', 'who we are'],
                'blog': ['blog', 'news', 'articles', 'stories'],
                'careers': ['careers', 'jobs', 'work with us', 'join us'],
                'press': ['press', 'media', 'press kit'],
                'order_tracking': ['track', 'order status', 'my orders', 'track order'],
                'size_guide': ['size guide', 'sizing', 'size chart'],
                'shipping': ['shipping', 'delivery', 'shipping info'],
                'returns': ['returns', 'return policy', 'exchanges'],
                'faq': ['faq', 'help', 'support', 'questions']
            }
            
            # Find all links
            links = soup.find_all('a', href=True)
            
            for link in links:
                href = link.get('href', '')
                text = clean_text(link.get_text()).lower()
                
                if not href or not text:
                    continue
                
                # Check if link matches any category
                for category, keywords in link_categories.items():
                    if any(keyword in text for keyword in keywords):
                        full_url = build_absolute_url(self.base_url, href)
                        
                        important_link = ImportantLink(
                            title=text.title(),
                            url=full_url,
                            type=category
                        )
                        
                        important_links.append(important_link)
                        break
            
            # Remove duplicates
            seen_urls = set()
            unique_links = []
            
            for link in important_links:
                if link.url not in seen_urls:
                    seen_urls.add(link.url)
                    unique_links.append(link)
            
            logger.info(f"Found {len(unique_links)} important links")
            
        except Exception as e:
            logger.error(f"Error parsing important links: {e}")
        
        return unique_links[:15]  # Limit to 15 links
