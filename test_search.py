"""
Test Suite 1: Search Service Tests
Tests Serper API response, URL validation, and error handling
"""

import pytest
import requests
from pathlib import Path
import sys
import os

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from config import Config

# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture(scope="session")
def config():
    """Load configuration"""
    return Config

@pytest.fixture(scope="session")
def serper_headers():
    """Get Serper API headers"""
    return {
        "X-API-KEY": Config.SERPER_API_KEY,
        "Content-Type": "application/json"
    }

# ============================================================================
# TEST CONFIGURATION
# ============================================================================

class TestConfiguration:
    """Test configuration loading and validation"""
    
    def test_config_validate(self, config):
        """Test configuration validation"""
        is_valid, errors = config.validate()
        assert is_valid, f"Configuration invalid: {errors}"
    
    def test_google_api_key_configured(self, config):
        """Test Google API key is configured"""
        assert config.GOOGLE_API_KEY, "GOOGLE_API_KEY not configured"
        assert not config.GOOGLE_API_KEY.startswith("sk-"), "Google API key not filled in"
    
    def test_serper_api_key_configured(self, config):
        """Test Serper API key is configured"""
        assert config.SERPER_API_KEY, "SERPER_API_KEY not configured"
        assert not config.SERPER_API_KEY.startswith("x"), "Serper API key not filled in"
    
    def test_timeout_values_valid(self, config):
        """Test timeout values are reasonable"""
        assert config.REQUEST_TIMEOUT > 0, "REQUEST_TIMEOUT must be > 0"
        assert config.SERPER_TIMEOUT > 0, "SERPER_TIMEOUT must be > 0"
        assert config.SCRAPE_TIMEOUT > 0, "SCRAPE_TIMEOUT must be > 0"
        assert config.SERPER_TIMEOUT <= config.REQUEST_TIMEOUT, "Serper timeout should be less than general timeout"

# ============================================================================
# TEST SERPER API
# ============================================================================

class TestSerperAPI:
    """Test Serper API integration"""
    
    @pytest.mark.timeout(Config.SERPER_TIMEOUT + 5)
    def test_serper_search_success(self, serper_headers):
        """Test successful Serper API search"""
        query = "machine learning fundamentals"
        data = {"q": query, "num": 10}
        
        response = requests.post(
            "https://google.serper.dev/search",
            headers=serper_headers,
            json=data,
            timeout=Config.SERPER_TIMEOUT
        )
        
        assert response.status_code == 200, f"Serper API returned {response.status_code}"
        
        results = response.json()
        assert "organic" in results, "Organic results not in response"
        assert len(results["organic"]) > 0, "No organic results returned"
    
    def test_serper_url_extraction(self, serper_headers):
        """Test URL extraction from Serper response"""
        query = "artificial intelligence"
        data = {"q": query, "num": 5}
        
        response = requests.post(
            "https://google.serper.dev/search",
            headers=serper_headers,
            json=data,
            timeout=Config.SERPER_TIMEOUT
        )
        
        results = response.json()
        urls = [
            result["link"]
            for result in results.get("organic", [])
            if "link" in result
        ]
        
        assert len(urls) > 0, "No URLs extracted"
        assert len(urls) <= 5, f"More URLs than requested: {len(urls)}"
        
        # Validate URL format
        for url in urls:
            assert url.startswith("http"), f"Invalid URL format: {url}"
            assert "." in url, f"URL missing domain: {url}"
    
    def test_serper_url_list_length(self, serper_headers):
        """Test URL list matches requested count"""
        for num_results in [3, 5, 10]:
            query = "python programming"
            data = {"q": query, "num": num_results}
            
            response = requests.post(
                "https://google.serper.dev/search",
                headers=serper_headers,
                json=data,
                timeout=Config.SERPER_TIMEOUT
            )
            
            results = response.json()
            urls = [r["link"] for r in results.get("organic", []) if "link" in r]
            
            assert len(urls) > 0, f"Expected URLs for {num_results} results"
            assert len(urls) <= num_results, f"Got more URLs than requested"
    
    @pytest.mark.timeout(Config.SERPER_TIMEOUT + 5)
    def test_serper_timeout_handling(self, serper_headers):
        """Test Serper API timeout handling"""
        query = "timeout test"
        data = {"q": query}
        
        try:
            response = requests.post(
                "https://google.serper.dev/search",
                headers=serper_headers,
                json=data,
                timeout=1  # Very short timeout to test error handling
            )
            # If it doesn't timeout, that's fine
            assert response.status_code in [200, 408, 504], f"Unexpected status: {response.status_code}"
        except requests.Timeout:
            # Timeout is expected
            pass
    
    def test_serper_response_structure(self, serper_headers):
        """Test Serper response has expected structure"""
        query = "data science"
        data = {"q": query, "num": 3}
        
        response = requests.post(
            "https://google.serper.dev/search",
            headers=serper_headers,
            json=data,
            timeout=Config.SERPER_TIMEOUT
        )
        
        results = response.json()
        
        # Check expected keys
        assert isinstance(results, dict), "Response is not a dictionary"
        assert "organic" in results or "news" in results, "No results section found"
        
        # Validate organic results structure
        if "organic" in results:
            assert isinstance(results["organic"], list), "Organic results not a list"
            for result in results["organic"][:3]:  # Check first 3
                assert "link" in result, "Result missing 'link' field"
                assert "title" in result, "Result missing 'title' field"

# ============================================================================
# TEST ERROR HANDLING
# ============================================================================

class TestErrorHandling:
    """Test error scenarios"""
    
    def test_empty_query_handling(self):
        """Test handling of empty query"""
        from config import Config
        headers = {
            "X-API-KEY": Config.SERPER_API_KEY,
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(
                "https://google.serper.dev/search",
                headers=headers,
                json={"q": ""},
                timeout=Config.SERPER_TIMEOUT
            )
            # API should handle empty query
            assert response.status_code in [200, 400], "Invalid status for empty query"
        except Exception:
            # Some error is acceptable for empty query
            pass
    
    def test_invalid_api_key_handling(self):
        """Test handling of invalid API key"""
        headers = {
            "X-API-KEY": "invalid_key_12345",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            "https://google.serper.dev/search",
            headers=headers,
            json={"q": "test"},
            timeout=10
        )
        
        # Should return 401 or 403 for invalid key
        assert response.status_code in [401, 403, 400], f"Expected auth error, got {response.status_code}"

# ============================================================================
# PARAMETRIZED TESTS
# ============================================================================

@pytest.mark.parametrize("query", [
    "machine learning",
    "artificial intelligence",
    "deep learning",
    "neural networks",
    "python programming"
])
def test_multiple_queries(query, serper_headers):
    """Test multiple search queries"""
    data = {"q": query, "num": 5}
    
    response = requests.post(
        "https://google.serper.dev/search",
        headers=serper_headers,
        json=data,
        timeout=Config.SERPER_TIMEOUT
    )
    
    assert response.status_code == 200, f"Failed for query: {query}"
    results = response.json()
    urls = [r["link"] for r in results.get("organic", []) if "link" in r]
    assert len(urls) > 0, f"No results for query: {query}"

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
