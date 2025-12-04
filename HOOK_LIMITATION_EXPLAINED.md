# Why PRE Hooks Don't Override API2 Responses

## The Problem

Your hook (`dns_list_zones`) **is being called** (we can see it in the logs), but cPanel's API2 system **is not using the hook's output** to replace the response.

When you run `whmapi1 listzones`, it still returns local DNS zones instead of PowerDNS zones, even though:
- ✅ The hook is registered correctly
- ✅ The hook is being called
- ✅ The hook outputs valid JSON
- ✅ The hook exits with code 0

## Why This Happens

PRE hooks for API2 in cPanel have limitations:

1. **PRE hooks can modify parameters** but may not be able to completely override the API response
2. **cPanel's DNS Zone Manager** might read zones directly from local DNS files, bypassing API2 entirely
3. **API2 system** might not read stdout from PRE hook scripts to replace responses

## Solutions

### Solution 1: Use Sync Approach (Recommended for Now)

Instead of trying to override API2, sync PowerDNS zones to cPanel's local DNS:

```bash
# Run sync script
sudo python3 /usr/local/cpanel/bin/ultahost_dns/sync_zones.py

# Or use the WHM interface
# Navigate to: WHM > Plugins > Ultahost DNS > Sync Zones
```

This way:
- PowerDNS remains the source of truth
- Zones appear in DNS Zone Manager
- Changes made in WHM sync back to PowerDNS via hooks

### Solution 2: Override API2 Module (Advanced - Current Attempt)

We're trying to override `/usr/local/cpanel/Cpanel/API2/Dns.pm` directly. This is risky but might work.

**To test:**
1. Reinstall the plugin (it will install the override)
2. Restart cPanel services: `/scripts/restartsrv_cpsrvd`
3. Test: `whmapi1 listzones`

**If it breaks:**
```bash
# Restore original
cp /usr/local/cpanel/Cpanel/API2/Dns.pm.orig /usr/local/cpanel/Cpanel/API2/Dns.pm
/scripts/restartsrv_cpsrvd
```

### Solution 3: Use DNS Provider Plugin (Most Robust)

Create a proper DNS provider plugin using cPanel's `dnsadmin` system. This requires:
- `Cpanel::Dnsadmin::Plugins::*` modules
- Proper registration in cPanel
- More complex but officially supported

We have started this with `src/ultahost_dns/dnsadmin/Setup.pm` and `Remote.pm`, but it needs more work.

## Current Status

- ✅ Hooks are registered and called
- ✅ Hook outputs correct format
- ❌ Hook output is not used by API2
- ⚠️ API2 module override attempted (needs testing)

## Next Steps

1. **Test the API2 module override** after reinstalling
2. **If that doesn't work**, use the sync approach as a workaround
3. **Long-term**: Complete the dnsadmin plugin implementation

