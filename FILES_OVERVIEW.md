# Files Overview

## Project Structure

```
Ultahost-DNS/
├── src/ultahost_dns/          # Core Python package
│   ├── __init__.py            # Package initialization
│   ├── config.py              # Configuration management
│   ├── logger.py              # Logging system
│   ├── permissions.py         # Permission management
│   ├── powerdns_client.py     # PowerDNS v4 API client
│   └── dns_template.py        # DNS template integration
│
├── scripts/                   # Executable scripts
│   ├── hooks/                 # cPanel hook scripts
│   │   ├── dns_create_zone    # Zone creation hook
│   │   ├── dns_delete_zone    # Zone deletion hook
│   │   ├── dns_add_record     # Record addition hook
│   │   ├── dns_delete_record  # Record deletion hook
│   │   └── dns_update_record  # Record update hook
│   └── test_connection.py     # Connection test utility
│
├── whm/                       # WHM interface
│   ├── cgi/                   # CGI scripts
│   │   ├── ultahost_dns_settings.cgi          # Main settings (advanced)
│   │   └── ultahost_dns_settings_simple.cgi   # Simple settings (recommended)
│   └── templates/             # WHM templates
│       └── ultahost_dns_settings.tmpl
│
├── tests/                     # Test suite
│   ├── __init__.py
│   ├── test_config.py         # Configuration tests
│   └── test_powerdns_client.py # API client tests
│
├── install.sh                 # Installation script
├── uninstall.sh               # Uninstallation script
├── Makefile                   # Development commands
├── pyproject.toml             # Python project configuration
├── requirements.txt           # Python dependencies
│
└── Documentation/
    ├── README.md              # Main readme
    ├── INSTALLATION.md        # Detailed installation guide
    ├── QUICK_START.md         # Quick start guide
    ├── PROJECT_SUMMARY.md     # Architecture overview
    ├── CHANGELOG.md           # Version history
    └── FILES_OVERVIEW.md      # This file
```

## Key Files Description

### Core Package (`src/ultahost_dns/`)

- **config.py**: Manages plugin configuration (API URL, key, enabled state)
- **powerdns_client.py**: Main API client for PowerDNS v4 operations
- **permissions.py**: Handles user permission checking (root/reseller/user)
- **logger.py**: Centralized logging system
- **dns_template.py**: Applies cPanel DNS templates to new zones

### Hook Scripts (`scripts/hooks/`)

These scripts are called by cPanel when DNS operations occur:
- **dns_create_zone**: Creates zone in PowerDNS when domain is added
- **dns_delete_zone**: Deletes zone from PowerDNS when domain is removed
- **dns_add_record**: Adds DNS record via PowerDNS API
- **dns_delete_record**: Deletes DNS record via PowerDNS API
- **dns_update_record**: Updates DNS record via PowerDNS API

### WHM Interface (`whm/cgi/`)

- **ultahost_dns_settings_simple.cgi**: Simple HTML form for configuration (recommended)
- **ultahost_dns_settings.cgi**: Advanced interface using cPanel UI framework

### Installation Scripts

- **install.sh**: Installs plugin, registers hooks, sets permissions
- **uninstall.sh**: Removes plugin and optionally cleans up

### Configuration Files

- **pyproject.toml**: Python package configuration, linting rules
- **requirements.txt**: Python dependencies
- **Makefile**: Development commands (test, lint, format)

## Installation Locations (After Install)

After running `install.sh`, files are installed to:

```
/usr/local/cpanel/whostmgr/docroot/cgi/ultahost_dns/     # WHM interface
/usr/local/cpanel/scripts/ultahost_dns/                  # Hook scripts
/usr/local/cpanel/bin/ultahost_dns/                       # Utilities
/var/cpanel/ultahost_dns_config.json                      # Configuration
/var/log/ultahost_dns/ultahost_dns.log                    # Logs
```

## File Permissions

- Configuration file: `600` (root only)
- Hook scripts: `755` (executable)
- CGI scripts: `755` (executable)
- Log directory: `755` (writable by root)

## Development

### Running Tests
```bash
make test
# or
pytest tests/ -v
```

### Linting
```bash
make lint
make format
```

### Clean Build Artifacts
```bash
make clean
```

## Next Steps

1. Review `INSTALLATION.md` for detailed setup
2. Check `QUICK_START.md` for quick setup
3. Read `PROJECT_SUMMARY.md` for architecture details
4. Install and configure as per installation guide

