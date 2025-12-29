"""Centralized logging configuration module."""

import logging
import logging.handlers
from pathlib import Path
from typing import Optional


class LoggerConfig:
    """Configuration for application logging."""
    
    LOG_DIR = Path(__file__).parent / "logs"
    LOG_FILE = LOG_DIR / "app.log"
    LOG_LEVEL = logging.INFO
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
    MAX_BYTES = 10 * 1024 * 1024  # 10 MB
    BACKUP_COUNT = 5


def setup_logger(name: str, level: Optional[int] = None) -> logging.Logger:
    """
    Set up a logger with console and file handlers.
    
    Args:
        name: Logger name (typically __name__)
        level: Logging level. If None, uses LoggerConfig.LOG_LEVEL
        
    Returns:
        Configured logger instance
    """
    # Create logs directory if it doesn't exist
    LoggerConfig.LOG_DIR.mkdir(exist_ok=True)
    
    # Get or create logger
    logger = logging.getLogger(name)
    logger.setLevel(level or LoggerConfig.LOG_LEVEL)
    
    # Avoid duplicate handlers if logger already configured
    if logger.hasHandlers():
        return logger
    
    # Create formatter
    formatter = logging.Formatter(
        LoggerConfig.LOG_FORMAT,
        datefmt=LoggerConfig.DATE_FORMAT
    )
    
    # Console Handler (INFO and above)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(LoggerConfig.LOG_LEVEL)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File Handler with rotation (all levels)
    file_handler = logging.handlers.RotatingFileHandler(
        LoggerConfig.LOG_FILE,
        maxBytes=LoggerConfig.MAX_BYTES,
        backupCount=LoggerConfig.BACKUP_COUNT
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a configured logger instance.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Logger instance
    """
    return setup_logger(name)
