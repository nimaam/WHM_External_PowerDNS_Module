#!/usr/bin/env python3
"""Fix configuration file to ensure proper boolean values."""

import json
import sys
from pathlib import Path

CONFIG_FILE = Path("/var/cpanel/ultahost_dns_config.json")

if not CONFIG_FILE.exists():
    print(f"ERROR: Config file not found: {CONFIG_FILE}")
    sys.exit(1)

# Load config
with open(CONFIG_FILE, "r") as f:
    config = json.load(f)

print("Current config:")
print(json.dumps(config, indent=2))

# Fix boolean values
fixed = False
if isinstance(config.get("enabled"), str):
    config["enabled"] = config["enabled"].lower() in ("true", "1", "yes", "on")
    fixed = True
    print(f"\nFixed enabled from string to boolean: {config['enabled']}")

# Ensure api_url doesn't have trailing slash (we handle that in code)
if config.get("api_url") and config["api_url"].endswith("/"):
    config["api_url"] = config["api_url"].rstrip("/")
    fixed = True
    print(f"\nRemoved trailing slash from api_url")

# Save if fixed
if fixed:
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)
    import os
    os.chmod(CONFIG_FILE, 0o600)
    print("\nConfig file updated!")
else:
    print("\nConfig file is already correct.")

print("\nFinal config:")
print(json.dumps(config, indent=2))

# Verify
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from ultahost_dns.config import Config

is_enabled = Config.is_enabled()
print(f"\nPlugin enabled check: {is_enabled}")

