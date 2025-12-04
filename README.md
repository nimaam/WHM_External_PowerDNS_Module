# Ultahost DNS Plugin for WHM/cPanel

A WHM/cPanel plugin that replaces the default DNS module with PowerDNS v4 API integration.

## Features

- Complete DNS management through PowerDNS v4 API
- WHM settings interface for root configuration
- Permission-based access (Root/Reseller/User)
- Support for all DNS record types
- DNS template integration
- Comprehensive logging system
- Compatible with cPanel/WHM 130.x.x

## Installation

1. Clone this repository
2. Run the installation script:
   ```bash
   sudo ./install.sh
   ```

## Configuration

1. Log in to WHM as root
2. Navigate to "Plugins" > "Ultahost DNS Settings"
3. Configure:
   - PowerDNS v4 API URL
   - API Key for authentication

## Requirements

- cPanel/WHM 130.x.x
- Python 3.12+
- PowerDNS v4 API access
- Root access to WHM

## Structure

```
/usr/local/cpanel/whostmgr/docroot/cgi/ultahost_dns/  - WHM interface
/usr/local/cpanel/base/frontend/paper_lantern/ultahost_dns/  - cPanel interface
/usr/local/cpanel/scripts/ultahost_dns/  - Hook scripts
/usr/local/cpanel/bin/ultahost_dns/  - Utilities and API client
```

## License

Proprietary

