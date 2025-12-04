"""DNS template management for cPanel integration."""

import subprocess
from pathlib import Path

from ultahost_dns.logger import PluginLogger


class DNSTemplate:
    """Manage DNS templates from cPanel."""

    logger = PluginLogger.get_logger()
    TEMPLATE_DIR = Path("/var/cpanel/dns_templates")

    @classmethod
    def get_template_records(cls, template_name="default"):
        """Get DNS records from a cPanel DNS template."""
        template_file = cls.TEMPLATE_DIR / f"{template_name}.db"

        if not template_file.exists():
            cls.logger.warning(f"DNS template {template_name} not found, using default")
            return cls._get_default_records()

        records = []
        try:
            with open(template_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith(";") or line.startswith("$"):
                        continue

                    # Parse DNS record format
                    # Format: name TTL class type content
                    parts = line.split()
                    if len(parts) >= 5:
                        name = parts[0]
                        ttl = int(parts[1]) if parts[1].isdigit() else 3600
                        record_type = parts[3]
                        content = " ".join(parts[4:])

                        records.append(
                            {
                                "name": name,
                                "type": record_type,
                                "ttl": ttl,
                                "content": content,
                            }
                        )
        except OSError as e:
            cls.logger.error(f"Error reading DNS template {template_name}: {e}")
            return cls._get_default_records()

        return records

    @classmethod
    def _get_default_records(cls):
        """Get default DNS records."""
        return [
            {
                "name": "@",
                "type": "NS",
                "ttl": 3600,
                "content": "ns1.example.com.",
            },
            {
                "name": "@",
                "type": "NS",
                "ttl": 3600,
                "content": "ns2.example.com.",
            },
            {
                "name": "@",
                "type": "A",
                "ttl": 3600,
                "content": "0.0.0.0",
            },
            {
                "name": "www",
                "type": "A",
                "ttl": 3600,
                "content": "0.0.0.0",
            },
        ]

    @classmethod
    def apply_template_to_zone(cls, client, zone_name, template_name="default"):
        """Apply DNS template records to a zone."""
        records = cls.get_template_records(template_name)
        applied = 0

        for record in records:
            name = record["name"]
            if name == "@":
                name = zone_name.rstrip(".")

            priority = None
            content = record["content"]

            # Handle MX and SRV records with priority
            if record["type"] in ["MX", "SRV"] and " " in content:
                parts = content.split(" ", 1)
                if parts[0].isdigit():
                    priority = int(parts[0])
                    content = parts[1]

            if client.add_record(zone_name, name, record["type"], content, record["ttl"], priority):
                applied += 1
            else:
                cls.logger.warning(f"Failed to apply record {name} {record['type']} to zone {zone_name}")

        cls.logger.info(f"Applied {applied}/{len(records)} template records to zone {zone_name}")
        return applied == len(records)

