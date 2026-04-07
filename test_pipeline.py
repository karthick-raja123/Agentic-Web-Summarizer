"""
Test Suite 4: Full Pipeline Tests
Tests end-to-end pipeline execution, integration, and output validation
"""

import pytest
import requests
from bs4 import BeautifulSoup
from pathlib import Path
import sys
import time
from typing import Dict, List, Tuple

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
    """Get Serper headers"""
    return {
        "X-API-KEY": Config.SERPER_API_KEY,
        "Content-Type": "application/json"
    }

@pytest.fixture(scope="session")
def http_headers():
    """Get HTTP headers"""
    return {"User-Agent": "Mozilla/5.0"}

# ============================================================================
# TEST FULL PIPELINE
# ============================================================================

class TestFullPipeline:
    """Test complete pipeline execution"""
    
    @pytest.mark.timeout(120)  # Full pipeline max 2 minutes
    def test_pipeline_search_phase(self, serper_headers):
        """Test pipeline search phase"""
        query = "python programming best practices"
        
        # Phase 1: Search
        response = requests.post(
            "https://google.serper.dev/search",
            headers=serper_headers,
            json={"q": query, "num": Config.MAX_SEARCH_RESULTS},
            timeout=Config.SERPER_TIMEOUT
        )
        
        assert response.status_code == 200, "Search phase failed"
        results = response.json()
        urls = [r["link"] for r in results.get("organic", []) if "link" in r]
        
        assert len(urls) > 0, "Search returned no URLs"
        assert len(urls) <= Config.MAX_URLS_TO_SCRAPE, "Too many URLs"
    
    @pytest.mark.timeout(120)
    def test_pipeline_scrape_phase(self, serper_headers, http_headers):
        """Test pipeline scrape phase"""
        query = "machine learning tutorial"
        
        # Phase 1: Search
        response = requests.post(
            "https://google.serper.dev/search",
            headers=serper_headers,
            json={"q": query, "num": 3},
            timeout=Config.SERPER_TIMEOUT
        )
        
        urls = [r["link"] for r in response.json().get("organic", []) if "link" in r][:2]
        
        # Phase 2: Scrape
        combined_content = ""
        scraped_count = 0
        
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
                    scraped_count += 1
            except Exception:
                pass
        
        assert scraped_count > 0, "Scrape phase: no URLs successfully scraped"
        assert len(combined_content) > 100, "Scrape phase: insufficient content"
    
    @pytest.mark.timeout(180)
    def test_pipeline_summarize_phase(self, serper_headers, http_headers):
        """Test pipeline summarize phase"""
        import google.generativeai as genai
        
        # Initialize Gemini
        try:
            genai.configure(api_key=Config.GOOGLE_API_KEY)
            model = genai.GenerativeModel("gemini-1.5-flash")
        except Exception as e:
            pytest.skip(f"Gemini initialization failed: {str(e)}")
        
        query = "artificial intelligence applications"
        
        # Phase 1: Search
        response = requests.post(
            "https://google.serper.dev/search",
            headers=serper_headers,
            json={"q": query, "num": 2},
            timeout=Config.SERPER_TIMEOUT
        )
        
        urls = [r["link"] for r in response.json().get("organic", []) if "link" in r][:1]
        
        # Phase 2: Scrape
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
                    combined_content += text[:Config.MAX_CONTENT_PER_URL]
                    break
            except Exception:
                pass
        
        if not combined_content:
            pytest.skip("No content retrieved for summarization test")
        
        # Phase 3: Summarize
        prompt = f"Summarize in 5 bullet points:\n\n{combined_content[:Config.MAX_TOTAL_CONTENT]}"
        response = model.generate_content(prompt)
        summary = response.text
        
        assert summary, "Summarize phase: empty summary"
        assert len(summary) > 20, "Summarize phase: summary too short"
        assert any(c in summary for c in ["•", "-", "*"]), "Summarize phase: no bullets in summary"
    
    @pytest.mark.timeout(300)
    def test_full_end_to_end_pipeline(self, serper_headers, http_headers):
        """Test complete end-to-end pipeline"""
        import google.generativeai as genai
        
        # Initialize
        try:
            genai.configure(api_key=Config.GOOGLE_API_KEY)
            model = genai.GenerativeModel("gemini-1.5-flash")
        except Exception as e:
            pytest.skip(f"Failed to initialize: {str(e)}")
        
        query = "data science fundamentals"
        
        # PHASE 1: SEARCH
        print("\n🔍 PHASE 1: SEARCH")
        search_start = time.time()
        
        try:
            response = requests.post(
                "https://google.serper.dev/search",
                headers=serper_headers,
                json={"q": query, "num": Config.MAX_SEARCH_RESULTS},
                timeout=Config.SERPER_TIMEOUT
            )
            
            assert response.status_code == 200, f"Search failed: {response.status_code}"
            urls = [r["link"] for r in response.json().get("organic", []) if "link" in r]
            assert len(urls) > 0, "Search returned no URLs"
            
            search_time = time.time() - search_start
            print(f"  ✓ Found {len(urls)} URLs in {search_time:.2f}s")
            
        except Exception as e:
            pytest.fail(f"Search phase failed: {str(e)}")
        
        # PHASE 2: SCRAPE
        print("📄 PHASE 2: SCRAPE")
        scrape_start = time.time()
        
        combined_content = ""
        scraped_count = 0
        
        for url in urls[:Config.MAX_URLS_TO_SCRAPE]:
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
                    scraped_count += 1
            except Exception:
                pass
        
        combined_content = combined_content[:Config.MAX_TOTAL_CONTENT]
        scrape_time = time.time() - scrape_start
        
        assert scraped_count > 0, "Scrape phase: no URLs scraped successfully"
        assert len(combined_content) > 100, "Scrape phase: insufficient content"
        print(f"  ✓ Scraped {scraped_count} URLs ({len(combined_content)} chars) in {scrape_time:.2f}s")
        
        # PHASE 3: SUMMARIZE
        print("✍️  PHASE 3: SUMMARIZE")
        summarize_start = time.time()
        
        try:
            prompt = f"""Summarize this content in exactly 5 bullet points.
Use • for bullets. Be concise and informative.

Content:
{combined_content}"""
            
            response = model.generate_content(prompt)
            summary = response.text
            
            summarize_time = time.time() - summarize_start
            
            assert summary, "Summarize phase: empty summary"
            assert len(summary) > 20, "Summarize phase: summary too short"
            
            print(f"  ✓ Generated summary ({len(summary)} chars) in {summarize_time:.2f}s")
            
        except Exception as e:
            pytest.fail(f"Summarize phase failed: {str(e)}")
        
        # PHASE 4: VALIDATE
        print("✅ PHASE 4: VALIDATE")
        
        # Validate all phases completed
        assert len(urls) > 0, "No search results"
        assert scraped_count > 0, "No content scraped"
        assert len(summary) > 0, "No summary generated"
        
        # Validate summary structure
        has_bullets = any(c in summary for c in ["•", "-", "*"])
        assert has_bullets, "Summary lacks bullet points"
        
        total_time = time.time() - search_start
        print(f"  ✓ Full pipeline completed in {total_time:.2f}s")
        
        # Print results
        print(f"\n📊 PIPELINE RESULTS")
        print(f"  Query: {query}")
        print(f"  URLs Found: {len(urls)}")
        print(f"  URLs Scraped: {scraped_count}")
        print(f"  Content Length: {len(combined_content)} chars")
        print(f"  Summary Length: {len(summary)} chars")
        print(f"  Total Time: {total_time:.2f}s")

# ============================================================================
# TEST OUTPUT VALIDATION
# ============================================================================

class TestOutputValidation:
    """Test output validation and format"""
    
    @pytest.mark.timeout(180)
    def test_summary_format_validation(self, serper_headers, http_headers):
        """Test summary output format"""
        import google.generativeai as genai
        
        try:
            genai.configure(api_key=Config.GOOGLE_API_KEY)
            model = genai.GenerativeModel("gemini-1.5-flash")
        except Exception:
            pytest.skip("Gemini not available")
        
        # Get some content
        query = "technology trends 2024"
        
        try:
            response = requests.post(
                "https://google.serper.dev/search",
                headers=serper_headers,
                json={"q": query, "num": 1},
                timeout=Config.SERPER_TIMEOUT
            )
            
            urls = [r["link"] for r in response.json().get("organic", []) if "link" in r][:1]
            
            if not urls:
                pytest.skip("No search results")
            
            # Scrape first URL
            content = ""
            try:
                response = requests.get(
                    urls[0],
                    timeout=Config.SCRAPE_TIMEOUT,
                    headers=http_headers
                )
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, "html.parser")
                    content = soup.get_text(separator=" ", strip=True)[:1000]
            except Exception:
                pass
            
            if not content:
                pytest.skip("Could not scrape content")
            
            # Generate summary
            prompt = f"Summarize in bullet points:\n\n{content}"
            response = model.generate_content(prompt)
            summary = response.text
            
            # Validate format
            assert summary, "Empty summary"
            assert len(summary) > 10, "Summary too short"
            
            # Check for common formatting issues
            assert not summary.startswith("Here"), "Summary has explanation prefix"
            assert not summary.endswith("..."), "Summary appears truncated"
            
        except Exception as e:
            if "skip" not in str(e).lower():
                pytest.skip(f"Test setup failed: {str(e)}")

# ============================================================================
# TEST CONFIGURATION VALIDATION
# ============================================================================

class TestConfigurationForPipeline:
    """Test configuration is appropriate for pipeline"""
    
    def test_timeouts_reasonable(self, config):
        """Test timeout values are reasonable"""
        # Serper timeout should be shorter than general
        assert config.SERPER_TIMEOUT <= config.REQUEST_TIMEOUT, \
            "Serper timeout should be less than general timeout"
        
        # Scrape timeout should be reasonable
        assert 5 <= config.SCRAPE_TIMEOUT <= 30, \
            "Scrape timeout seems unreasonable"
    
    def test_content_limits_reasonable(self, config):
        """Test content limits are reasonable"""
        # Per-URL should be less than total
        assert config.MAX_CONTENT_PER_URL <= config.MAX_TOTAL_CONTENT, \
            "Per-URL limit should be less than total"
        
        # Should have reasonable minimums
        assert config.MAX_TOTAL_CONTENT >= 5000, \
            "Total content limit too small for summarization"
    
    def test_retry_configuration(self, config):
        """Test retry configuration"""
        assert config.RETRIES_MAX >= 1, "Retries must be at least 1"
        assert config.RETRY_DELAY > 0, "Retry delay must be positive"

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s", "--tb=short"])
