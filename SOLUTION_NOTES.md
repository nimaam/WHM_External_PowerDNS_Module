# Why PowerDNS Zones Don't Appear in WHM DNS Zone Manager

## The Problem

PRE hooks for API2 might not be able to completely override the API response. Even if the hook runs and outputs JSON, cPanel's API2 system might:
1. Not call the hook for certain operations
2. Not use the hook's output to replace the response
3. Read zones directly from local DNS files instead of using API2

## Current Status

- ✅ Hooks are registered
- ✅ Config shows enabled: true
- ✅ Test connection works
- ✅ Hook works when called directly
- ❌ Zones don't appear in DNS Zone Manager
- ❌ whmapi1 listzones returns local DNS zones

## Solution Options

### Option 1: Verify Hook is Being Called

Run this on your server:
```bash
sudo ./scripts/test_api2_hook.sh
```

This will show if the hook is actually being called when accessing DNS Zone Manager.

### Option 2: Use Sync Approach (Temporary)

Until we can fully replace DNS, use the sync script:
```bash
sudo python3 /usr/local/cpanel/bin/ultahost_dns/sync_zones.py
```

This will sync PowerDNS zones to cPanel's local DNS so they appear in DNS Zone Manager.

### Option 3: Create Custom DNS Provider (Advanced)

Create a proper DNS provider plugin that cPanel can use. This requires:
- Custom API2 module
- DNS provider registration
- Full integration with cPanel's DNS system

### Option 4: Check Hook Output Mechanism

PRE hooks might need to write to a specific location or use a different mechanism. Check cPanel documentation for how PRE hooks should provide data to override API2 responses.

## Next Steps

1. Run `test_api2_hook.sh` to see if hooks are called
2. Check logs when accessing DNS Zone Manager
3. If hooks aren't called, we need a different approach
4. If hooks are called but output isn't used, we need to fix the output mechanism

