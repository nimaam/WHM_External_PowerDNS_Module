# API2 Module Override Warning

## Important Notice

The plugin now attempts to override cPanel's default `Api2::Dns` module by placing a custom module at `/usr/local/cpanel/Cpanel/API2/Dns.pm`.

**This is an advanced and potentially risky approach** that may:
- Break cPanel's default DNS functionality
- Cause conflicts with other plugins
- Not work as expected in all cPanel versions
- Require manual restoration if something goes wrong

## How It Works

1. The install script backs up the original `Dns.pm` to `Dns.pm.orig`
2. Our custom module is placed at `/usr/local/cpanel/Cpanel/API2/Dns.pm`
3. The custom module checks if the plugin is enabled
4. If enabled, it uses PowerDNS API; otherwise, it tries to call the original module

## Restoration

If you need to restore the original DNS module:

```bash
# Restore from backup
cp /usr/local/cpanel/Cpanel/API2/Dns.pm.orig /usr/local/cpanel/Cpanel/API2/Dns.pm

# Or reinstall cPanel DNS module
/scripts/upcp --force
```

## Alternative Approach

If overriding the API2 module doesn't work or causes issues, consider:
1. Using the sync approach (sync PowerDNS zones to local DNS)
2. Using the dnsadmin plugin system (more complex but safer)
3. Using POST hooks to sync changes after they happen

## Testing

After installation, test thoroughly:
1. Check if DNS Zone Manager shows PowerDNS zones
2. Verify that creating/deleting zones works
3. Test record management
4. Check cPanel error logs for any issues

