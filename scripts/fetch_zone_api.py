#!/usr/bin/env python3
"""Fetch zone API - returns zone data for dnsadmin plugin."""

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

if len(sys.argv) < 2:
    sys.exit(1)

zone_name = sys.argv[1]
client = PowerDNSClient()
records = client.get_records(zone_name)

for record in records:
    name = record["name"].rstrip(".")
    ttl = record.get("ttl", 3600)
    record_type = record["type"]
    content = record["content"]

    if name == zone_name.rstrip("."):
        name = "@"

    print(f"{name}\t{ttl}\tIN\t{record_type}\t{content}")

