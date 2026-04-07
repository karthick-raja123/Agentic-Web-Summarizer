"""
Centralized logging configuration for the Visual Web Agent system.
Provides consistent logging across all modules.
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path


class LoggerSetup:
    """Configure and manage logging for the application."""
    
    _logger = None
    
    @staticmethod
    def setup_logger(name: str = "VisualWebAgent", log_level: str = "INFO") -> logging.Logger:
        """
        Setup logger with both file and console handlers.
        
        Args:
            name: Logger name
            log_level: Log level (INFO, ERROR, DEBUG, WARNING)
            
        Returns:
            Configured logger instance
        """
        if LoggerSetup._logger is not None:
            return LoggerSetup._logger
        
        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, log_level))
        
        # Create logs directory if it doesn't exist
        log_dir = Path(__file__).parent.parent / "logs"
        log_dir.mkdir(exist_ok=True)
        
        # Console Handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, log_level))
        console_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_format)
        
        # File Handler with rotation
        file_handler = RotatingFileHandler(
            log_dir / "app.log",
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)
        file_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(funcName)s:%(lineno)d] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_format)
        
        # Add handlers
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
        
        LoggerSetup._logger = logger
        return logger


def get_logger(name: str = "VisualWebAgent") -> logging.Logger:
    """Get logger instance."""
    return LoggerSetup.setup_logger(name)
