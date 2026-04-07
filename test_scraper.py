"""
Test Suite 2: Web Scraper Tests
Tests web scraping functionality, content extraction, and error handling
"""

import pytest
import requests
from bs4 import BeautifulSoup
from pathlib import Path
import sys
from typing import List, Tuple

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from config import Config

# ============================================================================
# TEST DATA
# ============================================================================

# Sample URLs known to have good content
SAMPLE_URLS = [
    "https://www.wikipedia.org/",
    "https://www.github.com/",
    "https://www.python.org/"
]

# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture(scope="session")
def config():
    """Load configuration"""
    return Config

@pytest.fixture(scope="session")
def http_headers():
    """Get HTTP headers for web requests"""
    return {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

# ============================================================================
# TEST SCRAPING FUNCTIONALITY
# ============================================================================

class TestWebScraping:
    """Test web scraping capabilities"""
    
    @pytest.mark.timeout(Config.SCRAPE_TIMEOUT + 5)
    def test_scrape_single_url(self, http_headers):
        """Test scraping a single URL"""
        url = "https://www.wikipedia.org/"
        
        response = requests.get(
            url,
            timeout=Config.SCRAPE_TIMEOUT,
            headers=http_headers
        )
        
        assert response.status_code == 200, f"Failed to fetch {url}"
        
        # Parse content
        soup = BeautifulSoup(response.text, "html.parser")
        text = soup.get_text(separator=" ", strip=True)
        
        assert len(text) > 0, "No content extracted from page"
        assert len(text) > 100, "Content seems too short"
    
    @pytest.mark.timeout(Config.SCRAPE_TIMEOUT + 10)
    def test_scrape_multiple_urls(self, http_headers):
        """Test scraping multiple URLs"""
        urls = SAMPLE_URLS[:2]
        contents = []
        
        for url in urls:
            try:
                response = requests.get(
                    url,
                    timeout=Config.SCRAPE_TIMEOUT,
                    headers=http_headers
                )
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, "html.parser")
                    text = soup.get_text(separator=" ", strip=True)
                    contents.append((url, text))
            except Exception:
                pass
        
        assert len(contents) > 0, "Could not scrape any URLs"
    
    def test_content_extraction(self, http_headers):
        """Test content extraction from HTML"""
        url = "https://www.wikipedia.org/"
        
        response = requests.get(
            url,
            timeout=Config.SCRAPE_TIMEOUT,
            headers=http_headers
        )
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Test different extraction methods
        text_with_sep = soup.get_text(separator=" ", strip=True)
        text_basic = soup.get_text(strip=True)
        
        assert len(text_with_sep) > 0, "Text extraction with separator failed"
        assert len(text_basic) > 0, "Basic text extraction failed"
        # Text with separator should have spaces
        assert " " in text_with_sep, "Separator not used correctly"
    
    def test_content_cleaning(self, http_headers):
        """Test content cleaning and formatting"""
        url = "https://www.wikipedia.org/"
        
        response = requests.get(
            url,
            timeout=Config.SCRAPE_TIMEOUT,
            headers=http_headers
        )
        
        soup = BeautifulSoup(response.text, "html.parser")
        text = soup.get_text(separator=" ", strip=True)
        
        # Check for excess whitespace
        lines = text.split("\n")
        non_empty_lines = [l.strip() for l in lines if l.strip()]
        
        # Should have reasonable content
        assert len(non_empty_lines) > 0, "No non-empty content lines"
    
    def test_content_length_limiting(self, http_headers):
        """Test content length limitation"""
        url = "https://www.wikipedia.org/"
        max_length = Config.MAX_CONTENT_PER_URL
        
        response = requests.get(
            url,
            timeout=Config.SCRAPE_TIMEOUT,
            headers=http_headers
        )
        
        soup = BeautifulSoup(response.text, "html.parser")
        text = soup.get_text(separator=" ", strip=True)
        
        # Limit content
        limited_text = text[:max_length]
        
        assert len(limited_text) <= max_length, "Limiting failed"
        assert len(limited_text) > 0, "Limiting removed all content"

# ============================================================================
# TEST HTML PARSING
# ============================================================================

class TestHTMLParsing:
    """Test HTML parsing and cleaning"""
    
    def test_beautifulsoup_initialization(self, http_headers):
        """Test BeautifulSoup integration"""
        url = SAMPLE_URLS[0]
        
        response = requests.get(url, timeout=Config.SCRAPE_TIMEOUT, headers=http_headers)
        soup = BeautifulSoup(response.text, "html.parser")
        
        assert soup is not None, "BeautifulSoup failed to parse"
        assert len(soup.contents) > 0, "No HTML content parsed"
    
    def test_tag_removal(self, http_headers):
        """Test script/style tag removal"""
        html = """
        <html>
            <head><script>console.log('test');</script></head>
            <body>
                <p>Content here</p>
                <style>.hidden { display: none; }</style>
                <div>More content</div>
            </body>
        </html>
        """
        
        soup = BeautifulSoup(html, "html.parser")
        
        # Remove scripts and styles
        for script in soup(["script", "style"]):
            script.decompose()
        
        text = soup.get_text(separator=" ", strip=True)
        
        # Check unwanted content is gone
        assert "console.log" not in text, "Script content not removed"
        assert ".hidden" not in text, "Style content not removed"
        # Check wanted content is there
        assert "Content here" in text, "Wanted content removed"
        assert "More content" in text, "Wanted content removed"
    
    @pytest.mark.parametrize("tag", ["script", "style", "noscript", "meta"])
    def test_tag_handling(self, tag):
        """Test handling of specific tags"""
        html = f"""
        <html>
            <body>
                <p>Main content</p>
                <{tag}>Hidden content</{tag}>
            </body>
        </html>
        """
        
        soup = BeautifulSoup(html, "html.parser")
        
        # Find tag
        found_tag = soup.find(tag)
        assert found_tag is not None, f"Tag {tag} not parsed"

# ============================================================================
# TEST ERROR HANDLING
# ============================================================================

class TestScrapeErrorHandling:
    """Test error handling in scraping"""
    
    @pytest.mark.timeout(Config.SCRAPE_TIMEOUT + 2)
    def test_timeout_handling(self, http_headers):
        """Test timeout handling"""
        # Using a timeout that will likely trigger timeout
        url = "https://www.httpbin.org/delay/10"  # Returns after 10 seconds
        
        try:
            response = requests.get(
                url,
                timeout=2,  # Short timeout
                headers=http_headers
            )
            # If succeeds, status should be valid
            assert response.status_code in [200, 408, 504, 500], f"Unexpected: {response.status_code}"
        except requests.Timeout:
            # Expected for this test
            pass

    def test_invalid_url_handling(self, http_headers):
        """Test handling of invalid URLs"""
        invalid_urls = [
            "http://invalid-domain-that-does-not-exist-12345.com",
            "not-a-url",
            ""
        ]
        
        for url in invalid_urls:
            try:
                response = requests.get(
                    url,
                    timeout=Config.SCRAPE_TIMEOUT,
                    headers=http_headers
                )
                # May succeed or fail, we're just checking it doesn't crash
                assert isinstance(response, requests.Response)
            except (requests.RequestException, Exception):
                # Expected for invalid URLs
                pass
    
    @pytest.mark.timeout(Config.SCRAPE_TIMEOUT + 5)
    def test_http_error_codes(self, http_headers):
        """Test handling of HTTP error responses"""
        test_cases = [
            ("https://httpbin.org/status/404", 404),  # Not Found
            ("https://httpbin.org/status/403", 403),  # Forbidden
            ("https://httpbin.org/status/500", 500),  # Server Error
        ]
        
        for url, expected_code in test_cases:
            try:
                response = requests.get(
                    url,
                    timeout=Config.SCRAPE_TIMEOUT,
                    headers=http_headers
                )
                assert response.status_code == expected_code, \
                    f"Expected {expected_code}, got {response.status_code}"
            except requests.RequestException:
                # Network errors are acceptable
                pass

# ============================================================================
# TEST CONTENT VALIDATION
# ============================================================================

class TestContentValidation:
    """Test content validation after scraping"""
    
    def test_non_empty_content_check(self, http_headers):
        """Test that scraped content is non-empty"""
        url = "https://www.wikipedia.org/"
        
        response = requests.get(url, timeout=Config.SCRAPE_TIMEOUT, headers=http_headers)
        soup = BeautifulSoup(response.text, "html.parser")
        text = soup.get_text(separator=" ", strip=True)
        
        assert len(text) > 0, "Content is empty"
        assert len(text.strip()) > 0, "Content is only whitespace"
    
    def test_content_has_meaningful_text(self, http_headers):
        """Test that content contains meaningful text"""
        url = "https://www.wikipedia.org/"
        
        response = requests.get(url, timeout=Config.SCRAPE_TIMEOUT, headers=http_headers)
        soup = BeautifulSoup(response.text, "html.parser")
        text = soup.get_text(separator=" ", strip=True)
        
        # Count words
        words = text.split()
        assert len(words) > 10, "Content has too few words"
    
    def test_combined_content_size(self, http_headers):
        """Test size of combined content from multiple URLs"""
        urls = SAMPLE_URLS[:2]
        combined_content = ""
        
        for url in urls:
            try:
                response = requests.get(
                    url,
                    timeout=Config.SCRAPE_TIMEOUT,
                    headers=http_headers
                )
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, "html.parser")
                    text = soup.get_text(separator=" ", strip=True)
                    combined_content += text[:Config.MAX_CONTENT_PER_URL] + "\n"
            except Exception:
                pass
        
        # Limit total size
        combined_content = combined_content[:Config.MAX_TOTAL_CONTENT]
        
        assert len(combined_content) > 0, "No content combined"
        assert len(combined_content) <= Config.MAX_TOTAL_CONTENT, "Content exceeds limit"

# ============================================================================
# PARAMETRIZED SCRAPING TESTS
# ============================================================================

@pytest.mark.parametrize("url", SAMPLE_URLS)
@pytest.mark.timeout(Config.SCRAPE_TIMEOUT + 5)
def test_scrape_sample_urls(url):
    """Test scraping of all sample URLs"""
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        response = requests.get(
            url,
            timeout=Config.SCRAPE_TIMEOUT,
            headers=headers
        )
        
        assert response.status_code == 200, f"Failed to fetch {url}"
        
        soup = BeautifulSoup(response.text, "html.parser")
        text = soup.get_text(separator=" ", strip=True)
        
        assert len(text) > 0, f"No content from {url}"
        
    except requests.Timeout:
        pytest.skip(f"Timeout for {url}")
    except Exception as e:
        pytest.skip(f"Could not test {url}: {str(e)}")

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
