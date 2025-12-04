#!/bin/bash
# Manually register DNS hooks

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Error: This script must be run as root${NC}"
    exit 1
fi

echo -e "${GREEN}Registering DNS hooks...${NC}"

# Register each hook individually
/usr/local/cpanel/bin/manage_hooks add script /usr/local/cpanel/scripts/ultahost_dns/dns_list_zones \
    --category=Whostmgr --event=Api2::Dns::listzones --stage=pre

/usr/local/cpanel/bin/manage_hooks add script /usr/local/cpanel/scripts/ultahost_dns/dns_fetch_zone \
    --category=Whostmgr --event=Api2::Dns::fetchzone --stage=pre

/usr/local/cpanel/bin/manage_hooks add script /usr/local/cpanel/scripts/ultahost_dns/dns_create_zone \
    --category=Whostmgr --event=Api2::Dns::create_zone --stage=pre

/usr/local/cpanel/bin/manage_hooks add script /usr/local/cpanel/scripts/ultahost_dns/dns_delete_zone \
    --category=Whostmgr --event=Api2::Dns::delete_zone --stage=pre

/usr/local/cpanel/bin/manage_hooks add script /usr/local/cpanel/scripts/ultahost_dns/dns_add_record \
    --category=Whostmgr --event=Api2::Dns::add_record --stage=pre

/usr/local/cpanel/bin/manage_hooks add script /usr/local/cpanel/scripts/ultahost_dns/dns_delete_record \
    --category=Whostmgr --event=Api2::Dns::delete_record --stage=pre

/usr/local/cpanel/bin/manage_hooks add script /usr/local/cpanel/scripts/ultahost_dns/dns_update_record \
    --category=Whostmgr --event=Api2::Dns::edit_record --stage=pre

echo -e "${GREEN}All hooks registered!${NC}"

# List registered hooks
echo -e "${YELLOW}Registered hooks:${NC}"
/usr/local/cpanel/bin/manage_hooks list | grep -A 2 ultahost || echo "No ultahost hooks found in list"

