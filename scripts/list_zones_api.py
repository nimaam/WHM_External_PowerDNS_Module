#!/usr/bin/env python3
"""List zones API - returns simple list for dnsadmin plugin."""

import sys
from pathlib import Path

possible_paths = [
    Path(__file__).parent.parent / "src",
    Path("/usr/local/cpanel/bin/ultahost_dns"),
]

for path in possible_paths:
    if path.exists():
        sys.path.insert(0, str(path))
        break

try:
    from ultahost_dns.config import Config
    from ultahost_dns.powerdns_client import PowerDNSClient
except ImportError:
    sys.exit(1)

if not Config.is_enabled():
    sys.exit(1)

client = PowerDNSClient()
zones = client.list_zones()

for zone in zones:
    zone_name = zone.get("name", "").rstrip(".")
    if zone_name:
        print(zone_name)

