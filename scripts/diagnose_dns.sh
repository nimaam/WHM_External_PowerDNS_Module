#!/bin/bash
# Diagnose DNS hook issues

echo "=== Checking Plugin Configuration ==="
if [ -f "/var/cpanel/ultahost_dns_config.json" ]; then
    echo "Config file exists:"
    cat /var/cpanel/ultahost_dns_config.json | python3 -m json.tool
else
    echo "ERROR: Config file not found!"
fi

echo ""
echo "=== Testing PowerDNS Connection ==="
python3 /usr/local/cpanel/bin/ultahost_dns/test_connection.py

echo ""
echo "=== Testing List Zones ==="
python3 /usr/local/cpanel/scripts/ultahost_dns/dns_list_zones

echo ""
echo "=== Checking Hook Registration ==="
/usr/local/cpanel/bin/manage_hooks list | grep -A 10 ultahost

echo ""
echo "=== Testing API2 Call via whmapi1 ==="
echo "This should trigger the hook if it's working:"
/usr/local/cpanel/bin/whmapi1 listzones 2>&1 | head -30

echo ""
echo "=== Recent Log Entries ==="
tail -30 /var/log/ultahost_dns/ultahost_dns.log

echo ""
echo "=== Checking if hooks are executable ==="
ls -la /usr/local/cpanel/scripts/ultahost_dns/

