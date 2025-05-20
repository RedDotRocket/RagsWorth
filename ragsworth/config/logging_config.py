import os
import logging
import logging.config
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Define log levels mapping for easier configuration
LOG_LEVELS = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
}

class LoggingConfig:
    """Configuration for the application's logging system."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize logging configuration.
        
        Args:
            config: Optional configuration dictionary with logging settings.
                   If None, default settings will be used.
        """
        self.config = config or {}
        self._configure_logging()
    
    def _configure_logging(self) -> None:
        """Configure the logging system based on the provided or default configuration."""
        log_level = self.config.get("log_level", "info").lower()
        log_format = self.config.get(
            "log_format", 
            "%(asctime)s [%(levelname)s][%(name)s]: %(message)s (%(filename)s:%(lineno)d)"
        )
        log_file = self.config.get("log_file")
        
        # Create logs directory if logging to file is enabled
        if log_file:
            log_dir = os.path.dirname(log_file)
            if log_dir:
                Path(log_dir).mkdir(parents=True, exist_ok=True)
        
        # Configure logging dictionary
        logging_config = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "standard": {
                    "format": log_format,
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "level": LOG_LEVELS.get(log_level, logging.INFO),
                    "formatter": "standard",
                    "stream": sys.stdout,
                },
            },
            "loggers": {
                "ragsworth": {
                    "level": LOG_LEVELS.get(log_level, logging.INFO),
                    "handlers": ["console"],
                    "propagate": False,
                },
            },
            "root": {
                "level": logging.WARNING,
                "handlers": ["console"],
            }
        }
        
        # Add file handler if log file is specified
        if log_file:
            logging_config["handlers"]["file"] = {
                "class": "logging.handlers.RotatingFileHandler",
                "level": LOG_LEVELS.get(log_level, logging.INFO),
                "formatter": "standard",
                "filename": log_file,
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
            }
            logging_config["loggers"]["ragsworth"]["handlers"].append("file")
            logging_config["root"]["handlers"].append("file")
        
        # Apply configuration
        logging.config.dictConfig(logging_config)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for the specified name.
    
    Args:
        name: The name of the logger, usually the module name.
        
    Returns:
        A configured logger instance.
    """
    # Format the name to include the ragsworth prefix if not already there
    if not name.startswith("ragsworth."):
        name = f"ragsworth.{name}"
    
    return logging.getLogger(name) 