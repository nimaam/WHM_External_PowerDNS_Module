#!/usr/bin/env python3
"""Test PowerDNS API connection."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ultahost_dns.config import Config
from ultahost_dns.logger import PluginLogger
from ultahost_dns.powerdns_client import PowerDNSClient


def main():
    """Test connection to PowerDNS API."""
    logger = PluginLogger.get_logger()

    if not Config.is_enabled():
        print("ERROR: Plugin is not enabled or configuration is incomplete")
        sys.exit(1)

    api_url = Config.get_api_url()
    api_key = Config.get_api_key()

    if not api_url or not api_key:
        print("ERROR: API URL or API Key is not configured")
        sys.exit(1)

    print(f"Testing connection to PowerDNS API: {api_url}")
    logger.info("Testing PowerDNS API connection")

    client = PowerDNSClient()
    if client.test_connection():
        print("SUCCESS: Connection to PowerDNS API successful")
        logger.info("PowerDNS API connection test successful")
        sys.exit(0)
    else:
        print("ERROR: Failed to connect to PowerDNS API. Please check your settings.")
        logger.error("PowerDNS API connection test failed")
        sys.exit(1)


if __name__ == "__main__":
    main()


