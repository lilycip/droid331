#!/usr/bin/env python3
"""
Example of creating and using a custom logger with the Droid agent.
"""
import os
import sys
import json
import time
import argparse
import logging
import datetime
from droid.core.agent import Agent
from droid.utils.logger import setup_logging

class ColoredFormatter(logging.Formatter):
    """Custom formatter with colored output."""
    
    COLORS = {
        'DEBUG': '\033[94m',  # Blue
        'INFO': '\033[92m',   # Green
        'WARNING': '\033[93m', # Yellow
        'ERROR': '\033[91m',   # Red
        'CRITICAL': '\033[91m\033[1m', # Bold Red
        'RESET': '\033[0m'    # Reset
    }
    
    def format(self, record):
        """Format the log record with colors."""
        log_message = super().format(record)
        level_name = record.levelname
        if level_name in self.COLORS:
            log_message = f"{self.COLORS[level_name]}{log_message}{self.COLORS['RESET']}"
        return log_message

class JSONFormatter(logging.Formatter):
    """Custom formatter that outputs logs as JSON."""
    
    def format(self, record):
        """Format the log record as JSON."""
        log_data = {
            'timestamp': datetime.datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'name': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'line': record.lineno
        }
        
        if hasattr(record, 'agent_id'):
            log_data['agent_id'] = record.agent_id
        
        if hasattr(record, 'task_id'):
            log_data['task_id'] = record.task_id
        
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)

class FileRotatingHandler(logging.Handler):
    """Custom handler that rotates log files based on size."""
    
    def __init__(self, filename, max_bytes=1024*1024, backup_count=5):
        """Initialize the handler."""
        super().__init__()
        self.filename = filename
        self.max_bytes = max_bytes
        self.backup_count = backup_count
        self.current_size = 0
        
        # Create the directory if it doesn't exist
        os.makedirs(os.path.dirname(self.filename), exist_ok=True)
        
        # Check if the file exists and get its size
        if os.path.exists(self.filename):
            self.current_size = os.path.getsize(self.filename)
    
    def emit(self, record):
        """Emit a log record."""
        msg = self.format(record)
        msg_bytes = (msg + '\n').encode('utf-8')
        
        # Check if we need to rotate
        if self.current_size + len(msg_bytes) > self.max_bytes:
            self._rotate()
        
        # Write to the file
        with open(self.filename, 'ab') as f:
            f.write(msg_bytes)
        
        self.current_size += len(msg_bytes)
    
    def _rotate(self):
        """Rotate the log files."""
        if self.backup_count > 0:
            # Remove the oldest log file if it exists
            if os.path.exists(f"{self.filename}.{self.backup_count}"):
                os.remove(f"{self.filename}.{self.backup_count}")
            
            # Rotate the existing backup files
            for i in range(self.backup_count - 1, 0, -1):
                src = f"{self.filename}.{i}"
                dst = f"{self.filename}.{i + 1}"
                if os.path.exists(src):
                    os.rename(src, dst)
            
            # Rename the current log file
            if os.path.exists(self.filename):
                os.rename(self.filename, f"{self.filename}.1")
        
        # Reset the current size
        self.current_size = 0

class CustomLogger:
    """Custom logger for the Droid agent."""
    
    def __init__(self, config=None):
        """Initialize the custom logger."""
        self.config = config or {}
        self.name = self.config.get("name", "Custom Logger")
        
        # Configure the logger
        self._configure_logger()
    
    def _configure_logger(self):
        """Configure the logger."""
        # Get configuration values
        log_level = self.config.get("level", "INFO")
        log_format = self.config.get("format", "standard")
        log_file = self.config.get("file", None)
        log_to_console = self.config.get("console", True)
        log_to_file = self.config.get("file_logging", False)
        log_file_max_bytes = self.config.get("file_max_bytes", 1024 * 1024)  # 1 MB
        log_file_backup_count = self.config.get("file_backup_count", 5)
        
        # Create the root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, log_level))
        
        # Remove existing handlers
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # Create formatters
        if log_format == "json":
            formatter = JSONFormatter()
        elif log_format == "colored":
            formatter = ColoredFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        else:
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        # Add console handler
        if log_to_console:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            root_logger.addHandler(console_handler)
        
        # Add file handler
        if log_to_file and log_file:
            file_handler = FileRotatingHandler(
                log_file,
                max_bytes=log_file_max_bytes,
                backup_count=log_file_backup_count
            )
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
        
        # Create a logger for this class
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Initialized {self.name}")
        self.logger.info(f"Log level: {log_level}")
        self.logger.info(f"Log format: {log_format}")
        if log_to_file and log_file:
            self.logger.info(f"Logging to file: {log_file}")

def setup_custom_logging(config=None):
    """Set up custom logging."""
    logger = CustomLogger(config)
    return logger

def main():
    """Run the agent with a custom logger."""
    parser = argparse.ArgumentParser(description="Run the Droid agent with a custom logger")
    parser.add_argument("--log-level", type=str, default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], help="Log level")
    parser.add_argument("--log-format", type=str, default="standard", choices=["standard", "colored", "json"], help="Log format")
    parser.add_argument("--log-file", type=str, help="Log file path")
    parser.add_argument("--no-console", action="store_true", help="Disable console logging")
    
    args = parser.parse_args()
    
    # Create the custom logger configuration
    logger_config = {
        "name": "Droid Custom Logger",
        "level": args.log_level,
        "format": args.log_format,
        "console": not args.no_console,
        "file_logging": args.log_file is not None,
        "file": args.log_file
    }
    
    # Set up the custom logger
    logger = setup_custom_logging(logger_config)
    
    # Create the agent
    agent = Agent()
    
    # Get the logger for this module
    module_logger = logging.getLogger(__name__)
    module_logger.info("Agent initialized with custom logger")
    
    # Log some example messages
    print("\nGenerating example log messages:")
    
    module_logger.debug("This is a debug message")
    module_logger.info("This is an info message")
    module_logger.warning("This is a warning message")
    module_logger.error("This is an error message")
    
    try:
        # Generate an exception
        result = 1 / 0
    except Exception as e:
        module_logger.exception("This is an exception message")
    
    # Log messages with extra attributes
    extra = {"agent_id": "agent-123", "task_id": "task-456"}
    module_logger.info("This is a message with extra attributes", extra=extra)
    
    # Log messages from different modules
    agent_logger = logging.getLogger("droid.core.agent")
    agent_logger.info("This is a message from the agent module")
    
    model_logger = logging.getLogger("droid.core.model_manager")
    model_logger.info("This is a message from the model manager module")
    
    # Simulate some activity
    print("\nSimulating agent activity:")
    
    for i in range(5):
        module_logger.info(f"Processing task {i+1}")
        time.sleep(0.5)
        
        if i == 2:
            module_logger.warning(f"Task {i+1} took longer than expected")
        else:
            module_logger.info(f"Task {i+1} completed successfully")
    
    module_logger.info("All tasks completed")

if __name__ == "__main__":
    main()