"""Logging system for Ultahost DNS plugin."""

import logging
import os
from datetime import datetime
from pathlib import Path


class PluginLogger:
    """Custom logger for the plugin."""

    LOG_DIR = Path("/var/log/ultahost_dns")
    LOG_FILE = LOG_DIR / "ultahost_dns.log"

    @classmethod
    def _setup_logger(cls):
        """Set up the logger."""
        cls.LOG_DIR.mkdir(parents=True, exist_ok=True)

        logger = logging.getLogger("ultahost_dns")
        logger.setLevel(logging.DEBUG)

        # Avoid duplicate handlers
        if logger.handlers:
            return logger

        # File handler
        file_handler = logging.FileHandler(cls.LOG_FILE)
        file_handler.setLevel(logging.DEBUG)

        # Console handler (for hook scripts)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # Formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        return logger

    @classmethod
    def get_logger(cls):
        """Get the logger instance."""
        return cls._setup_logger()

    @classmethod
    def log_error(cls, message, exc_info=None):
        """Log an error message."""
        logger = cls.get_logger()
        logger.error(message, exc_info=exc_info)

    @classmethod
    def log_info(cls, message):
        """Log an info message."""
        logger = cls.get_logger()
        logger.info(message)

    @classmethod
    def log_debug(cls, message):
        """Log a debug message."""
        logger = cls.get_logger()
        logger.debug(message)

    @classmethod
    def log_warning(cls, message):
        """Log a warning message."""
        logger = cls.get_logger()
        logger.warning(message)


