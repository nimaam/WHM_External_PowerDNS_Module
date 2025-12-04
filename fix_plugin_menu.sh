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

# Ensure directory exists
mkdir -p /usr/local/cpanel/whostmgr/docroot/addon_plugins

# Create/Update plugin registration
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

# Set correct permissions
chmod 644 /usr/local/cpanel/whostmgr/docroot/addon_plugins/ultahost_dns.json
chown root:root /usr/local/cpanel/whostmgr/docroot/addon_plugins/ultahost_dns.json

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

echo -e "${GREEN}Plugin registration fixed!${NC}"
echo -e "${YELLOW}Next steps:${NC}"
echo -e "1. Clear your browser cache"
echo -e "2. Log out and log back into WHM"
echo -e "3. The plugin should appear in: Plugins > Ultahost DNS"
echo -e ""
echo -e "If it still doesn't appear, try:"
echo -e "  /scripts/restartsrv_httpd"
echo -e "  /scripts/rebuildhttpdconf"

