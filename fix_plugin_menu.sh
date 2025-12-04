#!/bin/bash
# Fix WHM Plugin Menu Registration
# Run this script if the plugin menu doesn't appear in WHM

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Error: This script must be run as root${NC}"
    exit 1
fi

echo -e "${GREEN}Fixing WHM Plugin Menu Registration...${NC}"

# Ensure /var/cpanel/apps is a directory, not a file
if [ -f "/var/cpanel/apps" ]; then
    echo -e "${YELLOW}Removing /var/cpanel/apps file and creating directory...${NC}"
    rm -f /var/cpanel/apps
    mkdir -p /var/cpanel/apps
    chmod 755 /var/cpanel/apps
fi

# Ensure directories exist
mkdir -p /usr/local/cpanel/whostmgr/docroot/addon_plugins
mkdir -p /usr/local/cpanel/whostmgr/docroot/cgi/ultahost_dns

# Create .conf file for register_appconfig
cat > /usr/local/cpanel/whostmgr/docroot/cgi/ultahost_dns/ultahost_dns.conf << 'EOF'
name=Ultahost DNS
version=1.0.0
description=PowerDNS v4 API integration for WHM/cPanel DNS management
category=dns
url=/cgi/ultahost_dns/ultahost_dns_settings.cgi
requires_root=1
EOF
chmod 644 /usr/local/cpanel/whostmgr/docroot/cgi/ultahost_dns/ultahost_dns.conf
chown root:root /usr/local/cpanel/whostmgr/docroot/cgi/ultahost_dns/ultahost_dns.conf

# Also create JSON file for compatibility
cat > /usr/local/cpanel/whostmgr/docroot/addon_plugins/ultahost_dns.json << 'EOF'
{
    "name": "Ultahost DNS",
    "version": "1.0.0",
    "description": "PowerDNS v4 API integration for WHM/cPanel DNS management",
    "category": "dns",
    "url": "/cgi/ultahost_dns/ultahost_dns_settings.cgi",
    "requires_root": 1
}
EOF
chmod 644 /usr/local/cpanel/whostmgr/docroot/addon_plugins/ultahost_dns.json
chown root:root /usr/local/cpanel/whostmgr/docroot/addon_plugins/ultahost_dns.json

# Register plugin using register_appconfig
if [ -f "/usr/local/cpanel/bin/register_appconfig" ]; then
    echo -e "${YELLOW}Registering plugin with register_appconfig...${NC}"
    /usr/local/cpanel/bin/register_appconfig /usr/local/cpanel/whostmgr/docroot/cgi/ultahost_dns/ultahost_dns.conf
    echo -e "${GREEN}Plugin registered${NC}"
fi

# Verify CGI script exists
if [ ! -f "/usr/local/cpanel/whostmgr/docroot/cgi/ultahost_dns/ultahost_dns_settings.cgi" ]; then
    echo -e "${YELLOW}Warning: CGI script not found. Checking installation...${NC}"
    if [ -f "/usr/local/cpanel/whostmgr/docroot/cgi/ultahost_dns/ultahost_dns_settings_simple.cgi" ]; then
        cp /usr/local/cpanel/whostmgr/docroot/cgi/ultahost_dns/ultahost_dns_settings_simple.cgi \
           /usr/local/cpanel/whostmgr/docroot/cgi/ultahost_dns/ultahost_dns_settings.cgi
        chmod 755 /usr/local/cpanel/whostmgr/docroot/cgi/ultahost_dns/ultahost_dns_settings.cgi
        echo -e "${GREEN}CGI script created${NC}"
    else
        echo -e "${RED}Error: CGI scripts not found. Please run install.sh first.${NC}"
        exit 1
    fi
fi

# Clear plugins cache
if [ -f "/var/cpanel/pluginscache.yaml" ]; then
    echo -e "${YELLOW}Clearing plugins cache...${NC}"
    rm -f /var/cpanel/pluginscache.yaml
    echo -e "${GREEN}Plugins cache cleared${NC}"
fi

# Verify JSON syntax
if command -v python3 &> /dev/null; then
    python3 -m json.tool /usr/local/cpanel/whostmgr/docroot/addon_plugins/ultahost_dns.json > /dev/null
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Plugin registration JSON is valid${NC}"
    else
        echo -e "${RED}Error: Invalid JSON syntax${NC}"
        exit 1
    fi
fi

# Restart cPanel service
echo -e "${YELLOW}Restarting cPanel service...${NC}"
/scripts/restartsrv_cpsrvd > /dev/null 2>&1 || true

echo -e "${GREEN}Plugin registration fixed!${NC}"
echo -e "${YELLOW}Next steps:${NC}"
echo -e "1. Wait 10-15 seconds for cPanel service to restart"
echo -e "2. Clear your browser cache completely"
echo -e "3. Log out and log back into WHM"
echo -e "4. The plugin should appear in: Plugins > Ultahost DNS"
echo -e ""
echo -e "If it still doesn't appear, check:"
echo -e "  - File exists: ls -la /usr/local/cpanel/whostmgr/docroot/cgi/ultahost_dns/ultahost_dns.conf"
echo -e "  - Check logs: tail -f /usr/local/cpanel/logs/error_log"
echo -e "  - Verify registration: /usr/local/cpanel/bin/register_appconfig --list | grep ultahost"

