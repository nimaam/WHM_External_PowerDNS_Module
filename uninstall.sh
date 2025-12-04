#!/bin/bash
# Ultahost DNS Plugin Uninstallation Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Error: This script must be run as root${NC}"
    exit 1
fi

echo -e "${YELLOW}Uninstalling Ultahost DNS Plugin...${NC}"

# Remove directories
echo -e "${YELLOW}Removing plugin files...${NC}"
rm -rf /usr/local/cpanel/whostmgr/docroot/cgi/ultahost_dns
rm -rf /usr/local/cpanel/base/frontend/paper_lantern/ultahost_dns
rm -rf /usr/local/cpanel/scripts/ultahost_dns
rm -rf /usr/local/cpanel/bin/ultahost_dns
rm -f /usr/local/cpanel/whostmgr/docroot/addon_plugins/ultahost_dns.json

# Unregister hooks (if possible)
echo -e "${YELLOW}Unregistering hooks...${NC}"
# Note: cPanel doesn't have a direct unregister command, hooks will be ignored if files don't exist

# Remove Python package (optional - keep if other plugins use it)
read -p "Remove Python package? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    pip3 uninstall -y ultahost-dns 2>/dev/null || true
fi

# Keep or remove config/logs
read -p "Remove configuration and logs? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -f /var/cpanel/ultahost_dns_config.json
    rm -rf /var/log/ultahost_dns
fi

echo -e "${GREEN}Uninstallation completed!${NC}"


