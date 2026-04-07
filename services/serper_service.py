"""
Serper Service - Google search via Serper API with retry and rate limiting.
"""

import os
import requests
import json
from typing import List, Optional
from utils.logging_config import get_logger
from utils.retry import retry

logger = get_logger(__name__)

SERPER_API_URL = "https://google.serper.dev/search"


class SerperService:
    """Service for web search using Serper API."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Serper Service.
        
        Args:
            api_key: Serper API key (uses SERPER_API_KEY env var if not provided)
        """
        self.api_key = api_key or os.getenv("SERPER_API_KEY")
        if not self.api_key:
            raise ValueError("SERPER_API_KEY not found in environment variables")
        
        self.headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }
        logger.info("Serper Service initialized")
    
    @retry(max_attempts=3, delay=2.0, backoff=1.5, exceptions=(requests.RequestException,))
    def search(self, query: str, num_results: int = 10) -> List[str]:
        """
        Perform web search and return URLs.
        
        Args:
            query: Search query
            num_results: Number of results to return
            
        Returns:
            List of URLs
        """
        if not query or len(query.strip()) == 0:
            logger.error("Empty search query provided")
            return []
        
        try:
            logger.info(f"Searching for: '{query}' (requesting {num_results} results)")
            
            payload = {
                "q": query,
                "num": num_results
            }
            
            response = requests.post(
                SERPER_API_URL,
                headers=self.headers,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            
            results = response.json()
            
            # Extract URLs from organic results
            urls = []
            if "organic" in results:
                urls = [
                    result["link"]
                    for result in results["organic"]
                    if "link" in result
                ][:num_results]
            
            logger.info(f"Search returned {len(urls)} URLs")
            for i, url in enumerate(urls, 1):
                logger.debug(f"  {i}. {url}")
            
            return urls
            
        except requests.RequestException as e:
            logger.error(f"Serper API request failed: {str(e)}")
            raise
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse Serper response: {str(e)}")
            raise
    
    def search_with_metadata(self, query: str, num_results: int = 5) -> List[dict]:
        """
        Perform search and return metadata (title, snippet, URL).
        
        Args:
            query: Search query
            num_results: Number of results
            
        Returns:
            List of result dictionaries with title, snippet, link
        """
        if not query or len(query.strip()) == 0:
            logger.error("Empty search query provided")
            return []
        
        try:
            logger.info(f"Searching with metadata for: '{query}'")
            
            payload = {
                "q": query,
                "num": num_results
            }
            
            response = requests.post(
                SERPER_API_URL,
                headers=self.headers,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            
            results = response.json()
            
            # Extract results with metadata
            search_results = []
            if "organic" in results:
                for result in results["organic"][:num_results]:
                    search_results.append({
                        "title": result.get("title", ""),
                        "snippet": result.get("snippet", ""),
                        "link": result.get("link", ""),
                        "position": result.get("position", 0)
                    })
            
            logger.info(f"Retrieved {len(search_results)} results with metadata")
            return search_results
            
        except Exception as e:
            logger.error(f"Failed to retrieve search metadata: {str(e)}")
            raise
