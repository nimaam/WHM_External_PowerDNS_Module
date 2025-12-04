#!/bin/bash
# Check if DNS hooks are being called

echo "=== Checking Hook Registration ==="
/usr/local/cpanel/bin/manage_hooks list | grep -A 5 ultahost

echo ""
echo "=== Testing Hook Manually ==="
echo "Testing dns_list_zones:"
/usr/local/cpanel/scripts/ultahost_dns/dns_list_zones

echo ""
echo "=== Checking Recent Logs ==="
tail -20 /var/log/ultahost_dns/ultahost_dns.log

echo ""
echo "=== Testing API2 Call Directly ==="
echo "Testing API2::Dns::listzones via whmapi1:"
/usr/local/cpanel/bin/whmapi1 listzones 2>&1 | head -20

