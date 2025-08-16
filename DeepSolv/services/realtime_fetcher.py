"""
Real-time Shopify Store Insights Fetcher
Fetches live data from any Shopify store and analyzes it comprehensively
"""
import asyncio
import aiohttp
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import json
import re
from datetime import datetime
from typing import Dict, List, Optional, Any
import time
from dataclasses import dataclass
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class StoreInsights:
    """Comprehensive store insights data structure"""
    basic_info: Dict[str, Any]
    products: List[Dict[str, Any]]
    collections: List[Dict[str, Any]]
    policies: Dict[str, str]
    social_media: Dict[str, str]
    seo_analysis: Dict[str, Any]
    performance_metrics: Dict[str, Any]
    shopify_analysis: Dict[str, Any]
    competitive_analysis: Dict[str, Any]

class ShopifyStoreFetcher:
    """Real-time Shopify store data fetcher and analyzer"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
    def is_shopify_store(self, url: str) -> bool:
        """Check if the given URL is a Shopify store"""
        try:
            # Clean URL
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            response = self.session.get(url, timeout=10)
            
            # Check for Shopify indicators
            shopify_indicators = [
                'Shopify.shop',
                'shopify-section',
                'cdn.shopify.com',
                'shopifycdn.com',
                '/cart/add',
                'Shopify.theme',
                'shopify_pay'
            ]
            
            content = response.text.lower()
            headers = str(response.headers).lower()
            
            return any(indicator.lower() in content or indicator.lower() in headers 
                      for indicator in shopify_indicators)
            
        except Exception as e:
            logger.error(f"Error checking if {url} is Shopify store: {e}")
            return False
    
    def fetch_store_basic_info(self, url: str) -> Dict[str, Any]:
        """Fetch basic store information"""
        try:
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
                
            response = self.session.get(url, timeout=15)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract basic information
            title = soup.find('title')
            title_text = title.get_text().strip() if title else "Unknown"
            
            # Extract meta description
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            description = meta_desc.get('content', '').strip() if meta_desc else ""
            
            # Extract favicon
            favicon = soup.find('link', rel='icon') or soup.find('link', rel='shortcut icon')
            favicon_url = urljoin(url, favicon.get('href')) if favicon else ""
            
            # Extract brand name from various sources
            brand_name = self._extract_brand_name(soup, url, title_text)
            
            # Check for Shopify theme
            theme_info = self._extract_shopify_theme(response.text)
            
            # Extract contact information
            contact_info = self._extract_contact_info(soup)
            
            return {
                'brand_name': brand_name,
                'website_url': url,
                'title': title_text,
                'description': description,
                'favicon_url': favicon_url,
                'shopify_theme': theme_info,
                'contact_info': contact_info,
                'last_fetched': datetime.now(),
                'is_shopify': self.is_shopify_store(url),
                'status_code': response.status_code,
                'page_size': len(response.content)
            }
            
        except Exception as e:
            logger.error(f"Error fetching basic info from {url}: {e}")
            return {'error': str(e), 'website_url': url}
    
    def fetch_products(self, url: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Fetch products from Shopify store using products.json endpoint"""
        try:
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            products_url = urljoin(url, '/products.json')
            response = self.session.get(products_url, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                products = data.get('products', [])[:limit]
                
                processed_products = []
                for product in products:
                    processed_product = {
                        'id': product.get('id'),
                        'title': product.get('title', ''),
                        'description': BeautifulSoup(product.get('body_html', ''), 'html.parser').get_text()[:500],
                        'vendor': product.get('vendor', ''),
                        'product_type': product.get('product_type', ''),
                        'created_at': product.get('created_at', ''),
                        'updated_at': product.get('updated_at', ''),
                        'published_at': product.get('published_at', ''),
                        'tags': product.get('tags', '').split(',') if product.get('tags') else [],
                        'status': product.get('status', ''),
                        'variants_count': len(product.get('variants', [])),
                        'images_count': len(product.get('images', [])),
                        'url': urljoin(url, f"/products/{product.get('handle', '')}")
                    }
                    
                    # Get price range from variants
                    variants = product.get('variants', [])
                    if variants:
                        prices = [float(v.get('price', 0)) for v in variants if v.get('price')]
                        if prices:
                            processed_product.update({
                                'price_min': min(prices),
                                'price_max': max(prices),
                                'avg_price': sum(prices) / len(prices)
                            })
                    
                    # Get first image
                    images = product.get('images', [])
                    if images:
                        processed_product['featured_image'] = images[0].get('src', '')
                    
                    processed_products.append(processed_product)
                
                return processed_products
            else:
                logger.warning(f"Could not fetch products from {products_url}, status: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error fetching products from {url}: {e}")
            return []
    
    def fetch_collections(self, url: str) -> List[Dict[str, Any]]:
        """Fetch collections from Shopify store"""
        try:
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            collections_url = urljoin(url, '/collections.json')
            response = self.session.get(collections_url, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                collections = data.get('collections', [])
                
                processed_collections = []
                for collection in collections:
                    processed_collection = {
                        'id': collection.get('id'),
                        'title': collection.get('title', ''),
                        'description': BeautifulSoup(collection.get('body_html', ''), 'html.parser').get_text()[:200],
                        'handle': collection.get('handle', ''),
                        'updated_at': collection.get('updated_at', ''),
                        'products_count': collection.get('products_count', 0),
                        'url': urljoin(url, f"/collections/{collection.get('handle', '')}")
                    }
                    processed_collections.append(processed_collection)
                
                return processed_collections
            else:
                return []
                
        except Exception as e:
            logger.error(f"Error fetching collections from {url}: {e}")
            return []
    
    def analyze_seo(self, url: str) -> Dict[str, Any]:
        """Analyze SEO aspects of the store"""
        try:
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
                
            response = self.session.get(url, timeout=15)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Title analysis
            title = soup.find('title')
            title_text = title.get_text().strip() if title else ""
            
            # Meta description
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            description = meta_desc.get('content', '').strip() if meta_desc else ""
            
            # Headings analysis
            h1_tags = soup.find_all('h1')
            h2_tags = soup.find_all('h2')
            h3_tags = soup.find_all('h3')
            
            # Images analysis
            images = soup.find_all('img')
            images_without_alt = [img for img in images if not img.get('alt')]
            
            # Links analysis
            internal_links = []
            external_links = []
            
            for link in soup.find_all('a', href=True):
                href = link['href']
                if href.startswith('http'):
                    if urlparse(url).netloc in href:
                        internal_links.append(href)
                    else:
                        external_links.append(href)
                elif href.startswith('/'):
                    internal_links.append(href)
            
            # Schema markup
            schema_scripts = soup.find_all('script', type='application/ld+json')
            schema_count = len(schema_scripts)
            
            return {
                'title': {
                    'text': title_text,
                    'length': len(title_text),
                    'optimal': 30 <= len(title_text) <= 60
                },
                'meta_description': {
                    'text': description,
                    'length': len(description),
                    'optimal': 120 <= len(description) <= 160
                },
                'headings': {
                    'h1_count': len(h1_tags),
                    'h2_count': len(h2_tags),
                    'h3_count': len(h3_tags),
                    'h1_texts': [h.get_text().strip() for h in h1_tags]
                },
                'images': {
                    'total_images': len(images),
                    'images_without_alt': len(images_without_alt),
                    'alt_optimization': (len(images) - len(images_without_alt)) / len(images) * 100 if images else 0
                },
                'links': {
                    'internal_links': len(internal_links),
                    'external_links': len(external_links),
                    'link_ratio': len(internal_links) / (len(internal_links) + len(external_links)) if (internal_links or external_links) else 0
                },
                'schema_markup': {
                    'count': schema_count,
                    'has_schema': schema_count > 0
                },
                'page_load_time': response.elapsed.total_seconds()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing SEO for {url}: {e}")
            return {'error': str(e)}
    
    def analyze_performance(self, url: str) -> Dict[str, Any]:
        """Analyze performance metrics"""
        try:
            start_time = time.time()
            
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            response = self.session.get(url, timeout=30)
            load_time = time.time() - start_time
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Count resources
            stylesheets = soup.find_all('link', rel='stylesheet')
            scripts = soup.find_all('script', src=True)
            images = soup.find_all('img', src=True)
            
            # Analyze content
            text_content = soup.get_text()
            content_length = len(response.content)
            text_length = len(text_content)
            
            return {
                'load_time': load_time,
                'response_size': content_length,
                'status_code': response.status_code,
                'text_content_length': text_length,
                'text_to_html_ratio': text_length / content_length * 100 if content_length > 0 else 0,
                'resources': {
                    'stylesheets': len(stylesheets),
                    'scripts': len(scripts),
                    'images': len(images)
                },
                'compression': {
                    'gzip_enabled': 'gzip' in response.headers.get('content-encoding', ''),
                    'content_type': response.headers.get('content-type', '')
                },
                'caching': {
                    'cache_control': response.headers.get('cache-control', ''),
                    'expires': response.headers.get('expires', ''),
                    'etag': response.headers.get('etag', '')
                }
            }
            
        except Exception as e:
            logger.error(f"Error analyzing performance for {url}: {e}")
            return {'error': str(e)}
    
    def extract_social_media(self, url: str) -> Dict[str, str]:
        """Extract social media links and information"""
        try:
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
                
            response = self.session.get(url, timeout=15)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            social_patterns = {
                'facebook': r'(?:https?://)?(?:www\.)?facebook\.com/([a-zA-Z0-9\.]+)',
                'instagram': r'(?:https?://)?(?:www\.)?instagram\.com/([a-zA-Z0-9\._]+)',
                'twitter': r'(?:https?://)?(?:www\.)?twitter\.com/([a-zA-Z0-9_]+)',
                'youtube': r'(?:https?://)?(?:www\.)?youtube\.com/(?:channel/|user/|c/)?([a-zA-Z0-9\-_]+)',
                'tiktok': r'(?:https?://)?(?:www\.)?tiktok\.com/@([a-zA-Z0-9\._]+)',
                'pinterest': r'(?:https?://)?(?:www\.)?pinterest\.com/([a-zA-Z0-9_]+)',
                'linkedin': r'(?:https?://)?(?:www\.)?linkedin\.com/(?:company/|in/)?([a-zA-Z0-9\-]+)'
            }
            
            social_media = {}
            page_text = response.text
            
            # Search in links
            for link in soup.find_all('a', href=True):
                href = link['href']
                for platform, pattern in social_patterns.items():
                    match = re.search(pattern, href)
                    if match and platform not in social_media:
                        social_media[platform] = {
                            'url': href,
                            'username': match.group(1),
                            'found_method': 'link_href'
                        }
            
            # Search in page content
            for platform, pattern in social_patterns.items():
                if platform not in social_media:
                    matches = re.findall(pattern, page_text)
                    if matches:
                        social_media[platform] = {
                            'url': f"https://{platform}.com/{matches[0]}",
                            'username': matches[0],
                            'found_method': 'page_content'
                        }
            
            return social_media
            
        except Exception as e:
            logger.error(f"Error extracting social media from {url}: {e}")
            return {}
    
    def analyze_shopify_specifics(self, url: str) -> Dict[str, Any]:
        """Analyze Shopify-specific features and setup"""
        try:
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
                
            response = self.session.get(url, timeout=15)
            content = response.text
            
            # Detect Shopify theme
            theme_info = self._extract_shopify_theme(content)
            
            # Detect apps
            apps_detected = self._detect_shopify_apps(content)
            
            # Check for Shopify Plus
            is_plus = any(indicator in content.lower() for indicator in [
                'shopify plus',
                'plus.shopify',
                'shopifyplus'
            ])
            
            # Payment methods
            payment_methods = self._extract_payment_methods(content)
            
            # Shipping information
            shipping_info = self._extract_shipping_info(content)
            
            # Cart functionality
            cart_features = self._analyze_cart_features(content)
            
            return {
                'theme': theme_info,
                'apps_detected': apps_detected,
                'is_shopify_plus': is_plus,
                'payment_methods': payment_methods,
                'shipping_info': shipping_info,
                'cart_features': cart_features,
                'api_endpoints_accessible': {
                    'products_json': self._test_endpoint(urljoin(url, '/products.json')),
                    'collections_json': self._test_endpoint(urljoin(url, '/collections.json')),
                    'cart_json': self._test_endpoint(urljoin(url, '/cart.json'))
                }
            }
            
        except Exception as e:
            logger.error(f"Error analyzing Shopify specifics for {url}: {e}")
            return {'error': str(e)}
    
    def fetch_comprehensive_insights(self, url: str) -> StoreInsights:
        """Fetch comprehensive insights for a Shopify store"""
        logger.info(f"🔍 Starting comprehensive analysis of: {url}")
        
        start_time = time.time()
        
        # Validate if it's a Shopify store
        if not self.is_shopify_store(url):
            logger.warning(f"⚠️  {url} does not appear to be a Shopify store")
        
        # Fetch all data in parallel where possible
        basic_info = self.fetch_store_basic_info(url)
        logger.info("✅ Basic info fetched")
        
        products = self.fetch_products(url, limit=100)
        logger.info(f"✅ {len(products)} products fetched")
        
        collections = self.fetch_collections(url)
        logger.info(f"✅ {len(collections)} collections fetched")
        
        seo_analysis = self.analyze_seo(url)
        logger.info("✅ SEO analysis completed")
        
        performance_metrics = self.analyze_performance(url)
        logger.info("✅ Performance analysis completed")
        
        social_media = self.extract_social_media(url)
        logger.info(f"✅ {len(social_media)} social media accounts found")
        
        shopify_analysis = self.analyze_shopify_specifics(url)
        logger.info("✅ Shopify-specific analysis completed")
        
        # Generate competitive analysis
        competitive_analysis = self._generate_competitive_analysis(basic_info, products, collections)
        logger.info("✅ Competitive analysis completed")
        
        # Policies extraction (attempt to find common policy pages)
        policies = self._extract_policies(url)
        logger.info("✅ Policies extracted")
        
        total_time = time.time() - start_time
        logger.info(f"🎉 Analysis completed in {total_time:.2f} seconds")
        
        return StoreInsights(
            basic_info=basic_info,
            products=products,
            collections=collections,
            policies=policies,
            social_media=social_media,
            seo_analysis=seo_analysis,
            performance_metrics=performance_metrics,
            shopify_analysis=shopify_analysis,
            competitive_analysis=competitive_analysis
        )
    
    # Helper methods
    def _extract_brand_name(self, soup: BeautifulSoup, url: str, title: str) -> str:
        """Extract brand name from various sources"""
        # Try different methods to extract brand name
        
        # Method 1: Look for schema.org Organization name
        schema_scripts = soup.find_all('script', type='application/ld+json')
        for script in schema_scripts:
            try:
                data = json.loads(script.string)
                if isinstance(data, dict) and data.get('@type') == 'Organization':
                    return data.get('name', '')
            except:
                continue
        
        # Method 2: Look for meta property og:site_name
        og_site_name = soup.find('meta', property='og:site_name')
        if og_site_name:
            return og_site_name.get('content', '')
        
        # Method 3: Extract from title (remove common suffixes)
        title_clean = title
        for suffix in [' - Official Store', ' | Online Store', ' Store', ' Shop']:
            title_clean = title_clean.replace(suffix, '')
        
        # Method 4: Use domain name as fallback
        if not title_clean or len(title_clean) < 3:
            domain = urlparse(url).netloc.replace('www.', '')
            title_clean = domain.split('.')[0].title()
        
        return title_clean.strip()
    
    def _extract_shopify_theme(self, content: str) -> Dict[str, str]:
        """Extract Shopify theme information"""
        theme_patterns = {
            'theme_name': r'Shopify\.theme\s*=\s*{[^}]*"name":\s*"([^"]+)"',
            'theme_id': r'Shopify\.theme\s*=\s*{[^}]*"id":\s*(\d+)',
            'theme_handle': r'Shopify\.theme\s*=\s*{[^}]*"handle":\s*"([^"]+)"'
        }
        
        theme_info = {}
        for key, pattern in theme_patterns.items():
            match = re.search(pattern, content)
            if match:
                theme_info[key] = match.group(1)
        
        return theme_info
    
    def _detect_shopify_apps(self, content: str) -> List[str]:
        """Detect Shopify apps being used"""
        app_patterns = [
            (r'klaviyo', 'Klaviyo Email Marketing'),
            (r'yotpo', 'Yotpo Reviews'),
            (r'judge\.me', 'Judge.me Product Reviews'),
            (r'gorgias', 'Gorgias Customer Support'),
            (r'privy', 'Privy Email Marketing'),
            (r'loyaltylion', 'LoyaltyLion Rewards'),
            (r'aftership', 'AfterShip Tracking'),
            (r'smile\.io', 'Smile.io Rewards'),
            (r'okendo', 'Okendo Reviews'),
            (r'recharge', 'ReCharge Subscriptions')
        ]
        
        detected_apps = []
        content_lower = content.lower()
        
        for pattern, app_name in app_patterns:
            if re.search(pattern, content_lower):
                detected_apps.append(app_name)
        
        return detected_apps
    
    def _extract_contact_info(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract contact information"""
        contact_info = {}
        
        # Email patterns
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, soup.get_text())
        if emails:
            contact_info['emails'] = list(set(emails))
        
        # Phone patterns
        phone_pattern = r'[\+]?[1-9]?[\d\s\-\(\)]{10,15}'
        phones = re.findall(phone_pattern, soup.get_text())
        if phones:
            contact_info['phones'] = list(set(phones))
        
        return contact_info
    
    def _extract_payment_methods(self, content: str) -> List[str]:
        """Extract payment methods"""
        payment_patterns = [
            (r'paypal', 'PayPal'),
            (r'stripe', 'Stripe'),
            (r'apple\s*pay', 'Apple Pay'),
            (r'google\s*pay', 'Google Pay'),
            (r'shop\s*pay', 'Shop Pay'),
            (r'klarna', 'Klarna'),
            (r'afterpay', 'Afterpay'),
            (r'amazon\s*pay', 'Amazon Pay')
        ]
        
        detected_methods = []
        content_lower = content.lower()
        
        for pattern, method_name in payment_patterns:
            if re.search(pattern, content_lower):
                detected_methods.append(method_name)
        
        return detected_methods
    
    def _extract_shipping_info(self, content: str) -> Dict[str, bool]:
        """Extract shipping information"""
        content_lower = content.lower()
        
        return {
            'free_shipping': any(phrase in content_lower for phrase in ['free shipping', 'free delivery']),
            'international_shipping': any(phrase in content_lower for phrase in ['international shipping', 'worldwide shipping', 'global shipping']),
            'express_shipping': any(phrase in content_lower for phrase in ['express shipping', 'overnight shipping', 'next day delivery'])
        }
    
    def _analyze_cart_features(self, content: str) -> Dict[str, bool]:
        """Analyze cart functionality features"""
        content_lower = content.lower()
        
        return {
            'ajax_cart': 'ajax' in content_lower and 'cart' in content_lower,
            'mini_cart': 'mini-cart' in content_lower or 'minicart' in content_lower,
            'cart_drawer': 'cart-drawer' in content_lower or 'drawer-cart' in content_lower,
            'quick_buy': 'quick buy' in content_lower or 'quick-buy' in content_lower
        }
    
    def _test_endpoint(self, url: str) -> bool:
        """Test if an endpoint is accessible"""
        try:
            response = self.session.get(url, timeout=10)
            return response.status_code == 200
        except:
            return False
    
    def _extract_policies(self, url: str) -> Dict[str, str]:
        """Extract store policies"""
        policies = {}
        policy_pages = [
            ('privacy', '/pages/privacy-policy'),
            ('terms', '/pages/terms-of-service'),
            ('shipping', '/pages/shipping-policy'),
            ('returns', '/pages/return-policy'),
            ('refunds', '/pages/refund-policy')
        ]
        
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        for policy_name, policy_path in policy_pages:
            try:
                policy_url = urljoin(url, policy_path)
                response = self.session.get(policy_url, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    # Remove script and style elements
                    for script in soup(["script", "style"]):
                        script.decompose()
                    text = soup.get_text()
                    # Clean up text
                    lines = (line.strip() for line in text.splitlines())
                    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                    text = ' '.join(chunk for chunk in chunks if chunk)
                    if len(text) > 100:  # Only store if substantial content
                        policies[policy_name] = text[:1000]  # Limit length
            except:
                continue
        
        return policies
    
    def _generate_competitive_analysis(self, basic_info: Dict, products: List, collections: List) -> Dict[str, Any]:
        """Generate competitive analysis insights"""
        
        if not products:
            return {'error': 'No products found for analysis'}
        
        # Price analysis
        prices = []
        for product in products:
            if 'price_min' in product and product['price_min'] > 0:
                prices.append(product['price_min'])
            if 'price_max' in product and product['price_max'] > 0:
                prices.append(product['price_max'])
        
        price_analysis = {}
        if prices:
            price_analysis = {
                'avg_price': sum(prices) / len(prices),
                'min_price': min(prices),
                'max_price': max(prices),
                'price_range': max(prices) - min(prices),
                'total_products_with_pricing': len([p for p in products if 'price_min' in p])
            }
        
        # Category analysis
        categories = {}
        for product in products:
            category = product.get('product_type', 'Uncategorized')
            categories[category] = categories.get(category, 0) + 1
        
        # Vendor analysis
        vendors = {}
        for product in products:
            vendor = product.get('vendor', 'Unknown')
            vendors[vendor] = vendors.get(vendor, 0) + 1
        
        return {
            'price_analysis': price_analysis,
            'category_distribution': dict(sorted(categories.items(), key=lambda x: x[1], reverse=True)),
            'vendor_distribution': dict(sorted(vendors.items(), key=lambda x: x[1], reverse=True)),
            'product_metrics': {
                'total_products': len(products),
                'total_collections': len(collections),
                'avg_products_per_collection': len(products) / len(collections) if collections else 0,
                'products_with_images': len([p for p in products if 'featured_image' in p and p['featured_image']])
            },
            'content_analysis': {
                'avg_title_length': sum(len(p.get('title', '')) for p in products) / len(products) if products else 0,
                'products_with_descriptions': len([p for p in products if p.get('description', '').strip()]),
                'products_with_tags': len([p for p in products if p.get('tags') and len(p['tags']) > 0])
            }
        }

# Usage example
if __name__ == "__main__":
    fetcher = ShopifyStoreFetcher()
    
    # Example usage
    store_url = "allbirds.com"
    
    print(f"🚀 Starting analysis of {store_url}")
    insights = fetcher.fetch_comprehensive_insights(store_url)
    
    print("\n📊 ANALYSIS RESULTS:")
    print(f"Brand: {insights.basic_info.get('brand_name', 'Unknown')}")
    print(f"Products found: {len(insights.products)}")
    print(f"Collections found: {len(insights.collections)}")
    print(f"Social media accounts: {len(insights.social_media)}")
    print(f"SEO score: {insights.seo_analysis.get('title', {}).get('optimal', False)}")
    print(f"Load time: {insights.performance_metrics.get('load_time', 0):.2f}s")
