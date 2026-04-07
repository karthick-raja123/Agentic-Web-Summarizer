"""
Scrape Agent - Fetches and cleans content from URLs.
Part of the LangGraph workflow.
"""

from typing import List, Optional
from services.scraping_service import ScrapingService
from utils.logging_config import get_logger

logger = get_logger(__name__)


class ScrapeAgent:
    """Agent responsible for scraping web content."""
    
    def __init__(self, max_content_per_url: int = 10000, max_total_content: int = 30000):
        """
        Initialize Scrape Agent.
        
        Args:
            max_content_per_url: Max characters to fetch from each URL
            max_total_content: Max total combined content
        """
        self.scraping_service = ScrapingService(max_content_length=max_content_per_url)
        self.max_total_content = max_total_content
        logger.info(
            f"Scrape Agent initialized (max per URL: {max_content_per_url}, "
            f"max total: {max_total_content})"
        )
    
    def execute(self, urls: List[str]) -> dict:
        """
        Scrape content from URLs.
        
        Args:
            urls: List of URLs to scrape
            
        Returns:
            Dictionary with scraped content
        """
        logger.info(f"ScrapeAgent.execute() called for {len(urls)} URLs")
        
        if not urls or len(urls) == 0:
            logger.warning("No URLs provided to ScrapeAgent")
            return {"content": "", "url_count": 0, "status": "failed"}
        
        try:
            # Fetch from all URLs
            contents = self.scraping_service.fetch_multiple(urls)
            
            if not contents:
                logger.warning("No content retrieved from any URLs")
                return {
                    "content": "",
                    "url_count": 0,
                    "status": "failed",
                    "error": "No content could be scraped"
                }
            
            # Combine content
            combined_content = self.scraping_service.combine_contents(
                contents,
                max_chars=self.max_total_content
            )
            
            logger.info(
                f"ScrapeAgent successfully scraped {len(contents)} URLs, "
                f"combined {len(combined_content)} characters"
            )
            
            return {
                "content": combined_content,
                "url_count": len(contents),
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"ScrapeAgent failed: {str(e)}")
            return {
                "content": "",
                "url_count": 0,
                "status": "failed",
                "error": str(e)
            }
    
    def execute_for_urls(self, urls: List[str]) -> dict:
        """
        Scrape content with detailed per-URL tracking.
        
        Args:
            urls: List of URLs
            
        Returns:
            Dictionary with per-URL results
        """
        logger.info(f"ScrapeAgent.execute_for_urls() called for {len(urls)} URLs")
        
        if not urls or len(urls) == 0:
            return {"url_contents": {}, "status": "failed"}
        
        try:
            contents = self.scraping_service.fetch_multiple(urls)
            
            logger.info(f"ScrapeAgent retrieved content from {len(contents)} URLs")
            
            return {
                "url_contents": contents,
                "status": "success" if contents else "failed"
            }
            
        except Exception as e:
            logger.error(f"ScrapeAgent URL tracking failed: {str(e)}")
            return {
                "url_contents": {},
                "status": "failed",
                "error": str(e)
            }
