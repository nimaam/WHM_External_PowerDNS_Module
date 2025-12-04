"""PowerDNS v4 API client."""

import json
from typing import Any, Dict, List, Optional

import requests

from ultahost_dns.config import Config
from ultahost_dns.logger import PluginLogger


class PowerDNSClient:
    """Client for PowerDNS v4 API."""

    def __init__(self, api_url: Optional[str] = None, api_key: Optional[str] = None):
        """Initialize PowerDNS client."""
        self.api_url = api_url or Config.get_api_url()
        self.api_key = api_key or Config.get_api_key()
        self.logger = PluginLogger.get_logger()
        self.session = requests.Session()
        self.session.headers.update({"X-API-Key": self.api_key})

    def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make API request."""
        url = f"{self.api_url.rstrip('/')}/api/v1/servers/localhost{endpoint}"

        try:
            self.logger.debug(f"PowerDNS API {method} request: {url}")
            if data:
                self.logger.debug(f"Request data: {json.dumps(data, indent=2)}")

            response = self.session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                timeout=30,
            )

            response.raise_for_status()

            if response.content:
                return response.json()
            return {}

        except requests.exceptions.RequestException as e:
            self.logger.error(f"PowerDNS API error: {e}")
            if hasattr(e, "response") and e.response is not None:
                try:
                    error_detail = e.response.json()
                    self.logger.error(f"Error details: {json.dumps(error_detail, indent=2)}")
                except (ValueError, AttributeError):
                    self.logger.error(f"Error response: {e.response.text}")
            raise

    def create_zone(self, zone_name: str, kind: str = "Native", nameservers: Optional[List[str]] = None) -> bool:
        """Create a new DNS zone."""
        if not zone_name.endswith("."):
            zone_name += "."

        zone_data = {
            "name": zone_name,
            "kind": kind,
        }

        if nameservers:
            zone_data["nameservers"] = nameservers

        try:
            self._request("POST", "/zones", data=zone_data)
            self.logger.info(f"Zone created: {zone_name}")
            return True
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to create zone {zone_name}: {e}")
            return False

    def delete_zone(self, zone_name: str) -> bool:
        """Delete a DNS zone."""
        if not zone_name.endswith("."):
            zone_name += "."

        try:
            self._request("DELETE", f"/zones/{zone_name}")
            self.logger.info(f"Zone deleted: {zone_name}")
            return True
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to delete zone {zone_name}: {e}")
            return False

    def get_zone(self, zone_name: str) -> Optional[Dict[str, Any]]:
        """Get zone information."""
        if not zone_name.endswith("."):
            zone_name += "."

        try:
            return self._request("GET", f"/zones/{zone_name}")
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to get zone {zone_name}: {e}")
            return None

    def list_zones(self) -> List[Dict[str, Any]]:
        """List all zones."""
        try:
            response = self._request("GET", "/zones")
            return response.get("zones", [])
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to list zones: {e}")
            return []

    def add_record(
        self,
        zone_name: str,
        name: str,
        record_type: str,
        content: str,
        ttl: int = 3600,
        priority: Optional[int] = None,
    ) -> bool:
        """Add a DNS record to a zone."""
        if not zone_name.endswith("."):
            zone_name += "."

        if not name.endswith("."):
            name += "."

        # Ensure name is FQDN
        if not name.endswith(zone_name):
            name = f"{name}.{zone_name}" if name != zone_name else zone_name

        record_data = {
            "rrsets": [
                {
                    "name": name,
                    "type": record_type,
                    "ttl": ttl,
                    "changetype": "REPLACE",
                    "records": [
                        {
                            "content": content,
                            "disabled": False,
                        }
                    ],
                }
            ]
        }

        if priority is not None and record_type in ["MX", "SRV"]:
            record_data["rrsets"][0]["records"][0]["content"] = f"{priority} {content}"

        try:
            self._request("PATCH", f"/zones/{zone_name}", data=record_data)
            self.logger.info(f"Record added: {name} {record_type} {content} in {zone_name}")
            return True
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to add record {name} {record_type}: {e}")
            return False

    def delete_record(self, zone_name: str, name: str, record_type: str) -> bool:
        """Delete a DNS record from a zone."""
        if not zone_name.endswith("."):
            zone_name += "."

        if not name.endswith("."):
            name += "."

        if not name.endswith(zone_name):
            name = f"{name}.{zone_name}" if name != zone_name else zone_name

        record_data = {
            "rrsets": [
                {
                    "name": name,
                    "type": record_type,
                    "changetype": "DELETE",
                }
            ]
        }

        try:
            self._request("PATCH", f"/zones/{zone_name}", data=record_data)
            self.logger.info(f"Record deleted: {name} {record_type} from {zone_name}")
            return True
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to delete record {name} {record_type}: {e}")
            return False

    def update_record(
        self,
        zone_name: str,
        name: str,
        record_type: str,
        content: str,
        ttl: int = 3600,
        priority: Optional[int] = None,
    ) -> bool:
        """Update a DNS record in a zone."""
        return self.add_record(zone_name, name, record_type, content, ttl, priority)

    def get_records(self, zone_name: str) -> List[Dict[str, Any]]:
        """Get all records for a zone."""
        zone = self.get_zone(zone_name)
        if not zone:
            return []

        records = []
        for rrsets in zone.get("rrsets", []):
            for record in rrsets.get("records", []):
                records.append(
                    {
                        "name": rrsets["name"],
                        "type": rrsets["type"],
                        "ttl": rrsets.get("ttl", 3600),
                        "content": record.get("content", ""),
                        "disabled": record.get("disabled", False),
                    }
                )

        return records

    def test_connection(self) -> bool:
        """Test connection to PowerDNS API."""
        try:
            self._request("GET", "/servers/localhost")
            return True
        except requests.exceptions.RequestException:
            return False

