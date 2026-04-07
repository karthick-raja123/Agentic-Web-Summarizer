"""
LLM Service - Wrapper for Google Gemini API with retry and token management.
"""

import os
import google.generativeai as genai
from typing import Optional
from utils.logging_config import get_logger
from utils.retry import retry
from services.model_handler import create_model_with_fallback

logger = get_logger(__name__)


class LLMService:
    """Service wrapper for Gemini LLM with advanced features and fallback support."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-1.5-pro"):
        """
        Initialize LLM Service.
        
        Args:
            api_key: Gemini API key (uses GEMINI_API_KEY env var if not provided)
            model: Model name to use
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        # Initialize with fallback support
        try:
            self.model, self.model_name = create_model_with_fallback(self.api_key, preferred_model=model)
            logger.info(f"LLM Service initialized with model: {self.model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize LLM Service: {e}")
            raise
    
    @retry(max_attempts=3, delay=2.0, exceptions=(Exception,))
    def summarize(self, content: str, max_length: int = 5) -> str:
        """
        Summarize content using Gemini.
        
        Args:
            content: Text content to summarize
            max_length: Number of bullet points for summary
            
        Returns:
            Summarized text
        """
        if not content or len(content.strip()) == 0:
            logger.warning("Empty content provided for summarization")
            return "No content to summarize."
        
        # Truncate to avoid token limit
        content = content[:8000]
        
        prompt = f"""Summarize the following text in exactly {max_length} concise bullet points. 
Each bullet point should be clear and informative.
Make sure to capture the key insights.

Text:
{content}

Provide the summary as bullet points only."""
        
        logger.info(f"Summarizing {len(content)} characters of content")
        response = self.model.generate_content(prompt)
        summary = response.text
        
        logger.info("Summarization completed successfully")
        return summary
    
    @retry(max_attempts=3, delay=2.0, exceptions=(Exception,))
    def generate(self, prompt: str) -> str:
        """
        Generate content based on prompt.
        
        Args:
            prompt: Input prompt
            
        Returns:
            Generated text
        """
        if not prompt or len(prompt.strip()) == 0:
            logger.warning("Empty prompt provided for generation")
            return ""
        
        logger.info(f"Generating content for prompt: {prompt[:50]}...")
        response = self.model.generate_content(prompt)
        result = response.text
        
        logger.info("Content generation completed successfully")
        return result
    
    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text.
        Rough estimation: ~4 characters = 1 token (varies by content)
        
        Args:
            text: Text to estimate
            
        Returns:
            Estimated token count
        """
        estimated = len(text) // 4
        logger.debug(f"Estimated tokens: {estimated} for {len(text)} characters")
        return estimated
