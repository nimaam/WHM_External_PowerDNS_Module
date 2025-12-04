# Ultahost DNS Plugin Installation Guide

## Prerequisites

- cPanel/WHM 130.x.x installed
- Root access to the server
- Python 3.12 or higher
- PowerDNS v4 API server accessible
- PowerDNS v4 API key

## Installation Steps

### 1. Clone or Download the Plugin

```bash
cd /root
git clone <your-repo-url> Ultahost-DNS
cd Ultahost-DNS
```

### 2. Run Installation Script

```bash
sudo ./install.sh
```

The installation script will:
- Install Python dependencies
- Create necessary directories
- Copy hook scripts
- Register cPanel hooks
- Set up WHM interface
- Create configuration file

### 3. Configure the Plugin

1. Log in to WHM as root
2. Navigate to **Plugins** → **Ultahost DNS Settings**
3. Enter your PowerDNS v4 API configuration:
   - **API URL**: Full URL to your PowerDNS v4 API (e.g., `https://dns.example.com:8081`)
   - **API Key**: Your PowerDNS v4 API authentication key
   - **Enable Plugin**: Check this box to activate the plugin
4. Click **Save Settings**

### 4. Test Connection

After saving, the plugin will automatically test the connection. You can also test manually:

```bash
/usr/local/cpanel/bin/ultahost_dns/test_connection.py
```

### 5. Verify Installation

1. Create a test domain in cPanel
2. Check if DNS zone is created in PowerDNS
3. Verify DNS records are managed through PowerDNS API

## Configuration File

The configuration is stored at:
```
/var/cpanel/ultahost_dns_config.json
```

Format:
```json
{
  "api_url": "https://dns.example.com:8081",
  "api_key": "your-api-key-here",
  "enabled": true
}
```

## Logs

Plugin logs are available at:
```
/var/log/ultahost_dns/ultahost_dns.log
```

View logs:
```bash
tail -f /var/log/ultahost_dns/ultahost_dns.log
```

## Uninstallation

To remove the plugin:

```bash
sudo ./uninstall.sh
```

## Troubleshooting

### Plugin Not Working

1. Check if plugin is enabled:
   ```bash
   cat /var/cpanel/ultahost_dns_config.json
   ```

2. Check logs for errors:
   ```bash
   tail -100 /var/log/ultahost_dns/ultahost_dns.log
   ```

3. Test API connection:
   ```bash
   /usr/local/cpanel/bin/ultahost_dns/test_connection.py
   ```

4. Verify hooks are registered:
   ```bash
   /usr/local/cpanel/bin/manage_hooks list
   ```

### Permission Issues

- Ensure configuration file has correct permissions (600)
- Check that hook scripts are executable (755)
- Verify PowerDNS API key has proper permissions

### DNS Zones Not Creating

1. Check PowerDNS API is accessible from cPanel server
2. Verify API key is correct
3. Check PowerDNS server logs
4. Review plugin logs for specific errors

## Support

For issues or questions, check the logs first and provide:
- Error messages from logs
- Configuration (without API key)
- cPanel/WHM version
- PowerDNS version

