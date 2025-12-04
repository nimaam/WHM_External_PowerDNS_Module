#!/bin/bash
# Debug CGI Script Issues

echo "=== Checking CGI Script ==="
echo ""

# Check if CGI script exists
if [ -f "/usr/local/cpanel/whostmgr/docroot/cgi/ultahost_dns/ultahost_dns_settings.cgi" ]; then
    echo "✓ CGI script exists"
    ls -la /usr/local/cpanel/whostmgr/docroot/cgi/ultahost_dns/ultahost_dns_settings.cgi
else
    echo "✗ CGI script NOT found"
fi

echo ""
echo "=== Checking Perl Syntax ==="
perl -c /usr/local/cpanel/whostmgr/docroot/cgi/ultahost_dns/ultahost_dns_settings.cgi 2>&1

echo ""
echo "=== Checking AppConfig Registration ==="
/usr/local/cpanel/bin/show_appconfig | grep -A 10 ultahost || echo "Plugin not registered"

echo ""
echo "=== Checking /var/cpanel/apps/ ==="
ls -la /var/cpanel/apps/ | grep ultahost || echo "No appconfig file in /var/cpanel/apps/"

echo ""
echo "=== Checking Error Logs ==="
tail -20 /usr/local/cpanel/logs/error_log | grep -i ultahost || echo "No ultahost errors in recent logs"

echo ""
echo "=== Testing CGI Script Directly ==="
cd /usr/local/cpanel/whostmgr/docroot/cgi/ultahost_dns/
REMOTE_USER=root perl ultahost_dns_settings.cgi 2>&1 | head -20


