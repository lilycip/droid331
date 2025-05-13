"""
Configuration Manager - Handles loading and managing configuration.
"""
import os
import json
import yaml
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class ConfigManager:
    """
    Manages configuration loading and access.
    """
    
    def __init__(self, config_path: str = None):
        """
        Initialize the ConfigManager.
        
        Args:
            config_path: Path to the configuration file
        """
        self.config_path = config_path or os.environ.get("DROID_CONFIG", "config/config.yaml")
        self.config = {}
        
        # Load configuration
        self._load_config()
        
        logger.info(f"ConfigManager initialized with config from {self.config_path}")
    
    def _load_config(self):
        """Load configuration from file."""
        if not os.path.exists(self.config_path):
            logger.warning(f"Configuration file not found: {self.config_path}")
            self._create_default_config()
            return
            
        try:
            file_ext = os.path.splitext(self.config_path)[1].lower()
            
            if file_ext in ['.yaml', '.yml']:
                with open(self.config_path, 'r') as f:
                    self.config = yaml.safe_load(f)
            elif file_ext == '.json':
                with open(self.config_path, 'r') as f:
                    self.config = json.load(f)
            else:
                logger.error(f"Unsupported configuration file format: {file_ext}")
                self._create_default_config()
                
            logger.info(f"Loaded configuration from {self.config_path}")
        except Exception as e:
            logger.error(f"Failed to load configuration: {str(e)}")
            self._create_default_config()
    
    def _create_default_config(self):
        """Create a default configuration."""
        self.config = {
            "agent": {
                "name": "Droid",
                "version": "0.1.0"
            },
            "models": {
                "llama-3.1": {
                    "type": "llm",
                    "path": "models/llama-3.1",
                    "preload": True,
                    "config": {
                        "max_tokens": 2048,
                        "temperature": 0.7
                    }
                },
                "stable-diffusion-2.1": {
                    "type": "diffusion",
                    "path": "models/stable-diffusion-2.1",
                    "preload": False,
                    "config": {
                        "guidance_scale": 7.5
                    }
                },
                "stable-diffusion-xl": {
                    "type": "diffusion",
                    "path": "models/stable-diffusion-xl",
                    "preload": False,
                    "config": {
                        "guidance_scale": 7.5
                    }
                }
            },
            "modules": {
                "social_media": {
                    "enabled": True,
                    "platforms": ["twitter", "instagram", "facebook"]
                },
                "content_generator": {
                    "enabled": True,
                    "default_model": "llama-3.1"
                },
                "image_generator": {
                    "enabled": True,
                    "default_model": "stable-diffusion-xl"
                },
                "meme_generator": {
                    "enabled": True,
                    "templates_path": "data/meme_templates"
                }
            },
            "memory": {
                "path": "data/memory",
                "short_term_limit": 1000
            },
            "logging": {
                "level": "INFO",
                "file": "logs/droid.log"
            }
        }
        
        # Create the config directory if it doesn't exist
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        
        # Save the default configuration
        try:
            file_ext = os.path.splitext(self.config_path)[1].lower()
            
            if file_ext in ['.yaml', '.yml']:
                with open(self.config_path, 'w') as f:
                    yaml.dump(self.config, f, default_flow_style=False)
            elif file_ext == '.json':
                with open(self.config_path, 'w') as f:
                    json.dump(self.config, f, indent=2)
            else:
                # Default to YAML
                config_path = os.path.splitext(self.config_path)[0] + '.yaml'
                with open(config_path, 'w') as f:
                    yaml.dump(self.config, f, default_flow_style=False)
                self.config_path = config_path
                
            logger.info(f"Created default configuration at {self.config_path}")
        except Exception as e:
            logger.error(f"Failed to create default configuration: {str(e)}")
    
    def get_config(self) -> Dict[str, Any]:
        """
        Get the full configuration.
        
        Returns:
            The configuration dictionary
        """
        return self.config
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value by key.
        
        Args:
            key: Configuration key (dot notation supported)
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
                
        return value
    
    def set(self, key: str, value: Any) -> bool:
        """
        Set a configuration value.
        
        Args:
            key: Configuration key (dot notation supported)
            value: Value to set
            
        Returns:
            True if successful, False otherwise
        """
        keys = key.split('.')
        config = self.config
        
        # Navigate to the nested dictionary
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
            
        # Set the value
        config[keys[-1]] = value
        
        # Save the updated configuration
        try:
            file_ext = os.path.splitext(self.config_path)[1].lower()
            
            if file_ext in ['.yaml', '.yml']:
                with open(self.config_path, 'w') as f:
                    yaml.dump(self.config, f, default_flow_style=False)
            elif file_ext == '.json':
                with open(self.config_path, 'w') as f:
                    json.dump(self.config, f, indent=2)
            else:
                logger.error(f"Unsupported configuration file format: {file_ext}")
                return False
                
            logger.info(f"Updated configuration value: {key}")
            return True
        except Exception as e:
            logger.error(f"Failed to update configuration: {str(e)}")
            return False