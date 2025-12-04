# Ultahost DNS Plugin - Project Summary

## Overview

This plugin replaces the default DNS module in WHM/cPanel with PowerDNS v4 API integration. It allows root, resellers, and users to manage DNS zones and records through your PowerDNS v4 server instead of the built-in BIND/PowerDNS module.

## Architecture

### Components

1. **PowerDNS v4 API Client** (`src/ultahost_dns/powerdns_client.py`)
   - Handles all communication with PowerDNS v4 API
   - Supports zone creation, deletion, and record management
   - Implements error handling and logging

2. **Configuration Management** (`src/ultahost_dns/config.py`)
   - Stores API URL and API key securely
   - Manages plugin enable/disable state
   - Configuration stored at `/var/cpanel/ultahost_dns_config.json`

3. **Permission System** (`src/ultahost_dns/permissions.py`)
   - Root: Full access to all DNS zones
   - Reseller: Access to zones for their accounts
   - User: Access only to their own zones

4. **DNS Template Integration** (`src/ultahost_dns/dns_template.py`)
   - Applies cPanel DNS templates when creating zones
   - Supports default and custom templates

5. **Logging System** (`src/ultahost_dns/logger.py`)
   - Comprehensive logging to `/var/log/ultahost_dns/ultahost_dns.log`
   - Debug, info, warning, and error levels

6. **Hook Scripts** (`scripts/hooks/`)
   - `dns_create_zone`: Intercepts zone creation
   - `dns_delete_zone`: Intercepts zone deletion
   - `dns_add_record`: Intercepts record addition
   - `dns_delete_record`: Intercepts record deletion
   - `dns_update_record`: Intercepts record updates

7. **WHM Interface** (`whm/cgi/ultahost_dns_settings.cgi`)
   - Root-only settings page
   - Configure API URL and API Key
   - Enable/disable plugin
   - Test connection

## Installation Locations

```
/usr/local/cpanel/whostmgr/docroot/cgi/ultahost_dns/     - WHM interface
/usr/local/cpanel/scripts/ultahost_dns/                  - Hook scripts
/usr/local/cpanel/bin/ultahost_dns/                       - Utilities
/var/cpanel/ultahost_dns_config.json                      - Configuration
/var/log/ultahost_dns/ultahost_dns.log                    - Logs
```

## How It Works

1. **Zone Creation**: When a domain is added in cPanel, the `dns_create_zone` hook is triggered. The plugin creates the zone in PowerDNS v4 and applies the DNS template.

2. **Record Management**: When users add, modify, or delete DNS records through cPanel, the corresponding hooks intercept these operations and apply them to PowerDNS v4 via API.

3. **Permission Checking**: Before any operation, the plugin verifies that the user has permission to manage the zone based on their role (root/reseller/user).

4. **Error Handling**: All operations are logged. If an API call fails, the error is logged and the operation may fail (depending on hook configuration).

## Hook Integration

The plugin uses cPanel's hook system to intercept DNS operations. Hooks are registered to run after DNS operations complete, ensuring compatibility with cPanel's workflow.

**Important Note**: The hook registration method may vary depending on your cPanel version. If automatic registration fails, you may need to manually register hooks using:

```bash
/usr/local/cpanel/bin/manage_hooks add file /path/to/hooks.json
```

## Testing

Run the test suite:
```bash
make test
```

Test API connection:
```bash
/usr/local/cpanel/bin/ultahost_dns/test_connection.py
```

## Security Considerations

1. Configuration file (`ultahost_dns_config.json`) has 600 permissions (root-only read/write)
2. API key is stored in plain text (consider encryption for production)
3. Hook scripts are executable only by root
4. WHM interface requires root access

## Limitations & Future Enhancements

### Current Limitations
- DNS templates are read from `/var/cpanel/dns_templates/` (may need adjustment)
- Permission checking is simplified (may need domain ownership verification)
- No DNSSEC support yet
- No zone transfer support yet

### Potential Enhancements
- DNSSEC management
- Zone transfer support
- API key encryption
- Webhook notifications
- Advanced permission granularity
- Multi-server support
- Zone import/export

## Troubleshooting

### Hooks Not Firing
1. Check if plugin is enabled: `cat /var/cpanel/ultahost_dns_config.json`
2. Verify hooks are registered: `/usr/local/cpanel/bin/manage_hooks list`
3. Check hook script permissions: `ls -la /usr/local/cpanel/scripts/ultahost_dns/`

### API Connection Issues
1. Test connection: `/usr/local/cpanel/bin/ultahost_dns/test_connection.py`
2. Check firewall rules
3. Verify API URL and key in configuration
4. Check PowerDNS server logs

### Permission Issues
1. Review logs: `tail -f /var/log/ultahost_dns/ultahost_dns.log`
2. Verify user type detection
3. Check domain ownership

## Development

### Code Style
- Follows Python 3.12+ standards
- Uses ruff for linting and formatting
- Line length: 100 characters
- Double quotes for strings

### Running Tests
```bash
pytest tests/ -v
```

### Linting
```bash
make lint
make format
```

## Support & Maintenance

- Logs: `/var/log/ultahost_dns/ultahost_dns.log`
- Configuration: `/var/cpanel/ultahost_dns_config.json`
- Version: 1.0.0
- Compatible with: cPanel/WHM 130.x.x

## License

Proprietary - All rights reserved

