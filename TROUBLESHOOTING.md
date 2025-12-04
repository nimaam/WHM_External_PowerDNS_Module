# Troubleshooting Guide

## Issue: Hooks show "plugin is disabled" but config shows enabled: true

### Check 1: Verify Config File Format

The config file might have `"enabled": true` as a string instead of boolean. Check:

```bash
cat /var/cpanel/ultahost_dns_config.json | python3 -m json.tool
```

If `enabled` is a string `"true"` instead of boolean `true`, the plugin will think it's disabled.

### Check 2: Test Hook Directly

```bash
# Test if hook can read config
python3 /usr/local/cpanel/scripts/ultahost_dns/dns_list_zones

# Check debug log
tail -20 /var/log/ultahost_dns/hook_debug.log
```

### Check 3: Verify Hook is Called

When you access DNS Zone Manager or run `whmapi1 listzones`, check:

```bash
# Watch logs in real-time
tail -f /var/log/ultahost_dns/ultahost_dns.log

# Then access DNS Zone Manager in WHM
# You should see "DNS listzones hook called" in the logs
```

### Check 4: API2 Hook Limitation

PRE hooks for API2 might not be able to completely override the response. If hooks are called but zones still don't appear, we may need to:

1. Use a custom API2 module (more complex)
2. Use DNS provider plugin system
3. Modify cPanel's DNS configuration directly

## Issue: Zones don't appear in DNS Zone Manager

### Solution 1: Verify Hook Output Format

The hook must output JSON in API2 format. Test:

```bash
python3 /usr/local/cpanel/scripts/ultahost_dns/dns_list_zones
```

Should output:
```json
{"status": 1, "statusmsg": "OK", "data": {"zones": [...]}}
```

### Solution 2: Check if Hook is Actually Called

```bash
# Add this to hook script temporarily
echo "HOOK CALLED" >> /tmp/hook_test.log

# Then access DNS Zone Manager
# Check if /tmp/hook_test.log has entries
```

### Solution 3: Alternative Approach

If PRE hooks don't work, we might need to:
- Create a custom DNS provider module
- Use cPanel's DNS provider plugin system
- Modify DNS configuration to point to PowerDNS

## Quick Fix: Re-enable Plugin

If config shows enabled but hooks think it's disabled:

```bash
# Edit config directly
python3 << 'EOF'
import json
with open('/var/cpanel/ultahost_dns_config.json', 'r') as f:
    config = json.load(f)
config['enabled'] = True  # Ensure it's boolean True, not string
with open('/var/cpanel/ultahost_dns_config.json', 'w') as f:
    json.dump(config, f, indent=2)
EOF

# Verify
cat /var/cpanel/ultahost_dns_config.json | python3 -m json.tool
```

