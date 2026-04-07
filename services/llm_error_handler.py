"""
LLM Error Handler - Provides graceful error handling and retry logic for LLM calls.
Specifically handles 404 NOT_FOUND errors with fallback support.
"""

import streamlit as st
from typing import Optional, Callable, Any
from functools import wraps
import time


class LLMError(Exception):
    """Custom exception for LLM-related errors"""
    pass


class ModelNotFoundError(LLMError):
    """Exception when model is not found (404 error)"""
    pass


def handle_llm_error(func: Callable) -> Callable:
    """
    Decorator to handle LLM errors gracefully.
    
    Catches 404 errors and displays appropriate UI messages.
    """
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        try:
            return func(*args, **kwargs)
        
        except Exception as e:
            error_str = str(e).lower()
            error_msg = str(e)
            
            # Handle 404 NOT_FOUND error
            if "404" in error_msg or "not_found" in error_str or "model" in error_str and "not found" in error_str:
                message = "🔄 **Model temporarily unavailable**\n\nThe requested model is not currently available. The system will retry with an alternative model.\n\nPlease try again in a moment."
                st.warning(message)
                raise ModelNotFoundError(f"Model not found: {error_msg}")
            
            # Handle 401 UNAUTHORIZED error
            elif "401" in error_msg or "unauthorized" in error_str or "invalid" in error_str and "key" in error_str:
                message = "❌ **Authentication Failed**\n\nYour API key is invalid or expired.\n\n**Fix:**\n1. Go to https://makersuite.google.com/app/apikey\n2. Generate a new key\n3. Update your .env file\n4. Restart the app"
                st.error(message)
                raise LLMError(f"Authentication failed: {error_msg}")
            
            # Handle timeout errors
            elif "timeout" in error_str or "timed out" in error_str:
                message = "⏱️ **Request Timeout**\n\nThe API is taking too long to respond.\n\n**Try:**\n- Wait a moment and retry\n- Check your internet connection"
                st.warning(message)
                raise LLMError(f"Request timeout: {error_msg}")
            
            # Handle rate limit errors
            elif "429" in error_msg or "rate limit" in error_str or "quota" in error_str:
                message = "📊 **Rate Limit Exceeded**\n\nToo many requests made in a short time.\n\n**Try:**\n- Wait a few minutes\n- Check API quota at https://makersuite.google.com"
                st.warning(message)
                raise LLMError(f"Rate limited: {error_msg}")
            
            # Handle server errors
            elif "500" in error_msg or "503" in error_msg or "server error" in error_str:
                message = "🚨 **API Server Error**\n\nThe service is temporarily unavailable.\n\n**Try:**\n- Wait and retry in a moment\n- Check status: https://status.cloud.google.com"
                st.warning(message)
                raise LLMError(f"Server error: {error_msg}")
            
            # Generic error
            else:
                st.error(f"❌ Error: {error_msg}")
                raise LLMError(f"LLM error: {error_msg}")
    
    return wrapper


def retry_with_fallback(max_attempts: int = 3, delay: float = 2.0):
    """
    Decorator to retry LLM calls with fallback logic.
    
    Args:
        max_attempts: Maximum number of retry attempts
        delay: Delay between retries in seconds
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_error = None
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                
                except ModelNotFoundError as e:
                    last_error = e
                    if attempt < max_attempts - 1:
                        st.info(f"🔄 Retrying... (attempt {attempt + 1}/{max_attempts})")
                        time.sleep(delay)
                    continue
                
                except Exception as e:
                    last_error = e
                    break
            
            # All retries failed
            raise last_error if last_error else LLMError("All retry attempts failed")
        
        return wrapper
    return decorator


def safe_llm_call(summary_func: Callable, content: str, **kwargs) -> Optional[str]:
    """
    Safely call LLM summarization function with error handling.
    
    Args:
        summary_func: The LLM summarization function
        content: Content to summarize
        **kwargs: Additional arguments for the function
        
    Returns:
        Summarized content or None if error
    """
    try:
        result = summary_func(content, **kwargs)
        return result
    
    except ModelNotFoundError:
        st.warning("Model not available. Using cached result or alternative method.")
        return None
    
    except LLMError as e:
        st.error(f"LLM Error: {str(e)}")
        return None
    
    except Exception as e:
        error_msg = str(e)
        if "404" in error_msg or "NOT_FOUND" in error_msg:
            st.warning("🔄 Model temporarily unavailable. Please try again.")
        else:
            st.error(f"Unexpected error: {error_msg}")
        return None
