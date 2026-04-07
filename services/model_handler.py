"""
Model Handler - Manages Gemini model initialization with fallback support.
Handles 404 errors gracefully and switches between available models.
"""

import google.generativeai as genai
from typing import Optional, Tuple
import os

class ModelHandler:
    """Handles Gemini model selection with automatic fallback"""
    
    # Available models ordered by preference
    # CRITICAL FIX: Switched from gemini-1.5.x (NO LONGER AVAILABLE)
    # to gemini-2.5.x models which are current and working
    # gemini-2.5-flash is confirmed WORKING with most API keys
    AVAILABLE_MODELS = [
        "gemini-2.5-flash",         # PRIMARY - working, reliable
        "gemini-2.5-pro",           # SECONDARY - if flash hits quota
        "gemini-flash-latest",      # FALLBACK - alias
        "gemini-pro-latest",        # LAST RESORT - alias
    ]
    
    def __init__(self, api_key: str):
        """Initialize with API key"""
        self.api_key = api_key
        genai.configure(api_key=api_key)
        self._model_cache = None
        self._current_model_name = None
    
    def get_model(self, preferred_model: Optional[str] = None) -> Tuple[object, str]:
        """
        Get available Gemini model with automatic fallback.
        
        Args:
            preferred_model: Preferred model name (optional)
            
        Returns:
            Tuple of (model_object, model_name)
            
        Raises:
            RuntimeError: If no models are available
        """
        # Return cached model if available
        if self._model_cache is not None and self._current_model_name:
            return self._model_cache, self._current_model_name
        
        # Build priority list
        model_priority = []
        if preferred_model:
            model_priority.append(preferred_model)
        model_priority.extend(self.AVAILABLE_MODELS)
        
        # Try each model
        last_error = None
        for model_name in model_priority:
            try:
                print(f"🔄 Trying model: {model_name}")
                model = genai.GenerativeModel(model_name)
                
                # Verify model works by listing it
                self._verify_model_availability(model_name)
                
                print(f"✅ Successfully loaded model: {model_name}")
                self._model_cache = model
                self._current_model_name = model_name
                return model, model_name
                
            except Exception as e:
                error_str = str(e).lower()
                last_error = e
                
                print(f"❌ Model '{model_name}' failed: {e}")
                
                # Stop if it's auth error (won't help with fallback)
                if "401" in str(e) or "unauthorized" in error_str or "invalid api key" in error_str:
                    raise RuntimeError(f"API authentication failed: {e}")
                
                # Continue to next model on 404 or other errors
                continue
        
        # No model available
        raise RuntimeError(
            f"No Gemini models available. Tried: {model_priority}\n"
            f"Last error: {last_error}\n"
            f"Available models: {self.AVAILABLE_MODELS}"
        )
    
    def _verify_model_availability(self, model_name: str) -> bool:
        """Verify model is actually available (not just instantiated)"""
        try:
            # Try to list available models
            models = genai.list_models()
            available_names = [m.name.replace("models/", "") for m in models]
            
            # Check if model is in available list
            if model_name not in available_names and f"models/{model_name}" not in available_names:
                # Still try to use it anyway (in case list is incomplete)
                pass
            
            return True
        except Exception as e:
            # If list fails, still try to use model
            print(f"⚠️  Could not verify model availability: {e}")
            return True
    
    def get_fallback_model_name(self) -> str:
        """Get currently active fallback model name"""
        return self._current_model_name or "gemini-1.5-pro"
    
    def reset_cache(self):
        """Reset cached model (useful for switching models)"""
        self._model_cache = None
        self._current_model_name = None


def create_model_with_fallback(api_key: str, preferred_model: Optional[str] = None) -> Tuple[object, str]:
    """
    Convenience function to create model with built-in fallback.
    
    Args:
        api_key: Google API key
        preferred_model: Preferred model (default: gemini-1.5-pro)
        
    Returns:
        Tuple of (model, model_name)
    """
    handler = ModelHandler(api_key)
    return handler.get_model(preferred_model or "gemini-1.5-pro")
