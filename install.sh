#!/bin/bash
# Ultahost DNS Plugin Installation Script
# For WHM/cPanel 130.x.x

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

# Check if cPanel is installed
if [ ! -d "/usr/local/cpanel" ]; then
    echo -e "${RED}Error: cPanel/WHM is not installed on this system${NC}"
    exit 1
fi

echo -e "${GREEN}Installing Ultahost DNS Plugin...${NC}"

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Install Python package
echo -e "${YELLOW}Installing Python package...${NC}"
cd "$SCRIPT_DIR"
pip3 install -e . --quiet

# Create directories
echo -e "${YELLOW}Creating directories...${NC}"
mkdir -p /usr/local/cpanel/whostmgr/docroot/cgi/ultahost_dns
mkdir -p /usr/local/cpanel/whostmgr/docroot/addon_plugins
mkdir -p /usr/local/cpanel/base/frontend/paper_lantern/ultahost_dns
mkdir -p /usr/local/cpanel/scripts/ultahost_dns
mkdir -p /usr/local/cpanel/bin/ultahost_dns
mkdir -p /var/log/ultahost_dns
mkdir -p /var/cpanel

# Copy WHM interface
echo -e "${YELLOW}Installing WHM interface...${NC}"
cp -r "$SCRIPT_DIR/whm/cgi/"* /usr/local/cpanel/whostmgr/docroot/cgi/ultahost_dns/
chmod 755 /usr/local/cpanel/whostmgr/docroot/cgi/ultahost_dns/*.cgi

# Use simple interface as primary (more compatible)
if [ -f "/usr/local/cpanel/whostmgr/docroot/cgi/ultahost_dns/ultahost_dns_settings_simple.cgi" ]; then
    cp /usr/local/cpanel/whostmgr/docroot/cgi/ultahost_dns/ultahost_dns_settings_simple.cgi \
       /usr/local/cpanel/whostmgr/docroot/cgi/ultahost_dns/ultahost_dns_settings.cgi
fi

# Copy hook scripts
echo -e "${YELLOW}Installing hook scripts...${NC}"
cp -r "$SCRIPT_DIR/scripts/hooks/"* /usr/local/cpanel/scripts/ultahost_dns/
chmod 755 /usr/local/cpanel/scripts/ultahost_dns/*

# Copy utilities
echo -e "${YELLOW}Installing utilities...${NC}"
cp "$SCRIPT_DIR/scripts/test_connection.py" /usr/local/cpanel/bin/ultahost_dns/
chmod 755 /usr/local/cpanel/bin/ultahost_dns/*.py

# Create WHM plugin registration
echo -e "${YELLOW}Registering WHM plugin...${NC}"
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

# Register hooks using cPanel hook system
echo -e "${YELLOW}Registering DNS hooks...${NC}"

# Create hook registration JSON
cat > /tmp/ultahost_dns_hooks.json << 'HOOKS_EOF'
{
    "hooks": [
        {
            "hook": "Api2::Dns::create_zone",
            "category": "Whostmgr",
            "event": "post",
            "stage": "post",
            "exectype": "script",
            "script": "/usr/local/cpanel/scripts/ultahost_dns/dns_create_zone"
        },
        {
            "hook": "Api2::Dns::delete_zone",
            "category": "Whostmgr",
            "event": "post",
            "stage": "post",
            "exectype": "script",
            "script": "/usr/local/cpanel/scripts/ultahost_dns/dns_delete_zone"
        },
        {
            "hook": "Api2::Dns::add_record",
            "category": "Whostmgr",
            "event": "post",
            "stage": "post",
            "exectype": "script",
            "script": "/usr/local/cpanel/scripts/ultahost_dns/dns_add_record"
        },
        {
            "hook": "Api2::Dns::delete_record",
            "category": "Whostmgr",
            "event": "post",
            "stage": "post",
            "exectype": "script",
            "script": "/usr/local/cpanel/scripts/ultahost_dns/dns_delete_record"
        },
        {
            "hook": "Api2::Dns::edit_record",
            "category": "Whostmgr",
            "event": "post",
            "stage": "post",
            "exectype": "script",
            "script": "/usr/local/cpanel/scripts/ultahost_dns/dns_update_record"
        }
    ]
}
HOOKS_EOF

# Register hooks
if [ -f "/usr/local/cpanel/bin/manage_hooks" ]; then
    /usr/local/cpanel/bin/manage_hooks add file /tmp/ultahost_dns_hooks.json 2>/dev/null || {
        echo -e "${YELLOW}Note: Hook registration may need manual configuration${NC}"
        echo -e "${YELLOW}Hooks are installed at: /usr/local/cpanel/scripts/ultahost_dns/${NC}"
    }
    rm -f /tmp/ultahost_dns_hooks.json
else
    echo -e "${YELLOW}Warning: manage_hooks not found. Hooks may need manual registration.${NC}"
    echo -e "${YELLOW}Hook scripts are installed at: /usr/local/cpanel/scripts/ultahost_dns/${NC}"
fi

# Set permissions
echo -e "${YELLOW}Setting permissions...${NC}"
chown -R root:root /usr/local/cpanel/whostmgr/docroot/cgi/ultahost_dns
chown -R root:root /usr/local/cpanel/scripts/ultahost_dns
chown -R root:root /usr/local/cpanel/bin/ultahost_dns
chown -R root:root /var/log/ultahost_dns

# Create initial config if it doesn't exist
if [ ! -f "/var/cpanel/ultahost_dns_config.json" ]; then
    echo -e "${YELLOW}Creating initial configuration...${NC}"
    cat > /var/cpanel/ultahost_dns_config.json << 'EOF'
{
  "api_url": "",
  "api_key": "",
  "enabled": false
}
EOF
    chmod 600 /var/cpanel/ultahost_dns_config.json
fi

echo -e "${GREEN}Installation completed successfully!${NC}"
echo -e "${YELLOW}Next steps:${NC}"
echo -e "1. Log in to WHM as root"
echo -e "2. Navigate to Plugins > Ultahost DNS Settings"
echo -e "3. Configure your PowerDNS v4 API URL and API Key"
echo -e "4. Enable the plugin"
echo -e ""
echo -e "Logs are available at: /var/log/ultahost_dns/ultahost_dns.log"

