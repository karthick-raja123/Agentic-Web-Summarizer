"""
Scraping Service - Web scraping with retry, timeout, and content cleaning.
"""

import requests
from typing import List, Optional
from utils.logging_config import get_logger
from utils.retry import retry
from utils.cleaning import clean_content

logger = get_logger(__name__)

# Default request headers
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}


class ScrapingService:
    """Service for web scraping with robust error handling."""
    
    def __init__(
        self,
        timeout: int = 10,
        max_content_length: int = 50000,
        default_headers: Optional[dict] = None
    ):
        """
        Initialize Scraping Service.
        
        Args:
            timeout: Request timeout in seconds
            max_content_length: Maximum content to fetch per URL
            default_headers: Custom request headers
        """
        self.timeout = timeout
        self.max_content_length = max_content_length
        self.headers = default_headers or DEFAULT_HEADERS
        logger.info(f"Scraping Service initialized with timeout: {timeout}s")
    
    @retry(max_attempts=3, delay=1.0, backoff=1.5, exceptions=(requests.RequestException,))
    def fetch_content(self, url: str) -> Optional[str]:
        """
        Fetch and clean content from a single URL.
        
        Args:
            url: URL to scrape
            
        Returns:
            Cleaned content or None if failed
        """
        try:
            logger.info(f"Fetching content from: {url}")
            response = requests.get(
                url,
                headers=self.headers,
                timeout=self.timeout,
                allow_redirects=True
            )
            response.raise_for_status()
            
            # Limit content size
            if len(response.text) > self.max_content_length:
                logger.warning(
                    f"Content exceeds max length. Truncating from {len(response.text)} to {self.max_content_length}"
                )
            
            html_content = response.text[:self.max_content_length]
            
            # Clean and process
            cleaned_content = clean_content(html_content)
            
            logger.info(f"Successfully fetched and cleaned {len(cleaned_content)} characters from {url}")
            return cleaned_content
            
        except requests.RequestException as e:
            logger.error(f"Failed to fetch {url}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error scraping {url}: {str(e)}")
            return None
    
    def fetch_multiple(self, urls: List[str]) -> dict:
        """
        Fetch content from multiple URLs.
        
        Args:
            urls: List of URLs to scrape
            
        Returns:
            Dictionary with URL -> content mapping
        """
        results = {}
        successful = 0
        failed = 0
        
        logger.info(f"Starting to fetch {len(urls)} URLs")
        
        for url in urls:
            content = self.fetch_content(url)
            if content:
                results[url] = content
                successful += 1
            else:
                failed += 1
        
        logger.info(f"Scraping complete: {successful} successful, {failed} failed")
        return results
    
    def combine_contents(self, contents: dict, max_chars: int = 20000) -> str:
        """
        Combine multiple content pieces with length limit.
        
        Args:
            contents: Dictionary of URL -> content
            max_chars: Maximum total characters
            
        Returns:
            Combined content string
        """
        combined = ""
        
        for url, content in contents.items():
            if len(combined) >= max_chars:
                logger.info(f"Reached maximum combined content length ({max_chars} chars)")
                break
            
            combined += f"\n[From: {url}]\n{content}\n"
        
        if len(combined) > max_chars:
            combined = combined[:max_chars]
            logger.warning(f"Combined content truncated to {max_chars} characters")
        
        return combined
