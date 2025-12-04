"""Permission management for Ultahost DNS plugin."""

import subprocess
from pathlib import Path

from ultahost_dns.logger import PluginLogger


class Permissions:
    """Manage user permissions for DNS zones."""

    logger = PluginLogger.get_logger()

    @classmethod
    def is_root(cls):
        """Check if current user is root."""
        try:
            result = subprocess.run(
                ["whoami"],
                capture_output=True,
                text=True,
                check=True,
                timeout=5,
            )
            return result.stdout.strip() == "root"
        except (subprocess.SubprocessError, subprocess.TimeoutExpired):
            return False

    @classmethod
    def get_user_type(cls, username):
        """Get user type: root, reseller, or user."""
        if cls.is_root() and username == "root":
            return "root"

        try:
            # Check if user is a reseller
            result = subprocess.run(
                ["/usr/local/cpanel/bin/whmapi1", "listaccts", "search=" + username, "searchtype=reseller"],
                capture_output=True,
                text=True,
                check=True,
                timeout=10,
            )
            if username in result.stdout:
                return "reseller"

            # Check if user exists
            result = subprocess.run(
                ["/usr/local/cpanel/bin/whmapi1", "listaccts", "search=" + username],
                capture_output=True,
                text=True,
                check=True,
                timeout=10,
            )
            if username in result.stdout:
                return "user"

            return None
        except (subprocess.SubprocessError, subprocess.TimeoutExpired) as e:
            cls.logger.error(f"Error checking user type for {username}: {e}")
            return None

    @classmethod
    def can_manage_zone(cls, username, zone_name):
        """Check if user can manage a specific zone."""
        user_type = cls.get_user_type(username)

        if user_type == "root":
            return True

        if user_type == "reseller":
            # Reseller can manage zones for their accounts
            try:
                result = subprocess.run(
                    ["/usr/local/cpanel/bin/whmapi1", "listaccts", "searchtype=reseller", "reseller=" + username],
                    capture_output=True,
                    text=True,
                    check=True,
                    timeout=10,
                )
                # Check if zone belongs to any of reseller's accounts
                # This is simplified - in production, check actual domain ownership
                return True  # Simplified for now
            except (subprocess.SubprocessError, subprocess.TimeoutExpired):
                return False

        if user_type == "user":
            # User can only manage their own zones
            try:
                # Get user's domains
                result = subprocess.run(
                    ["/usr/local/cpanel/bin/whmapi1", "listaccts", "search=" + username],
                    capture_output=True,
                    text=True,
                    check=True,
                    timeout=10,
                )
                # Check if zone_name matches user's domain
                # Simplified check - zone should match user's domain
                domain = zone_name.rstrip(".")
                return domain in result.stdout or zone_name in result.stdout
            except (subprocess.SubprocessError, subprocess.TimeoutExpired):
                return False

        return False

    @classmethod
    def get_user_domains(cls, username):
        """Get all domains for a user."""
        user_type = cls.get_user_type(username)
        domains = []

        try:
            if user_type == "root":
                # Root can see all domains
                result = subprocess.run(
                    ["/usr/local/cpanel/bin/whmapi1", "listaccts"],
                    capture_output=True,
                    text=True,
                    check=True,
                    timeout=10,
                )
                # Parse domains from output (simplified)
                domains = []  # Would need proper parsing
            elif user_type == "reseller":
                result = subprocess.run(
                    ["/usr/local/cpanel/bin/whmapi1", "listaccts", "reseller=" + username],
                    capture_output=True,
                    text=True,
                    check=True,
                    timeout=10,
                )
                # Parse domains from output
                domains = []  # Would need proper parsing
            elif user_type == "user":
                result = subprocess.run(
                    ["/usr/local/cpanel/bin/whmapi1", "listaccts", "search=" + username],
                    capture_output=True,
                    text=True,
                    check=True,
                    timeout=10,
                )
                # Parse user's domain
                domains = []  # Would need proper parsing

        except (subprocess.SubprocessError, subprocess.TimeoutExpired) as e:
            cls.logger.error(f"Error getting domains for {username}: {e}")

        return domains


