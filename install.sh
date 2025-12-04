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
cp -r "$SCRIPT_DIR/whm/cgi/"* /usr/local/cpanel/whostmgr/docroot/cgi/ultahost_dns/ 2>/dev/null || true

# Use the main settings CGI (not the simple one)
if [ -f "$SCRIPT_DIR/whm/cgi/ultahost_dns_settings.cgi" ]; then
    cp "$SCRIPT_DIR/whm/cgi/ultahost_dns_settings.cgi" /usr/local/cpanel/whostmgr/docroot/cgi/ultahost_dns/ultahost_dns_settings.cgi
    chmod 755 /usr/local/cpanel/whostmgr/docroot/cgi/ultahost_dns/ultahost_dns_settings.cgi
    chown root:root /usr/local/cpanel/whostmgr/docroot/cgi/ultahost_dns/ultahost_dns_settings.cgi
    echo -e "${GREEN}Main CGI script installed${NC}"
elif [ -f "/usr/local/cpanel/whostmgr/docroot/cgi/ultahost_dns/ultahost_dns_settings_simple.cgi" ]; then
    cp /usr/local/cpanel/whostmgr/docroot/cgi/ultahost_dns/ultahost_dns_settings_simple.cgi \
       /usr/local/cpanel/whostmgr/docroot/cgi/ultahost_dns/ultahost_dns_settings.cgi
    chmod 755 /usr/local/cpanel/whostmgr/docroot/cgi/ultahost_dns/ultahost_dns_settings.cgi
    chown root:root /usr/local/cpanel/whostmgr/docroot/cgi/ultahost_dns/ultahost_dns_settings.cgi
    echo -e "${GREEN}Using simple CGI script${NC}"
fi

# Ensure all CGI files have correct permissions
chmod 755 /usr/local/cpanel/whostmgr/docroot/cgi/ultahost_dns/*.cgi 2>/dev/null || true
chown root:root /usr/local/cpanel/whostmgr/docroot/cgi/ultahost_dns/*.cgi 2>/dev/null || true

# Copy hook scripts
echo -e "${YELLOW}Installing hook scripts...${NC}"
cp -r "$SCRIPT_DIR/scripts/hooks/"* /usr/local/cpanel/scripts/ultahost_dns/
chmod 755 /usr/local/cpanel/scripts/ultahost_dns/*

# Copy utilities
echo -e "${YELLOW}Installing utilities...${NC}"
cp "$SCRIPT_DIR/scripts/test_connection.py" /usr/local/cpanel/bin/ultahost_dns/
cp "$SCRIPT_DIR/scripts/sync_zones.py" /usr/local/cpanel/bin/ultahost_dns/ 2>/dev/null || true
cp "$SCRIPT_DIR/scripts/list_zones_api.py" /usr/local/cpanel/bin/ultahost_dns/ 2>/dev/null || true
cp "$SCRIPT_DIR/scripts/fetch_zone_api.py" /usr/local/cpanel/bin/ultahost_dns/ 2>/dev/null || true
chmod 755 /usr/local/cpanel/bin/ultahost_dns/*.py

# Install dnsadmin plugin (if Perl modules exist)
if [ -f "$SCRIPT_DIR/src/ultahost_dns/dnsadmin/Setup.pm" ]; then
    echo -e "${YELLOW}Installing dnsadmin plugin...${NC}"
    mkdir -p /usr/local/cpanel/Cpanel/Dnsadmin/Plugins
    cp "$SCRIPT_DIR/src/ultahost_dns/dnsadmin/"*.pm /usr/local/cpanel/Cpanel/Dnsadmin/Plugins/ 2>/dev/null || true
    echo -e "${GREEN}dnsadmin plugin installed${NC}"
fi

# Create WHM plugin registration
echo -e "${YELLOW}Registering WHM plugin...${NC}"

# Ensure /var/cpanel/apps is a directory, not a file
if [ -f "/var/cpanel/apps" ]; then
    echo -e "${YELLOW}Removing /var/cpanel/apps file and creating directory...${NC}"
    rm -f /var/cpanel/apps
    mkdir -p /var/cpanel/apps
fi

# Create .conf file for register_appconfig (both in cgi dir and apps dir)
# First, create in source location if it doesn't exist
if [ ! -f "$SCRIPT_DIR/var/cpanel/apps/ultahost_dns.conf" ]; then
    mkdir -p "$SCRIPT_DIR/var/cpanel/apps"
    cat > "$SCRIPT_DIR/var/cpanel/apps/ultahost_dns.conf" << 'EOF'
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
fi

# Copy to cgi directory (for reference)
cat > /usr/local/cpanel/whostmgr/docroot/cgi/ultahost_dns/ultahost_dns.conf << 'EOF'
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
chmod 644 /usr/local/cpanel/whostmgr/docroot/cgi/ultahost_dns/ultahost_dns.conf
chown root:root /usr/local/cpanel/whostmgr/docroot/cgi/ultahost_dns/ultahost_dns.conf

# Also create JSON file for compatibility
mkdir -p /usr/local/cpanel/whostmgr/docroot/addon_plugins
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
# The appconfig file should be in /var/cpanel/apps/ directory
if [ -f "/usr/local/cpanel/bin/register_appconfig" ]; then
    # Ensure /var/cpanel/apps/ exists
    mkdir -p /var/cpanel/apps
    chmod 755 /var/cpanel/apps
    
    # Copy conf file from source to /var/cpanel/apps/
    if [ -f "$SCRIPT_DIR/var/cpanel/apps/ultahost_dns.conf" ]; then
        cp "$SCRIPT_DIR/var/cpanel/apps/ultahost_dns.conf" /var/cpanel/apps/ultahost_dns.conf
    else
        # Create it if it doesn't exist in source
        cp /usr/local/cpanel/whostmgr/docroot/cgi/ultahost_dns/ultahost_dns.conf /var/cpanel/apps/ultahost_dns.conf
    fi
    
    chmod 600 /var/cpanel/apps/ultahost_dns.conf
    chown root:root /var/cpanel/apps/ultahost_dns.conf
    
    # Register from /var/cpanel/apps/ (this is the standard location)
    /usr/local/cpanel/bin/register_appconfig /var/cpanel/apps/ultahost_dns.conf
    echo -e "${GREEN}Plugin registered using register_appconfig${NC}"
    
    # Verify registration
    if /usr/local/cpanel/bin/show_appconfig 2>/dev/null | grep -q ultahost_dns; then
        echo -e "${GREEN}Plugin registration verified${NC}"
    else
        echo -e "${YELLOW}Warning: Plugin registration may need manual verification${NC}"
    fi
fi

# Clear plugins cache
if [ -f "/var/cpanel/pluginscache.yaml" ]; then
    rm -f /var/cpanel/pluginscache.yaml
    echo -e "${GREEN}Plugins cache cleared${NC}"
fi

# Register hooks using cPanel hook system
echo -e "${YELLOW}Registering DNS hooks...${NC}"

# Create hook registration JSON
# Using PRE hooks to intercept BEFORE default DNS operations
cat > /tmp/ultahost_dns_hooks.json << 'HOOKS_EOF'
{
    "hooks": [
        {
            "hook": "Api2::Dns::listzones",
            "category": "Whostmgr",
            "event": "pre",
            "stage": "pre",
            "exectype": "script",
            "script": "/usr/local/cpanel/scripts/ultahost_dns/dns_list_zones"
        },
        {
            "hook": "Api2::Dns::fetchzone",
            "category": "Whostmgr",
            "event": "pre",
            "stage": "pre",
            "exectype": "script",
            "script": "/usr/local/cpanel/scripts/ultahost_dns/dns_fetch_zone"
        },
        {
            "hook": "Api2::Dns::create_zone",
            "category": "Whostmgr",
            "event": "pre",
            "stage": "pre",
            "exectype": "script",
            "script": "/usr/local/cpanel/scripts/ultahost_dns/dns_create_zone"
        },
        {
            "hook": "Api2::Dns::delete_zone",
            "category": "Whostmgr",
            "event": "pre",
            "stage": "pre",
            "exectype": "script",
            "script": "/usr/local/cpanel/scripts/ultahost_dns/dns_delete_zone"
        },
        {
            "hook": "Api2::Dns::add_record",
            "category": "Whostmgr",
            "event": "pre",
            "stage": "pre",
            "exectype": "script",
            "script": "/usr/local/cpanel/scripts/ultahost_dns/dns_add_record"
        },
        {
            "hook": "Api2::Dns::delete_record",
            "category": "Whostmgr",
            "event": "pre",
            "stage": "pre",
            "exectype": "script",
            "script": "/usr/local/cpanel/scripts/ultahost_dns/dns_delete_record"
        },
        {
            "hook": "Api2::Dns::edit_record",
            "category": "Whostmgr",
            "event": "pre",
            "stage": "pre",
            "exectype": "script",
            "script": "/usr/local/cpanel/scripts/ultahost_dns/dns_update_record"
        }
    ]
}
HOOKS_EOF

# Register hooks individually using manage_hooks
if [ -f "/usr/local/cpanel/bin/manage_hooks" ]; then
    echo -e "${YELLOW}Registering DNS hooks individually...${NC}"
    
    # Register listzones hook
    /usr/local/cpanel/bin/manage_hooks add script /usr/local/cpanel/scripts/ultahost_dns/dns_list_zones \
        --category=Whostmgr --event=Api2::Dns::listzones --stage=pre 2>/dev/null || true
    
    # Register fetchzone hook
    /usr/local/cpanel/bin/manage_hooks add script /usr/local/cpanel/scripts/ultahost_dns/dns_fetch_zone \
        --category=Whostmgr --event=Api2::Dns::fetchzone --stage=pre 2>/dev/null || true
    
    # Register create_zone hook
    /usr/local/cpanel/bin/manage_hooks add script /usr/local/cpanel/scripts/ultahost_dns/dns_create_zone \
        --category=Whostmgr --event=Api2::Dns::create_zone --stage=pre 2>/dev/null || true
    
    # Register delete_zone hook
    /usr/local/cpanel/bin/manage_hooks add script /usr/local/cpanel/scripts/ultahost_dns/dns_delete_zone \
        --category=Whostmgr --event=Api2::Dns::delete_zone --stage=pre 2>/dev/null || true
    
    # Register add_record hook
    /usr/local/cpanel/bin/manage_hooks add script /usr/local/cpanel/scripts/ultahost_dns/dns_add_record \
        --category=Whostmgr --event=Api2::Dns::add_record --stage=pre 2>/dev/null || true
    
    # Register delete_record hook
    /usr/local/cpanel/bin/manage_hooks add script /usr/local/cpanel/scripts/ultahost_dns/dns_delete_record \
        --category=Whostmgr --event=Api2::Dns::delete_record --stage=pre 2>/dev/null || true
    
    # Register edit_record hook
    /usr/local/cpanel/bin/manage_hooks add script /usr/local/cpanel/scripts/ultahost_dns/dns_update_record \
        --category=Whostmgr --event=Api2::Dns::edit_record --stage=pre 2>/dev/null || true
    
    echo -e "${GREEN}Hooks registered${NC}"
    
    # Verify hooks
    if /usr/local/cpanel/bin/manage_hooks list 2>/dev/null | grep -q ultahost; then
        echo -e "${GREEN}Hook registration verified${NC}"
    else
        echo -e "${YELLOW}Warning: Hooks may not be visible in list. They should still work.${NC}"
    fi
    
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

# Restart cPanel service to refresh plugin list
echo -e "${YELLOW}Restarting cPanel service to refresh plugins...${NC}"
/scripts/restartsrv_cpsrvd > /dev/null 2>&1 || true

echo -e "${GREEN}Installation completed successfully!${NC}"
echo -e "${YELLOW}Next steps:${NC}"
echo -e "1. Wait a few seconds for cPanel service to restart"
echo -e "2. Clear your browser cache"
echo -e "3. Log out and log back into WHM"
echo -e "4. Navigate to Plugins > Ultahost DNS"
echo -e "5. Configure your PowerDNS v4 API URL and API Key"
echo -e "6. Enable the plugin"
echo -e ""
echo -e "If the menu still doesn't appear, run: sudo ./fix_plugin_menu.sh"
echo -e "Logs are available at: /var/log/ultahost_dns/ultahost_dns.log"

