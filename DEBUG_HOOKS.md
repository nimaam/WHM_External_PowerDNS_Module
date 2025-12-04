# Debugging DNS Hooks

## Check if hooks are being called

1. **Check hook registration:**
   ```bash
   /usr/local/cpanel/bin/manage_hooks list | grep ultahost
   ```

2. **Check if hooks are being triggered:**
   ```bash
   # Add logging to see when hooks are called
   tail -f /var/log/ultahost_dns/ultahost_dns.log
   ```

3. **Test hooks manually:**
   ```bash
   # Test list zones
   /usr/local/cpanel/scripts/ultahost_dns/dns_list_zones
   
   # Test fetch zone
   /usr/local/cpanel/scripts/ultahost_dns/dns_fetch_zone example.com
   ```

## Check API2 calls

cPanel's DNS Zone Manager uses API2 calls. Check what API2 calls are being made:

```bash
# Check API2 DNS calls in cPanel logs
tail -f /usr/local/cpanel/logs/api2_log | grep -i dns
```

## Verify hook output format

API2 hooks need to output JSON in a specific format. The hooks now output:
- `status`: 1 for success, 0 for error
- `statusmsg`: Status message
- `data`: The actual data

## If hooks still don't work

PRE hooks for API2 might not work as expected. Alternative approaches:

1. **Use POST hooks and sync** - Keep local DNS in sync with PowerDNS
2. **Create custom API2 module** - More complex but gives full control
3. **Use DNS provider plugin** - cPanel's DNS provider system

