#!/usr/bin/env python3
"""Sync zones from PowerDNS to cPanel local DNS."""

import sys
from pathlib import Path

# Add src to path
possible_paths = [
    Path(__file__).parent.parent / "src",
    Path("/usr/local/cpanel/bin/ultahost_dns"),
]

for path in possible_paths:
    if path.exists():
        sys.path.insert(0, str(path))
        break

from ultahost_dns.config import Config
from ultahost_dns.logger import PluginLogger
from ultahost_dns.powerdns_client import PowerDNSClient


def sync_zone_to_cpanel(zone_name: str, records: list) -> bool:
    """Sync a zone and its records to cPanel's local DNS."""
    import subprocess

    logger = PluginLogger.get_logger()

    # Remove trailing dot for cPanel
    zone_clean = zone_name.rstrip(".")

    try:
        # Use cPanel API to create zone if it doesn't exist
        # First check if zone exists
        result = subprocess.run(
            ["/usr/local/cpanel/bin/whmapi1", "listzones", "domain=" + zone_clean],
            capture_output=True,
            text=True,
            timeout=10,
        )

        zone_exists = zone_clean in result.stdout

        if not zone_exists:
            # Create zone using cPanel API
            logger.info(f"Creating zone {zone_clean} in cPanel local DNS")
            result = subprocess.run(
                [
                    "/usr/local/cpanel/bin/whmapi1",
                    "createzone",
                    "domain=" + zone_clean,
                    "username=root",
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode != 0:
                logger.error(f"Failed to create zone {zone_clean} in cPanel: {result.stderr}")
                return False

        # Add records to cPanel
        for record in records:
            name = record["name"].rstrip(".")
            record_type = record["type"]
            content = record["content"]
            ttl = record.get("ttl", 3600)

            # Skip NS and SOA records as they're managed by cPanel
            if record_type in ["NS", "SOA"]:
                continue

            # Handle MX records with priority
            if record_type == "MX" and " " in content:
                parts = content.split(" ", 1)
                priority = parts[0]
                content = parts[1]
            else:
                priority = "0"

            # Add record using cPanel API
            try:
                cmd = [
                    "/usr/local/cpanel/bin/whmapi1",
                    "addzonerecord",
                    "domain=" + zone_clean,
                    "name=" + name,
                    "type=" + record_type,
                    "address=" + content,
                    "ttl=" + str(ttl),
                ]

                if record_type == "MX":
                    cmd.append("priority=" + priority)

                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

                if result.returncode != 0:
                    logger.warning(f"Failed to add record {name} {record_type}: {result.stderr}")
                else:
                    logger.debug(f"Added record {name} {record_type} to cPanel")

            except Exception as e:
                logger.warning(f"Error adding record {name} {record_type}: {e}")

        return True

    except Exception as e:
        logger.error(f"Error syncing zone {zone_clean}: {e}")
        return False


def main():
    """Main sync function."""
    logger = PluginLogger.get_logger()

    if not Config.is_enabled():
        logger.error("Plugin is not enabled")
        print("ERROR: Plugin is not enabled. Please enable it in WHM plugin settings.")
        sys.exit(1)

    logger.info("Starting zone sync from PowerDNS to cPanel")

    client = PowerDNSClient()
    zones = client.list_zones()

    if not zones:
        logger.warning("No zones found in PowerDNS")
        print("No zones found in PowerDNS")
        sys.exit(0)

    print(f"Found {len(zones)} zones in PowerDNS")
    logger.info(f"Found {len(zones)} zones in PowerDNS")

    synced = 0
    failed = 0

    for zone in zones:
        zone_name = zone.get("name", "")
        if not zone_name:
            continue

        print(f"Syncing zone: {zone_name}")

        # Get zone details and records
        zone_details = client.get_zone(zone_name)
        if not zone_details:
            logger.warning(f"Could not get details for zone {zone_name}")
            failed += 1
            continue

        # Get records
        records = client.get_records(zone_name)

        # Sync to cPanel
        if sync_zone_to_cpanel(zone_name, records):
            synced += 1
            print(f"  ✓ Synced {zone_name}")
        else:
            failed += 1
            print(f"  ✗ Failed to sync {zone_name}")

    print(f"\nSync complete: {synced} synced, {failed} failed")
    logger.info(f"Zone sync complete: {synced} synced, {failed} failed")


if __name__ == "__main__":
    main()

