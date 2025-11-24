"""
Configuration management for JARVIS
"""
import os
import json
from pathlib import Path

# Default configuration
DEFAULT_CONFIG = {
    "language": "tr",  # "tr" for Turkish, "en" for English, "both" for both
    "tts": {
        "rate": 150,
        "volume": 0.9,
        "voice": None  # None for default
    },
    "weather": {
        "api_key": "",  # OpenWeatherMap API key
        "city": "Istanbul",
        "units": "metric"
    },
    "applications": {
        "notepad": "notepad.exe",
        "calculator": "calc.exe",
        "browser": "chrome.exe"
    },
    "llm": {
        "enabled": True,
        "api_url": "http://localhost:1234/v1/chat/completions",
        "model": "qwen3-4b-2507",
        "temperature": 0.7,
        "max_tokens": 200,
        "timeout": 10
    },
    "user": {
        "name": "Kutay",
        "preferences": {}
    },
    "conversation": {
        "max_history": 10,
        "save_history": False
    }
}

CONFIG_FILE = Path(__file__).parent.parent / "config.json"


class Config:
    """Configuration manager"""
    
    def __init__(self):
        self.config = self.load_config()
    
    def load_config(self):
        """Load configuration from file or create default"""
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    merged = DEFAULT_CONFIG.copy()
                    merged.update(config)
                    return merged
            except Exception as e:
                print(f"Error loading config: {e}")
                return DEFAULT_CONFIG.copy()
        else:
            self.save_config(DEFAULT_CONFIG.copy())
            return DEFAULT_CONFIG.copy()
    
    def save_config(self, config=None):
        """Save configuration to file"""
        if config is None:
            config = self.config
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get(self, key, default=None):
        """Get configuration value using dot notation (e.g., 'weather.api_key')"""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    def set(self, key, value):
        """Set configuration value using dot notation"""
        keys = key.split('.')
        config = self.config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
        self.save_config()


# Global config instance
config = Config()

