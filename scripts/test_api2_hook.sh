#!/bin/bash
# Test if API2 hooks are being called

echo "=== Testing if hook is called when accessing API2 ==="

# Clear hook debug log
> /var/log/ultahost_dns/hook_debug.log

echo "Calling whmapi1 listzones..."
/usr/local/cpanel/bin/whmapi1 listzones 2>&1 | head -20

echo ""
echo "=== Checking if hook was called ==="
if [ -f "/var/log/ultahost_dns/hook_debug.log" ]; then
    echo "Hook debug log contents:"
    cat /var/log/ultahost_dns/hook_debug.log
else
    echo "Hook debug log not found - hook was NOT called"
fi

echo ""
echo "=== Checking main log ==="
tail -10 /var/log/ultahost_dns/ultahost_dns.log | grep -i "listzones\|hook called"

