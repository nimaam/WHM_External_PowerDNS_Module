"""Tests for configuration management."""

import json
import tempfile
from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

from ultahost_dns.config import Config


class TestConfig:
    """Test configuration management."""

    def test_default_config(self):
        """Test default configuration values."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(Config, "CONFIG_FILE", Path(tmpdir) / "test_config.json"):
                config = Config.load()
                assert config["api_url"] == ""
                assert config["api_key"] == ""
                assert config["enabled"] is False

    def test_save_and_load(self):
        """Test saving and loading configuration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(Config, "CONFIG_FILE", Path(tmpdir) / "test_config.json"):
                test_config = {
                    "api_url": "https://dns.example.com:8081",
                    "api_key": "test-key-123",
                    "enabled": True,
                }
                assert Config.save(test_config) is True

                loaded_config = Config.load()
                assert loaded_config["api_url"] == test_config["api_url"]
                assert loaded_config["api_key"] == test_config["api_key"]
                assert loaded_config["enabled"] is test_config["enabled"]

    def test_get_api_url(self):
        """Test getting API URL."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(Config, "CONFIG_FILE", Path(tmpdir) / "test_config.json"):
                Config.save({"api_url": "https://test.example.com", "api_key": "", "enabled": False})
                assert Config.get_api_url() == "https://test.example.com"

    def test_get_api_key(self):
        """Test getting API key."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(Config, "CONFIG_FILE", Path(tmpdir) / "test_config.json"):
                Config.save({"api_url": "", "api_key": "secret-key", "enabled": False})
                assert Config.get_api_key() == "secret-key"

    def test_is_enabled(self):
        """Test enabled check."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(Config, "CONFIG_FILE", Path(tmpdir) / "test_config.json"):
                # Not enabled - missing URL
                Config.save({"api_url": "", "api_key": "key", "enabled": True})
                assert Config.is_enabled() is False

                # Not enabled - missing key
                Config.save({"api_url": "https://test.com", "api_key": "", "enabled": True})
                assert Config.is_enabled() is False

                # Not enabled - flag is False
                Config.save({"api_url": "https://test.com", "api_key": "key", "enabled": False})
                assert Config.is_enabled() is False

                # Enabled - all conditions met
                Config.save({"api_url": "https://test.com", "api_key": "key", "enabled": True})
                assert Config.is_enabled() is True

    def test_update(self):
        """Test updating configuration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(Config, "CONFIG_FILE", Path(tmpdir) / "test_config.json"):
                Config.save({"api_url": "", "api_key": "", "enabled": False})

                Config.update(api_url="https://new.com", enabled=True)
                config = Config.load()
                assert config["api_url"] == "https://new.com"
                assert config["enabled"] is True
                assert config["api_key"] == ""

