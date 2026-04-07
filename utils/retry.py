"""
Retry decorator and utilities for handling transient failures.
"""

import time
import functools
from typing import Callable, Any, Type, Tuple
from utils.logging_config import get_logger

logger = get_logger(__name__)


def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,)
) -> Callable:
    """
    Decorator for retrying functions with exponential backoff.
    
    Args:
        max_attempts: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        backoff: Multiplier for delay after each attempt
        exceptions: Tuple of exceptions to catch and retry on
        
    Returns:
        Decorated function with retry capability
        
    Example:
        @retry(max_attempts=3, delay=1.0, backoff=2.0, exceptions=(TimeoutError, IOError))
        def fetch_data():
            ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            attempt = 0
            current_delay = delay
            
            while attempt < max_attempts:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    attempt += 1
                    if attempt >= max_attempts:
                        logger.error(
                            f"Failed after {max_attempts} attempts for {func.__name__}: {str(e)}"
                        )
                        raise
                    
                    logger.warning(
                        f"Attempt {attempt}/{max_attempts} failed for {func.__name__}. "
                        f"Retrying in {current_delay}s... Error: {str(e)}"
                    )
                    time.sleep(current_delay)
                    current_delay *= backoff
            
            return None
        
        return wrapper
    return decorator
