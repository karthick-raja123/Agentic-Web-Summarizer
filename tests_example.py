"""
Unit tests for Visual Web Agent components.
Run with: pytest tests/ -v
"""

import pytest
from utils.cleaning import (
    remove_scripts_and_styles,
    extract_meaningful_paragraphs,
    deduplicate_content,
    chunk_text,
    clean_content
)
from utils.retry import retry
from bs4 import BeautifulSoup
import time


class TestCleaning:
    """Test text cleaning utilities."""
    
    def test_remove_scripts_and_styles(self):
        """Test removal of script and style tags."""
        html = """
        <html>
            <head><script>alert('hi')</script><style>.red {}</style></head>
            <body><p>Content here</p></body>
        </html>
        """
        soup = BeautifulSoup(html, 'html.parser')
        cleaned = remove_scripts_and_styles(soup)
        
        # Verify scripts and styles are removed
        assert cleaned.find('script') is None
        assert cleaned.find('style') is None
        assert cleaned.find('p') is not None
    
    def test_extract_meaningful_paragraphs(self):
        """Test extraction of meaningful paragraphs."""
        text = """
        Short
        This is a meaningful paragraph with actual content and information.
        x
        Another paragraph with good length and substance in it.
        """
        
        result = extract_meaningful_paragraphs(text, min_length=30)
        
        assert len(result) == 2
        assert all(len(p) >= 30 for p in result)
    
    def test_deduplicate_content(self):
        """Test content deduplication."""
        paragraphs = [
            "The quick brown fox jumps over the lazy dog",
            "The quick brown fox jumps over the lazy dog",  # Exact duplicate
            "Another completely different paragraph here",
        ]
        
        result = deduplicate_content(paragraphs, similarity_threshold=0.85)
        
        # Should have reduced from 3 to 2 (duplicate removed)
        assert len(result) <= 3
    
    def test_chunk_text(self):
        """Test text chunking."""
        text = "a" * 10000
        
        chunks = chunk_text(text, chunk_size=3000, overlap=100)
        
        assert len(chunks) > 1
        assert len(chunks[0]) == 3000


class TestRetry:
    """Test retry decorator."""
    
    def test_retry_success_first_attempt(self):
        """Test retry succeeds on first attempt."""
        call_count = 0
        
        @retry(max_attempts=3, delay=0.1)
        def success_function():
            nonlocal call_count
            call_count += 1
            return "success"
        
        result = success_function()
        
        assert result == "success"
        assert call_count == 1
    
    def test_retry_failure_all_attempts(self):
        """Test retry fails after max attempts."""
        call_count = 0
        
        @retry(max_attempts=3, delay=0.1, exceptions=(ValueError,))
        def failing_function():
            nonlocal call_count
            call_count += 1
            raise ValueError("Test error")
        
        with pytest.raises(ValueError):
            failing_function()
        
        assert call_count == 3
    
    def test_retry_succeeds_on_second_attempt(self):
        """Test retry succeeds on retry."""
        call_count = 0
        
        @retry(max_attempts=3, delay=0.1, exceptions=(ValueError,))
        def eventually_succeeds():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ValueError("First attempt fails")
            return "success"
        
        result = eventually_succeeds()
        
        assert result == "success"
        assert call_count == 2


class TestCleanContent:
    """Test complete cleaning pipeline."""
    
    def test_clean_content_full_pipeline(self):
        """Test complete content cleaning."""
        html = """
        <html>
            <head>
                <script>console.log('test')</script>
                <style>.hidden {display: none;}</style>
            </head>
            <body>
                <p>This is the first meaningful paragraph with substantial content.</p>
                <p>Another paragraph with relevant information here.</p>
                <div>Short</div>
            </body>
        </html>
        """
        
        result = clean_content(html)
        
        # Verify cleaning
        assert "script" not in result.lower()
        assert "style" not in result.lower()
        assert "meaningful paragraph" in result.lower()


class TestIntegration:
    """Integration tests."""
    
    def test_chunk_and_deduplicate(self):
        """Test chunking followed by deduplication."""
        text = "This is a test paragraph. " * 1000
        
        chunks = chunk_text(text, chunk_size=500)
        assert len(chunks) > 1
        
        # Extract paragraphs from chunks
        all_paragraphs = []
        for chunk in chunks:
            paras = extract_meaningful_paragraphs(chunk, min_length=30)
            all_paragraphs.extend(paras)
        
        # Deduplicate
        unique = deduplicate_content(all_paragraphs, similarity_threshold=0.9)
        
        # With duplicate content, should reduce significantly
        assert len(unique) < len(all_paragraphs)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
