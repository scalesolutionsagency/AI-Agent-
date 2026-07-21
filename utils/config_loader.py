"""Configuration loader for YAML config files."""

import os
from pathlib import Path
from typing import Dict, Any
import yaml


class ConfigLoader:
    """Load and parse YAML configuration files."""
    
    @staticmethod
    def load(config_path: str = "config.yaml") -> Dict[str, Any]:
        """Load configuration from YAML file.
        
        Args:
            config_path: Path to YAML configuration file
            
        Returns:
            Configuration dictionary
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            yaml.YAMLError: If YAML parsing fails
        """
        config_file = Path(config_path)
        
        if not config_file.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f) or {}
        
        # Load environment variables
        ConfigLoader._apply_env_vars(config)
        
        return config
    
    @staticmethod
    def _apply_env_vars(config: Dict[str, Any]) -> None:
        """Replace placeholders with environment variables.
        
        Looks for values like ${VAR_NAME} and replaces with env var.
        
        Args:
            config: Configuration dictionary to update in-place
        """
        for key, value in config.items():
            if isinstance(value, dict):
                ConfigLoader._apply_env_vars(value)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        ConfigLoader._apply_env_vars(item)
            elif isinstance(value, str) and value.startswith("${') and value.endswith("}"):
                env_var = value[2:-1]
                config[key] = os.getenv(env_var, value)
