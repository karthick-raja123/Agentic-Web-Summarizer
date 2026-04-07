"""
Configuration Management - Load and validate environment variables
Production-grade environment handling with validation and defaults
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional

# ============================================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================================

def load_env_file():
    """Load .env file with fallback to .env.example"""
    env_path = Path(__file__).parent / ".env"
    env_example_path = Path(__file__).parent / ".env.example"
    
    if env_path.exists():
        load_dotenv(env_path, override=True)
    elif env_example_path.exists():
        load_dotenv(env_example_path, override=True)
    else:
        print("⚠️  Warning: No .env or .env.example file found")

# Load environment variables
load_env_file()

# ============================================================================
# CONFIGURATION CLASS
# ============================================================================

class Config:
    """Environment configuration with validation."""
    
    # ========================================================================
    # API KEYS (REQUIRED)
    # ========================================================================
    
    GOOGLE_API_KEY: Optional[str] = os.getenv("GOOGLE_API_KEY")
    SERPER_API_KEY: Optional[str] = os.getenv("SERPER_API_KEY")
    
    # ========================================================================
    # API CONFIGURATION
    # ========================================================================
    
    API_HOST: str = os.getenv("API_HOST", "127.0.0.1")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    API_ENVIRONMENT: str = os.getenv("API_ENVIRONMENT", "development")
    API_RELOAD: bool = os.getenv("API_RELOAD", "false").lower() == "true"
    
    # ========================================================================
    # REQUEST TIMEOUTS & RETRIES
    # ========================================================================
    
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "30"))
    SERPER_TIMEOUT: int = int(os.getenv("SERPER_TIMEOUT", "15"))
    SCRAPE_TIMEOUT: int = int(os.getenv("SCRAPE_TIMEOUT", "10"))
    RETRIES_MAX: int = int(os.getenv("RETRIES_MAX", "3"))
    RETRY_DELAY: float = float(os.getenv("RETRY_DELAY", "2.0"))
    
    # ========================================================================
    # CONTENT LIMITS
    # ========================================================================
    
    MAX_CONTENT_PER_URL: int = int(os.getenv("MAX_CONTENT_PER_URL", "10000"))
    MAX_TOTAL_CONTENT: int = int(os.getenv("MAX_TOTAL_CONTENT", "50000"))
    MAX_SEARCH_RESULTS: int = int(os.getenv("MAX_SEARCH_RESULTS", "10"))
    MAX_URLS_TO_SCRAPE: int = int(os.getenv("MAX_URLS_TO_SCRAPE", "5"))
    
    # ========================================================================
    # DEBUG & LOGGING
    # ========================================================================
    
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "logs/quickglance.log")
    
    # ========================================================================
    # FEATURE FLAGS
    # ========================================================================
    
    ENABLE_EVALUATION: bool = os.getenv("ENABLE_EVALUATION", "true").lower() == "true"
    ENABLE_FORMATTING: bool = os.getenv("ENABLE_FORMATTING", "true").lower() == "true"
    ENABLE_CACHING: bool = os.getenv("ENABLE_CACHING", "false").lower() == "true"
    ENABLE_AUDIO_OUTPUT: bool = os.getenv("ENABLE_AUDIO_OUTPUT", "false").lower() == "true"
    
    # ========================================================================
    # STREAMLIT
    # ========================================================================
    
    STREAMLIT_PORT: int = int(os.getenv("STREAMLIT_SERVER_PORT", "8501"))
    STREAMLIT_ADDRESS: str = os.getenv("STREAMLIT_SERVER_ADDRESS", "127.0.0.1")
    STREAMLIT_HEADLESS: bool = os.getenv("STREAMLIT_SERVER_HEADLESS", "false").lower() == "true"
    
    # ========================================================================
    # CORS
    # ========================================================================
    
    ALLOWED_ORIGINS: list = os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:8501,http://localhost:3000"
    ).split(",")
    
    @classmethod
    def validate(cls) -> tuple[bool, list]:
        """
        Validate critical configuration.
        
        Returns:
            (is_valid, list of errors)
        """
        errors = []
        
        # Check required API keys
        if not cls.GOOGLE_API_KEY or cls.GOOGLE_API_KEY.startswith("sk-"):
            errors.append("❌ GOOGLE_API_KEY is missing or not configured in .env")
        
        if not cls.SERPER_API_KEY or cls.SERPER_API_KEY.startswith("x"):
            errors.append("❌ SERPER_API_KEY is missing or not configured in .env")
        
        # Check timeouts are reasonable
        if cls.REQUEST_TIMEOUT <= 0:
            errors.append("❌ REQUEST_TIMEOUT must be > 0")
        
        # Check ports are valid
        if not (1 <= cls.API_PORT <= 65535):
            errors.append("❌ API_PORT must be between 1 and 65535")
        
        return len(errors) == 0, errors
    
    @classmethod
    def get_summary(cls) -> str:
        """Get configuration summary for debugging."""
        is_valid, errors = cls.validate()
        
        summary = "\n" + "=" * 70 + "\n"
        summary += "CONFIGURATION SUMMARY\n"
        summary += "=" * 70 + "\n"
        summary += f"Environment: {cls.API_ENVIRONMENT}\n"
        summary += f"Debug Mode: {cls.DEBUG}\n"
        summary += f"Log Level: {cls.LOG_LEVEL}\n"
        summary += f"API: {cls.API_HOST}:{cls.API_PORT}\n"
        summary += f"Timeouts: Request={cls.REQUEST_TIMEOUT}s, Serper={cls.SERPER_TIMEOUT}s, Scrape={cls.SCRAPE_TIMEOUT}s\n"
        summary += f"Content Limits: Per-URL={cls.MAX_CONTENT_PER_URL}, Total={cls.MAX_TOTAL_CONTENT}\n"
        summary += f"Features: Evaluation={cls.ENABLE_EVALUATION}, Formatting={cls.ENABLE_FORMATTING}\n"
        summary += f"API Keys Configured: GOOGLE={'✓' if cls.GOOGLE_API_KEY else '✗'}, SERPER={'✓' if cls.SERPER_API_KEY else '✗'}\n"
        summary += "=" * 70 + "\n"
        
        if errors:
            summary += "\n⚠️  CONFIGURATION ERRORS:\n"
            for error in errors:
                summary += f"  {error}\n"
            summary += "\n"
        else:
            summary += "✅ All configurations valid!\n\n"
        
        return summary


# ============================================================================
# STANDALONE VALIDATION (Call from any script)
# ============================================================================

if __name__ == "__main__":
    print(Config.get_summary())
    is_valid, errors = Config.validate()
    exit(0 if is_valid else 1)
