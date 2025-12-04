"""Configuration management for Ultahost DNS plugin."""

import json
import os
from pathlib import Path


class Config:
    """Manage plugin configuration."""

    CONFIG_FILE = Path("/var/cpanel/ultahost_dns_config.json")
    DEFAULT_CONFIG = {
        "api_url": "",
        "api_key": "",
        "enabled": False,
    }

    @classmethod
    def load(cls):
        """Load configuration from file."""
        if not cls.CONFIG_FILE.exists():
            cls.save(cls.DEFAULT_CONFIG)
            return cls.DEFAULT_CONFIG.copy()

        try:
            with open(cls.CONFIG_FILE, "r", encoding="utf-8") as f:
                config = json.load(f)
                # Ensure all keys exist
                for key, value in cls.DEFAULT_CONFIG.items():
                    if key not in config:
                        config[key] = value
                return config
        except (json.JSONDecodeError, OSError) as e:
            # Return default config on error
            return cls.DEFAULT_CONFIG.copy()

    @classmethod
    def save(cls, config):
        """Save configuration to file."""
        try:
            cls.CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(cls.CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2)
            os.chmod(cls.CONFIG_FILE, 0o600)  # Secure permissions
            return True
        except OSError:
            return False

    @classmethod
    def get_api_url(cls):
        """Get PowerDNS API URL."""
        config = cls.load()
        return config.get("api_url", "")

    @classmethod
    def get_api_key(cls):
        """Get PowerDNS API key."""
        config = cls.load()
        return config.get("api_key", "")

    @classmethod
    def is_enabled(cls):
        """Check if plugin is enabled."""
        config = cls.load()
        return config.get("enabled", False) and bool(config.get("api_url")) and bool(config.get("api_key"))

    @classmethod
    def update(cls, api_url=None, api_key=None, enabled=None):
        """Update configuration."""
        config = cls.load()
        if api_url is not None:
            config["api_url"] = api_url.rstrip("/")
        if api_key is not None:
            config["api_key"] = api_key
        if enabled is not None:
            config["enabled"] = bool(enabled)
        return cls.save(config)


