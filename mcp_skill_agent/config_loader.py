import os
import yaml
from typing import Dict, Any, Optional

class ConfigManager:
    """
    Infrastructure Component: Configuration Loader.
    Loads `config.yaml` and provides access to settings.
    """
    _instance = None
    _config: Dict[str, Any] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._load_config()
        return cls._instance

    def _load_config(self):
        """Loads config.yaml from the same directory as this file."""
        base_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(base_dir, "config.yaml")
        
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                self._config = yaml.safe_load(f) or {}
        else:
            print(f"WARNING: config.yaml not found at {config_path}")
            self._config = {}

    @property
    def config(self) -> Dict[str, Any]:
        return self._config

    def get(self, key: str, default: Any = None) -> Any:
        """Get a value from the config using dot notation (e.g. 'openai.default_model')."""
        keys = key.split(".")
        value = self._config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default

# Global instance for easy access
config = ConfigManager()
