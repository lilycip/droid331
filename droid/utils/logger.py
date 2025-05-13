"""
Logging System - Configures and manages logging.
"""
import os
import logging
import logging.handlers
from typing import Dict, Any

def setup_logging(config: Dict[str, Any] = None):
    """
    Set up logging based on configuration.
    
    Args:
        config: Logging configuration
    """
    config = config or {}
    
    # Get logging configuration
    log_level = config.get("level", "INFO")
    log_file = config.get("file", "logs/droid.log")
    log_format = config.get("format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    log_date_format = config.get("date_format", "%Y-%m-%d %H:%M:%S")
    max_bytes = config.get("max_bytes", 10 * 1024 * 1024)  # 10 MB
    backup_count = config.get("backup_count", 5)
    
    # Create logs directory if it doesn't exist
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level))
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create formatter
    formatter = logging.Formatter(log_format, log_date_format)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Create file handler
    file_handler = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=max_bytes, backupCount=backup_count
    )
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    # Set specific logger levels
    for logger_name, logger_level in config.get("loggers", {}).items():
        logging.getLogger(logger_name).setLevel(getattr(logging, logger_level))
    
    logging.info(f"Logging initialized with level {log_level}")
    
    return root_logger