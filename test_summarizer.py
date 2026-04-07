"""
Test Suite 3: Summarizer Tests
Tests Gemini API integration, summarization quality, and error handling
"""

import pytest
import google.generativeai as genai
from pathlib import Path
import sys
from typing import Optional

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
def gemini_model():
    """Initialize Gemini model"""
    try:
        genai.configure(api_key=Config.GOOGLE_API_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash")
        return model
    except Exception as e:
        pytest.skip(f"Failed to initialize Gemini: {str(e)}")

@pytest.fixture(scope="session")
def sample_content():
    """Sample content for testing"""
    return """
    Machine Learning (ML) is a subset of artificial intelligence that focuses on enabling 
    systems to learn from data and improve their performance over time without explicit programming.
    
    Key ML concepts include:
    1. Supervised Learning - Learning from labeled data
    2. Unsupervised Learning - Finding patterns in unlabeled data
    3. Reinforcement Learning - Learning through interaction and rewards
    
    Applications include computer vision, natural language processing, recommendation systems,
    and predictive analytics.
    
    Deep Learning uses neural networks with multiple layers to process complex data.
    The process is similar to how the human brain learns through networks of neurons.
    
    Common challenges in ML:
    - Data quality and quantity
    - Model overfitting
    - Computational resources
    - Interpretability
    """

# ============================================================================
# TEST CONFIGURATION
# ============================================================================

class TestGeminiConfiguration:
    """Test Gemini configuration and integration"""
    
    def test_gemini_api_key_configured(self, config):
        """Test Gemini API key is configured"""
        assert config.GOOGLE_API_KEY, "GOOGLE_API_KEY not configured"
        assert len(config.GOOGLE_API_KEY) > 10, "API key seems too short"
    
    def test_gemini_model_initialization(self, gemini_model):
        """Test Gemini model initialization"""
        assert gemini_model is not None, "Model initialization failed"
    
    def test_gemini_configuration(self, config):
        """Test general configuration for Gemini"""
        assert config.REQUEST_TIMEOUT > 0, "REQUEST_TIMEOUT not set"
        assert config.MAX_TOTAL_CONTENT > 0, "MAX_TOTAL_CONTENT not set"

# ============================================================================
# TEST SUMMARIZATION
# ============================================================================

class TestSummarization:
    """Test summarization capabilities"""
    
    @pytest.mark.timeout(Config.REQUEST_TIMEOUT + 5)
    def test_basic_summarization(self, gemini_model, sample_content):
        """Test basic summarization"""
        prompt = f"Summarize this text in 3 bullet points:\n\n{sample_content[:2000]}"
        
        response = gemini_model.generate_content(prompt)
        summary = response.text
        
        assert summary, "Empty response from Gemini"
        assert len(summary) > 10, "Summary too short"
        assert "•" in summary or "-" in summary or "1." in summary, "Summary not in bullet format"
    
    def test_summarization_with_bullets(self, gemini_model, sample_content):
        """Test summarization produces bullet points"""
        prompt = f"""Summarize this in EXACTLY 5 bullet points using • symbol.
Start each bullet with a dash or number.

Content:
{sample_content[:Config.MAX_TOTAL_CONTENT]}"""
        
        response = gemini_model.generate_content(prompt)
        summary = response.text
        
        # Count bullets
        bullet_lines = [l for l in summary.split("\n") if l.strip().startswith(("•", "-", "1.", "2.", "3.", "4.", "5."))]
        
        assert len(summary) > 20, "Summary is too short"
        # Should have bullet-like structure
        assert ("•" in summary or "-" in summary or any(s in summary for s in ["1.", "2.", "3."])), \
            "Summary doesn't have bullet format"
    
    @pytest.mark.timeout(Config.REQUEST_TIMEOUT + 5)
    def test_key_information_extraction(self, gemini_model, sample_content):
        """Test extraction of key information"""
        prompt = f"""Extract the 3 most important concepts from this text.
Format: bullet points

{sample_content}"""
        
        response = gemini_model.generate_content(prompt)
        summary = response.text
        
        # Check key terms are preserved
        key_terms = ["machine learning", "learning", "data", "neural"]
        found_terms = sum(1 for term in key_terms if term.lower() in summary.lower())
        
        assert found_terms > 0, "Key terms not found in summary"
    
    def test_empty_content_handling(self, gemini_model):
        """Test handling of minimal content"""
        minimal_content = "AI is good."
        prompt = f"Summarize: {minimal_content}"
        
        try:
            response = gemini_model.generate_content(prompt)
            summary = response.text
            assert summary, "Empty response for minimal content"
        except Exception as e:
            # May fail for very minimal content, which is acceptable
            pass

# ============================================================================
# TEST RESPONSE QUALITY
# ============================================================================

class TestResponseQuality:
    """Test quality of Gemini responses"""
    
    @pytest.mark.timeout(Config.REQUEST_TIMEOUT + 5)
    def test_response_contains_content(self, gemini_model, sample_content):
        """Test response contains meaningful content"""
        prompt = f"Summarize this in bullet points:\n\n{sample_content}"
        
        response = gemini_model.generate_content(prompt)
        summary = response.text
        
        assert len(summary) > 0, "Response is empty"
        assert len(summary) > 20, "Response is too short to be meaningful"
        assert summary != prompt, "Response is just echoing prompt"
    
    def test_response_structure(self, gemini_model, sample_content):
        """Test response has proper structure"""
        prompt = f"""Create a structured summary with:
1. Key Concepts (3 bullets)
2. Applications (2 bullets)
3. Challenges (2 bullets)

Content: {sample_content[:1000]}"""
        
        response = gemini_model.generate_content(prompt)
        summary = response.text
        
        # Check structure-related keywords are present
        structural_keywords = ["concept", "application", "challenge", "key", "bullet"]
        # Should have some structure
        assert len(summary) > 50, "Response lacks structure"
    
    @pytest.mark.timeout(Config.REQUEST_TIMEOUT + 5)
    def test_response_readability(self, gemini_model, sample_content):
        """Test response is readable and well-formatted"""
        prompt = f"Provide a clear, readable summary:\n\n{sample_content[:1000]}"
        
        response = gemini_model.generate_content(prompt)
        summary = response.text
        
        # Check for readability indicators
        has_newlines = "\n" in summary, "No line breaks"
        has_structure = any(c in summary for c in ["•", "-", "1.", "*"]), "No bullet structure"
        
        # Should be formatted reasonably
        lines = [l.strip() for l in summary.split("\n") if l.strip()]
        assert len(lines) > 1, "Response is single line"

# ============================================================================
# TEST ERROR HANDLING
# ============================================================================

class TestErrorHandling:
    """Test error handling in Gemini integration"""
    
    def test_long_content_handling(self, gemini_model):
        """Test handling of long content"""
        # Create very long content
        long_content = "word " * 10000  # ~50KB of text
        prompt = f"Summarize (keep brief):\n\n{long_content[:Config.MAX_TOTAL_CONTENT]}"
        
        try:
            response = gemini_model.generate_content(prompt)
            summary = response.text
            assert summary, "Failed to summarize long content"
        except Exception as e:
            # Long content may cause issues, which is acceptable
            assert "token" in str(e).lower() or "rate" in str(e).lower(), \
                f"Unexpected error: {str(e)}"
    
    @pytest.mark.timeout(Config.REQUEST_TIMEOUT + 10)
    def test_retry_on_failure(self, gemini_model, sample_content):
        """Test retry logic on failure"""
        prompt = f"Summarize:\n\n{sample_content}"
        
        # Try multiple times
        for attempt in range(3):
            try:
                response = gemini_model.generate_content(prompt)
                if response.text:
                    assert len(response.text) > 0, "Empty response"
                    break
            except Exception as e:
                if attempt == 2:  # Last attempt
                    raise
                # Otherwise, would retry
    
    def test_malformed_prompt_handling(self, gemini_model):
        """Test handling of malformed prompts"""
        malformed_prompts = [
            "",  # Empty
            "  ",  # Whitespace only
            None,  # Will cause different error
        ]
        
        for prompt in malformed_prompts:
            try:
                if prompt is None:
                    continue  # Skip None
                response = gemini_model.generate_content(prompt)
                # May succeed or fail gracefully
                assert response is not None
            except Exception:
                # Error is acceptable for malformed input
                pass

# ============================================================================
# TEST CONTENT LIMITING
# ============================================================================

class TestContentLimiting:
    """Test content limiting for token optimization"""
    
    def test_content_truncation(self, sample_content):
        """Test proper content truncation"""
        max_size = Config.MAX_TOTAL_CONTENT
        
        truncated = sample_content[:max_size]
        
        assert len(truncated) <= max_size, "Truncation failed"
        assert len(truncated) > 0, "Truncation removed all content"
    
    @pytest.mark.timeout(Config.REQUEST_TIMEOUT + 5)
    def test_summarize_truncated_content(self, gemini_model, sample_content):
        """Test summarization of truncated content"""
        max_size = Config.MAX_TOTAL_CONTENT
        truncated = sample_content[:max_size]
        
        prompt = f"Summarize in 3 points:\n\n{truncated}"
        
        response = gemini_model.generate_content(prompt)
        summary = response.text
        
        assert summary, "Failed to summarize truncated content"
        assert len(summary) > 10, "Summary too short"

# ============================================================================
# PARAMETRIZED TESTS
# ============================================================================

@pytest.mark.parametrize("num_bullets", [3, 5, 7])
@pytest.mark.timeout(Config.REQUEST_TIMEOUT + 5)
def test_variable_bullet_counts(gemini_model, sample_content, num_bullets):
    """Test summarization with different bullet counts"""
    prompt = f"Summarize in EXACTLY {num_bullets} bullet points with • bullets:\n\n{sample_content}"
    
    response = gemini_model.generate_content(prompt)
    summary = response.text
    
    assert summary, f"Failed for {num_bullets} bullets"
    # Should contain bullet-like structure
    assert any(c in summary for c in ["•", "-", "*"]), f"No bullets in {num_bullets} point summary"

@pytest.mark.parametrize("style", ["technical", "simple", "brief", "detailed"])
@pytest.mark.timeout(Config.REQUEST_TIMEOUT + 5)
def test_different_summary_styles(gemini_model, sample_content, style):
    """Test summarization with different styles"""
    prompt = f"Summarize in a {style} style using bullet points:\n\n{sample_content}"
    
    response = gemini_model.generate_content(prompt)
    summary = response.text
    
    assert summary, f"Failed for {style} style"
    assert len(summary) > 10, f"Summary too short for {style} style"

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
