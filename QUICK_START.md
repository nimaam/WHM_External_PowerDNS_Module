# Quick Start Guide

## Installation

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url> Ultahost-DNS
   cd Ultahost-DNS
   ```

2. **Run installation:**
   ```bash
   sudo ./install.sh
   ```

3. **Configure in WHM:**
   - Log in to WHM as root
   - Go to: **Plugins** → **Ultahost DNS Settings**
   - Enter your PowerDNS v4 API URL (e.g., `https://dns.example.com:8081`)
   - Enter your PowerDNS v4 API Key
   - Check "Enable Plugin"
   - Click "Save Settings"

4. **Test:**
   ```bash
   /usr/local/cpanel/bin/ultahost_dns/test_connection.py
   ```

## Verification

1. Create a test domain in cPanel
2. Check if DNS zone exists in PowerDNS
3. Add a DNS record through cPanel
4. Verify it appears in PowerDNS

## Troubleshooting

**Check logs:**
```bash
tail -f /var/log/ultahost_dns/ultahost_dns.log
```

**Check configuration:**
```bash
cat /var/cpanel/ultahost_dns_config.json
```

**Verify hooks:**
```bash
/usr/local/cpanel/bin/manage_hooks list | grep ultahost
```

## Uninstall

```bash
sudo ./uninstall.sh
```

