"""
Search Agent - Performs web search using Serper API.
Part of the LangGraph workflow.
"""

from typing import List
from services.serper_service import SerperService
from utils.logging_config import get_logger

logger = get_logger(__name__)


class SearchAgent:
    """Agent responsible for searching the web."""
    
    def __init__(self, num_results: int = 5):
        """
        Initialize Search Agent.
        
        Args:
            num_results: Number of search results to retrieve
        """
        self.serper_service = SerperService()
        self.num_results = num_results
        logger.info(f"Search Agent initialized (requesting {num_results} results)")
    
    def execute(self, query: str) -> dict:
        """
        Execute search for a query.
        
        Args:
            query: Search query
            
        Returns:
            Dictionary with search results
        """
        logger.info(f"SearchAgent.execute() called for query: '{query}'")
        
        if not query or len(query.strip()) == 0:
            logger.warning("Empty query provided to SearchAgent")
            return {"urls": [], "query": query, "status": "failed"}
        
        try:
            urls = self.serper_service.search(query, num_results=self.num_results)
            
            logger.info(f"SearchAgent found {len(urls)} URLs")
            return {
                "urls": urls,
                "query": query,
                "status": "success"
            }
        except Exception as e:
            logger.error(f"SearchAgent failed: {str(e)}")
            return {
                "urls": [],
                "query": query,
                "status": "failed",
                "error": str(e)
            }
    
    def execute_with_metadata(self, query: str) -> dict:
        """
        Execute search with detailed metadata.
        
        Args:
            query: Search query
            
        Returns:
            Dictionary with search results and metadata
        """
        logger.info(f"SearchAgent.execute_with_metadata() called for query: '{query}'")
        
        if not query or len(query.strip()) == 0:
            logger.warning("Empty query provided to SearchAgent")
            return {"results": [], "query": query, "status": "failed"}
        
        try:
            results = self.serper_service.search_with_metadata(query, num_results=self.num_results)
            
            logger.info(f"SearchAgent found {len(results)} results with metadata")
            return {
                "results": results,
                "query": query,
                "status": "success"
            }
        except Exception as e:
            logger.error(f"SearchAgent metadata retrieval failed: {str(e)}")
            return {
                "results": [],
                "query": query,
                "status": "failed",
                "error": str(e)
            }
