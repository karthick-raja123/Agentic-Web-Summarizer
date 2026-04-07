"""
Enhanced Scraper with Fallback - Scrapes URLs with automatic fallback to alternatives.
Reduces failure rate and improves content availability.
"""

from typing import List, Dict, Optional
from services.scraping_service import ScrapingService
from utils.logging_config import get_logger

logger = get_logger(__name__)


class EnhancedScraper:
    """Scraper with intelligent fallback strategy."""
    
    def __init__(self, timeout: int = 10, max_retries: int = 3):
        """
        Initialize enhanced scraper.
        
        Args:
            timeout: Request timeout in seconds
            max_retries: Max retry attempts per URL
        """
        self.scraping_service = ScrapingService()
        self.timeout = timeout
        self.max_retries = max_retries
        self.failed_urls = set()
        
        logger.info(f"EnhancedScraper initialized - timeout: {timeout}s, retries: {max_retries}")
    
    def scrape_with_fallback(self, urls: List[str], fallback_strategy: str = "alternative") -> Dict:
        """
        Scrape URLs with intelligent fallback handling.
        
        Args:
            urls: List of URLs to scrape
            fallback_strategy: "alternative" (try next URL) or "cache" (use cached)
            
        Returns:
            Dictionary with scraped content and fallback info
        """
        logger.info(f"Scraping {len(urls)} URLs with '{fallback_strategy}' fallback strategy")
        
        results = {
            "primary_results": [],
            "fallback_results": [],
            "failed_urls": [],
            "success_rate": 0.0,
            "content_sources": [],
            "total_content_length": 0
        }
        
        for i, url in enumerate(urls):
            logger.debug(f"Attempting URL {i+1}/{len(urls)}: {url}")
            
            # Try to scrape URL
            content = self._scrape_url_with_retry(url)
            
            if content:
                # Success
                result_entry = {
                    "url": url,
                    "content": content,
                    "length": len(content),
                    "source": "primary",
                    "attempt": 1
                }
                results["primary_results"].append(result_entry)
                results["content_sources"].append(url)
                results["total_content_length"] += len(content)
                
                logger.info(f"Successfully scraped: {url} ({len(content)} chars)")
            else:
                # Failed - try fallback
                logger.warning(f"Failed to scrape: {url}")
                self.failed_urls.add(url)
                results["failed_urls"].append(url)
                
                # Try fallback strategy
                fallback_content = self._apply_fallback_strategy(url, urls, fallback_strategy)
                
                if fallback_content:
                    result_entry = {
                        "original_url": url,
                        "fallback_url": fallback_content.get("fallback_url"),
                        "content": fallback_content.get("content"),
                        "length": len(fallback_content.get("content", "")),
                        "source": "fallback",
                        "fallback_type": fallback_content.get("fallback_type")
                    }
                    results["fallback_results"].append(result_entry)
                    results["content_sources"].append(fallback_content.get("fallback_url", "cache"))
                    results["total_content_length"] += len(fallback_content.get("content", ""))
        
        # Calculate success rate
        total_attempted = len(urls)
        successful = len(results["primary_results"]) + len(results["fallback_results"])
        results["success_rate"] = (successful / total_attempted * 100) if total_attempted > 0 else 0
        
        logger.info(
            f"Scraping complete - {successful}/{total_attempted} successful "
            f"({results['success_rate']:.1f}%)"
        )
        
        return results
    
    def _scrape_url_with_retry(self, url: str) -> Optional[str]:
        """
        Scrape URL with retry mechanism.
        
        Args:
            url: URL to scrape
            
        Returns:
            Content or None if failed
        """
        last_error = None
        
        for attempt in range(1, self.max_retries + 1):
            try:
                logger.debug(f"Scrape attempt {attempt}/{self.max_retries} for: {url}")
                
                content = self.scraping_service.scrape_url(url, timeout=self.timeout)
                
                if content and len(content.strip()) > 100:  # Minimum content
                    return content
                
                logger.debug(f"Attempt {attempt} returned insufficient content")
                
            except Exception as e:
                last_error = str(e)
                logger.debug(f"Attempt {attempt} failed: {last_error}")
                
                if attempt < self.max_retries:
                    # Exponential backoff between retries
                    import time
                    wait_time = (2 ** (attempt - 1))  # 1s, 2s, 4s
                    logger.debug(f"Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
        
        logger.warning(f"All {self.max_retries} attempts failed for {url}: {last_error}")
        return None
    
    def _apply_fallback_strategy(self, failed_url: str, all_urls: List[str], 
                                 strategy: str) -> Optional[Dict]:
        """
        Apply fallback strategy when URL fails to scrape.
        
        Args:
            failed_url: URL that failed
            all_urls: All attempted URLs
            strategy: Fallback strategy ("alternative" or "cache")
            
        Returns:
            Fallback result or None
        """
        if strategy == "alternative":
            return self._try_alternative_urls(failed_url, all_urls)
        elif strategy == "cache":
            return self._try_cached_content(failed_url)
        else:
            logger.warning(f"Unknown fallback strategy: {strategy}")
            return None
    
    def _try_alternative_urls(self, failed_url: str, all_urls: List[str]) -> Optional[Dict]:
        """
        Try scraping alternative URLs when one fails.
        
        Args:
            failed_url: URL that failed
            all_urls: All URLs available
            
        Returns:
            Result from alternative URL or None
        """
        logger.info(f"Attempting fallback: trying alternative URLs for {failed_url}")
        
        # Get remaining URLs (those not yet tried or failed)
        alternatives = [u for u in all_urls if u not in self.failed_urls and u != failed_url]
        
        if not alternatives:
            logger.warning("No alternative URLs available")
            return None
        
        # Try each alternative
        for alt_url in alternatives:
            logger.debug(f"Trying alternative: {alt_url}")
            content = self._scrape_url_with_retry(alt_url)
            
            if content:
                logger.info(f"Fallback successful using: {alt_url}")
                return {
                    "fallback_url": alt_url,
                    "content": content,
                    "fallback_type": "alternative_url"
                }
        
        logger.warning("No alternative URLs succeeded")
        return None
    
    def _try_cached_content(self, url: str) -> Optional[Dict]:
        """
        Try retrieving cached content for failed URL.
        
        Args:
            url: URL to get cache for
            
        Returns:
            Cached content or None
        """
        logger.info(f"Attempting fallback: checking cache for {url}")
        
        try:
            cached = self.scraping_service.get_cached_content(url)
            
            if cached:
                logger.info(f"Fallback successful using cached content for {url}")
                return {
                    "fallback_url": url,
                    "content": cached,
                    "fallback_type": "cached_content"
                }
        except Exception as e:
            logger.debug(f"Cache lookup failed: {str(e)}")
        
        return None
    
    def scrape_batch_with_validation(self, urls: List[str]) -> Dict:
        """
        Scrape batch of URLs with content validation.
        
        Args:
            urls: List of URLs
            
        Returns:
            Validated scraping results
        """
        logger.info(f"Batch scraping with validation: {len(urls)} URLs")
        
        results = self.scrape_with_fallback(urls)
        
        # Add validation
        validated_results = {
            "all_results": [],
            "valid_results": [],
            "invalid_results": [],
            "validation_summary": {}
        }
        
        all_items = results["primary_results"] + results["fallback_results"]
        
        for item in all_items:
            validation = self._validate_content(item["content"])
            item["validation"] = validation
            item["is_valid"] = validation["is_valid"]
            
            validated_results["all_results"].append(item)
            
            if validation["is_valid"]:
                validated_results["valid_results"].append(item)
            else:
                validated_results["invalid_results"].append(item)
        
        validated_results["validation_summary"] = {
            "total": len(all_items),
            "valid": len(validated_results["valid_results"]),
            "invalid": len(validated_results["invalid_results"]),
            "success_rate": (len(validated_results["valid_results"]) / len(all_items) * 100) if all_items else 0
        }
        
        logger.info(
            f"Validation complete - {validated_results['validation_summary']['valid']}/{len(all_items)} valid"
        )
        
        return validated_results
    
    def _validate_content(self, content: str) -> Dict:
        """
        Validate scraped content.
        
        Args:
            content: Content to validate
            
        Returns:
            Validation result dictionary
        """
        issues = []
        score = 1.0
        
        # Check minimum length
        if len(content) < 100:
            issues.append("content_too_short")
            score -= 0.3
        
        # Check for HTML remnants
        html_tags = content.count("<") + content.count(">")
        if html_tags > len(content) * 0.01:  # More than 1% HTML
            issues.append("html_not_fully_cleaned")
            score -= 0.2
        
        # Check density (too many special chars = low quality)
        special_chars = sum(1 for c in content if not c.isalnum() and not c.isspace())
        if special_chars > len(content) * 0.2:
            issues.append("high_special_char_density")
            score -= 0.1
        
        # Check for actual text
        words = len(content.split())
        if words < 20:
            issues.append("insufficient_words")
            score -= 0.3
        
        return {
            "is_valid": len(issues) == 0 and score > 0.5,
            "score": max(score, 0),
            "issues": issues,
            "word_count": words,
            "length": len(content)
        }
    
    def get_failure_analysis(self) -> Dict:
        """
        Analyze scraping failures and patterns.
        
        Returns:
            Failure analysis report
        """
        return {
            "total_failed_urls": len(self.failed_urls),
            "failed_urls_sample": list(self.failed_urls)[:10],
            "failure_rate_estimate": f"{len(self.failed_urls) / max(1, len(self.failed_urls) + 1) * 100:.1f}%"
        }
