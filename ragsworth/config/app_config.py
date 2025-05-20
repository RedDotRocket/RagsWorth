import os
from typing import Dict, Optional
import yaml

from .logging_config import LoggingConfig

class AppConfig:
    """Configuration manager for the RagsWorth application."""

    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or os.getenv("RAGSWORTH_CONFIG", "config.yaml")
        self.config = self.load_config()
        
        # Initialize logging as early as possible
        self.init_logging()

    def load_config(self) -> Dict:
        """Load configuration from YAML file."""
        if os.path.exists(self.config_path):
            with open(self.config_path) as f:
                return yaml.safe_load(f)
        else:
            raise FileNotFoundError(f"Configuration file not found at {self.config_path}") 
            
    def init_logging(self) -> None:
        """Initialize logging system based on configuration."""
        # Start with logging config from the YAML file
        logging_config = self.config.get("logging", {})
        
        # Override with environment variables if present
        log_level = os.getenv("RAGSWORTH_LOG_LEVEL")
        log_file = os.getenv("RAGSWORTH_LOG_FILE")
        
        if log_level:
            logging_config["log_level"] = log_level
        
        if log_file:
            logging_config["log_file"] = log_file
            
        # Initialize logging
        LoggingConfig(logging_config) 