#!/bin/bash
# Fix Plugin Registration - Update appconfig and refresh

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Error: This script must be run as root${NC}"
    exit 1
fi

echo -e "${GREEN}Fixing Plugin Registration...${NC}"

# Ensure /var/cpanel/apps exists
mkdir -p /var/cpanel/apps
chmod 755 /var/cpanel/apps

# Update appconfig file with correct format
cat > /var/cpanel/apps/ultahost_dns.conf << 'EOF'
name=ultahost_dns
service=whostmgr
user=root
url=/cgi/ultahost_dns/ultahost_dns_settings.cgi
acls=all
displayname=Ultahost DNS
description=PowerDNS v4 API integration for WHM/cPanel DNS management
entryurl=ultahost_dns/ultahost_dns_settings.cgi
target=_self
EOF

chmod 600 /var/cpanel/apps/ultahost_dns.conf
chown root:root /var/cpanel/apps/ultahost_dns.conf

# Re-register the plugin
echo -e "${YELLOW}Re-registering plugin...${NC}"
/usr/local/cpanel/bin/register_appconfig /var/cpanel/apps/ultahost_dns.conf

# Clear plugins cache
echo -e "${YELLOW}Clearing plugins cache...${NC}"
rm -f /var/cpanel/pluginscache.yaml

# Restart cPanel service
echo -e "${YELLOW}Restarting cPanel service...${NC}"
/scripts/restartsrv_cpsrvd > /dev/null 2>&1 || true

# Verify registration
echo -e "${YELLOW}Verifying registration...${NC}"
if /usr/local/cpanel/bin/show_appconfig 2>/dev/null | grep -A 5 "ultahost_dns" | grep -q "displayname: Ultahost DNS"; then
    echo -e "${GREEN}✓ Plugin is registered correctly${NC}"
else
    echo -e "${RED}✗ Plugin registration verification failed${NC}"
fi

echo -e "${GREEN}Done!${NC}"
echo -e "${YELLOW}Next steps:${NC}"
echo -e "1. Wait 10-15 seconds for cPanel to restart"
echo -e "2. Clear your browser cache completely"
echo -e "3. Log out and log back into WHM"
echo -e "4. Check Plugins menu - Ultahost DNS should appear"

