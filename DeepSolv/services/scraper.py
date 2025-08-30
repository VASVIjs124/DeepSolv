"""
Web scraper service for fetching raw content from websites
"""
import aiohttp
import asyncio
import logging
from typing import Optional, Dict, Any, List
from urllib.parse import urljoin
import time
from aiohttp import ClientTimeout, ClientError

from config import settings
from utils.helpers import normalize_url

logger = logging.getLogger(__name__)


class WebScraper:
    """
    Web scraper class for fetching HTML content and JSON data
    """
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.timeout = ClientTimeout(total=settings.REQUEST_TIMEOUT)
        self.headers = {
            'User-Agent': settings.USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=self.timeout,
            headers=self.headers,
            connector=aiohttp.TCPConnector(limit=10)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def fetch_html(self, url: str, retries: int = None) -> Optional[str]:
        """
        Fetch HTML content from URL
        
        Args:
            url: URL to fetch
            retries: Number of retry attempts
            
        Returns:
            HTML content or None if failed
        """
        if retries is None:
            retries = settings.MAX_RETRIES
        
        normalized_url = normalize_url(url)
        
        for attempt in range(retries + 1):
            try:
                if not self.session:
                    raise RuntimeError("WebScraper session not initialized")
                
                logger.debug(f"Fetching HTML from {normalized_url} (attempt {attempt + 1})")
                
                async with self.session.get(normalized_url) as response:
                    # Check if response is successful
                    if response.status == 200:
                        content = await response.text()
                        logger.debug(f"Successfully fetched HTML from {normalized_url}")
                        return content
                    else:
                        logger.warning(f"HTTP {response.status} for {normalized_url}")
                        
            except ClientError as e:
                logger.warning(f"Network error fetching {normalized_url}: {e}")
            except asyncio.TimeoutError:
                logger.warning(f"Timeout fetching {normalized_url}")
            except Exception as e:
                logger.error(f"Unexpected error fetching {normalized_url}: {e}")
            
            # Wait before retry (except on last attempt)
            if attempt < retries:
                await asyncio.sleep(settings.RATE_LIMIT_DELAY * (attempt + 1))
        
        logger.error(f"Failed to fetch HTML from {normalized_url} after {retries + 1} attempts")
        return None
    
    async def fetch_json(self, url: str, retries: int = None) -> Optional[Dict[str, Any]]:
        """
        Fetch JSON data from URL
        
        Args:
            url: URL to fetch
            retries: Number of retry attempts
            
        Returns:
            JSON data as dict or None if failed
        """
        if retries is None:
            retries = settings.MAX_RETRIES
        
        normalized_url = normalize_url(url)
        
        for attempt in range(retries + 1):
            try:
                if not self.session:
                    raise RuntimeError("WebScraper session not initialized")
                
                logger.debug(f"Fetching JSON from {normalized_url} (attempt {attempt + 1})")
                
                async with self.session.get(normalized_url) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.debug(f"Successfully fetched JSON from {normalized_url}")
                        return data
                    else:
                        logger.warning(f"HTTP {response.status} for {normalized_url}")
                        
            except ClientError as e:
                logger.warning(f"Network error fetching {normalized_url}: {e}")
            except asyncio.TimeoutError:
                logger.warning(f"Timeout fetching {normalized_url}")
            except Exception as e:
                logger.error(f"Unexpected error fetching JSON from {normalized_url}: {e}")
            
            # Wait before retry (except on last attempt)
            if attempt < retries:
                await asyncio.sleep(settings.RATE_LIMIT_DELAY * (attempt + 1))
        
        logger.error(f"Failed to fetch JSON from {normalized_url} after {retries + 1} attempts")
        return None
    
    async def fetch_multiple_pages(self, urls: List[str]) -> Dict[str, Any]:
        """
        Fetch multiple pages concurrently
        
        Args:
            urls: List of URLs to fetch
            
        Returns:
            Dictionary mapping URLs to their content (HTML or JSON)
        """
        if not urls:
            return {}
        
        logger.info(f"Fetching {len(urls)} pages concurrently")
        
        # Create tasks for concurrent execution
        tasks = []
        for url in urls:
            if url.endswith('.json'):
                tasks.append(self._fetch_json_with_url(url))
            else:
                tasks.append(self._fetch_html_with_url(url))
        
        # Execute all tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        scraped_data = {}
        for i, result in enumerate(results):
            url = urls[i]
            if isinstance(result, Exception):
                logger.error(f"Error fetching {url}: {result}")
                scraped_data[url] = None
            else:
                scraped_data[url] = result
        
        successful_fetches = sum(1 for v in scraped_data.values() if v is not None)
        logger.info(f"Successfully fetched {successful_fetches}/{len(urls)} pages")
        
        return scraped_data
    
    async def _fetch_html_with_url(self, url: str) -> Optional[Dict[str, Any]]:
        """Helper method to fetch HTML and return with metadata"""
        html_content = await self.fetch_html(url)
        if html_content:
            return {
                'url': url,
                'content': html_content,
                'type': 'html'
            }
        return None
    
    async def _fetch_json_with_url(self, url: str) -> Optional[Dict[str, Any]]:
        """Helper method to fetch JSON and return with metadata"""
        json_data = await self.fetch_json(url)
        if json_data:
            return {
                'url': url,
                'json': json_data,
                'type': 'json'
            }
        return None
    
    async def check_robots_txt(self, base_url: str) -> Optional[str]:
        """
        Check robots.txt for crawling permissions
        
        Args:
            base_url: Base URL of the site
            
        Returns:
            robots.txt content or None
        """
        try:
            robots_url = urljoin(base_url, '/robots.txt')
            content = await self.fetch_html(robots_url, retries=1)
            return content
        except Exception as e:
            logger.debug(f"Could not fetch robots.txt from {base_url}: {e}")
            return None
    
    async def get_page_metadata(self, url: str) -> Dict[str, Any]:
        """
        Get basic page metadata (title, description, etc.)
        
        Args:
            url: Page URL
            
        Returns:
            Dictionary with page metadata
        """
        try:
            if not self.session:
                raise RuntimeError("WebScraper session not initialized")
            
            async with self.session.head(url) as response:
                metadata = {
                    'status_code': response.status,
                    'content_type': response.headers.get('content-type', ''),
                    'content_length': response.headers.get('content-length'),
                    'last_modified': response.headers.get('last-modified'),
                    'server': response.headers.get('server', ''),
                    'url': str(response.url)
                }
                return metadata
                
        except Exception as e:
            logger.error(f"Error getting metadata for {url}: {e}")
            return {'error': str(e)}


# Helper functions for synchronous usage
async def fetch_page_content(url: str) -> Optional[str]:
    """
    Fetch single page content (async helper)
    
    Args:
        url: URL to fetch
        
    Returns:
        HTML content or None
    """
    async with WebScraper() as scraper:
        return await scraper.fetch_html(url)


async def fetch_shopify_data(base_url: str) -> Dict[str, Any]:
    """
    Fetch common Shopify data endpoints
    
    Args:
        base_url: Base URL of Shopify store
        
    Returns:
        Dictionary with various data endpoints
    """
    async with WebScraper() as scraper:
        # Common Shopify endpoints
        endpoints = {
            'products': '/products.json',
            'collections': '/collections.json',
            'shop': '/shop.json',
            'policies': '/policies.json'
        }
        
        results = {}
        for name, path in endpoints.items():
            try:
                url = urljoin(base_url, path)
                data = await scraper.fetch_json(url)
                results[name] = data
                # Rate limiting
                await asyncio.sleep(settings.RATE_LIMIT_DELAY)
            except Exception as e:
                logger.error(f"Error fetching {name} from {base_url}: {e}")
                results[name] = None
        
        return results


def run_async_scraper(coro):
    """
    Run async scraper function in sync context
    
    Args:
        coro: Coroutine to run
        
    Returns:
        Result of coroutine
    """
    try:
        # Try to get existing event loop
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If loop is running, create new thread
            import concurrent.futures
            import threading
            
            def run_in_thread():
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                try:
                    return new_loop.run_until_complete(coro)
                finally:
                    new_loop.close()
            
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(run_in_thread)
                return future.result()
        else:
            # Use existing loop
            return loop.run_until_complete(coro)
    except RuntimeError:
        # No event loop, create new one
        return asyncio.run(coro)
