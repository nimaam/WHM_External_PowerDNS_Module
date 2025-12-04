#!/usr/bin/perl
# Ultahost DNS Settings - WHM Plugin Interface
# Compatible with cPanel/WHM 130.x.x

use strict;
use warnings;

# Standard cPanel WHM plugin headers
use lib '/usr/local/cpanel';
use Cpanel::JSON ();
use CGI qw(:standard);

# Initialize
my $q = CGI->new;
my $config_file = '/var/cpanel/ultahost_dns_config.json';

# Security check - must be root
my $user = $ENV{'REMOTE_USER'} || '';
if ($user ne 'root') {
    print $q->header(-status => '403 Forbidden', -type => 'text/html');
    print "<html><head><title>Access Denied</title></head><body>";
    print "<h1>Access Denied</h1>";
    print "<p>Root access is required to access this plugin.</p>";
    print "</body></html>";
    exit;
}

# Load configuration
my $config = {
    api_url => '',
    api_key => '',
    enabled => 0,
};

if (-f $config_file && -r $config_file) {
    eval {
        open(my $fh, '<', $config_file) or die "Cannot read $config_file: $!";
        my $json_content = do { local $/; <$fh> };
        close $fh;
        $config = Cpanel::JSON::decode_json($json_content);
    };
    if ($@) {
        # If JSON decode fails, use defaults
        $config = {
            api_url => '',
            api_key => '',
            enabled => 0,
        };
    }
}

# Handle form submission
if ($q->param('action') && $q->param('action') eq 'save') {
    my $api_url = $q->param('api_url') || '';
    my $api_key = $q->param('api_key') || '';
    my $enabled = $q->param('enabled') ? 1 : 0;

    # Validate API URL
    unless ($api_url =~ m{^https?://}) {
        print $q->header(-type => 'text/html');
        print "<html><head><title>Error</title></head><body>";
        print "<h1>Error</h1>";
        print "<p>Invalid API URL format. Must start with http:// or https://</p>";
        print "<p><a href='?'>Go Back</a></p>";
        print "</body></html>";
        exit;
    }

    # Save configuration
    eval {
        my $json_data = Cpanel::JSON::encode_json({
            api_url => $api_url,
            api_key => $api_key,
            enabled => $enabled,
        });

        open(my $fh, '>', $config_file) or die "Cannot write $config_file: $!";
        print $fh $json_data;
        close $fh;
        chmod 0600, $config_file;
    };

    if ($@) {
        print $q->header(-type => 'text/html');
        print "<html><head><title>Error</title></head><body>";
        print "<h1>Error</h1>";
        print "<p>Failed to save configuration: $@</p>";
        print "<p><a href='?'>Go Back</a></p>";
        print "</body></html>";
        exit;
    }

    # Test connection if enabled
    my $test_passed = 0;
    if ($enabled) {
        my $test_output = `python3 /usr/local/cpanel/bin/ultahost_dns/test_connection.py 2>&1`;
        $test_passed = ($? == 0) ? 1 : 0;
    }

    # Redirect with status
    my $redirect_url = "?saved=1";
    $redirect_url .= "&test=$test_passed" if $enabled;
    print $q->redirect($redirect_url);
    exit;
}

# Display form
print $q->header(-type => 'text/html', -charset => 'UTF-8');

# Get saved message
my $saved_msg = '';
if ($q->param('saved')) {
    if ($q->param('test') && $q->param('test') eq '1') {
        $saved_msg = '<div class="alert alert-success">Configuration saved successfully and connection test passed!</div>';
    } elsif ($q->param('test') && $q->param('test') eq '0') {
        $saved_msg = '<div class="alert alert-warning">Configuration saved, but connection test failed. Please verify your API settings.</div>';
    } else {
        $saved_msg = '<div class="alert alert-success">Configuration saved successfully.</div>';
    }
}

# Escape HTML in config values
my $api_url_escaped = $q->escapeHTML($config->{api_url} || '');
my $api_key_escaped = $q->escapeHTML($config->{api_key} || '');
my $enabled_checked = $config->{enabled} ? ' checked' : '';

print <<HTML;
<!DOCTYPE html>
<html>
<head>
    <title>Ultahost DNS Settings</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
            color: #333;
        }
        .container { 
            max-width: 900px; 
            margin: 0 auto; 
            background: white; 
            padding: 30px; 
            border-radius: 8px; 
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        h1 { 
            color: #333; 
            border-bottom: 3px solid #0073aa; 
            padding-bottom: 15px; 
            margin-top: 0;
        }
        .form-group { 
            margin-bottom: 20px; 
        }
        label { 
            display: block; 
            margin-bottom: 8px; 
            font-weight: 600; 
            color: #555; 
        }
        input[type="text"], 
        input[type="password"] { 
            width: 100%; 
            padding: 10px; 
            border: 1px solid #ddd; 
            border-radius: 4px; 
            font-size: 14px;
            transition: border-color 0.3s;
        }
        input[type="text"]:focus,
        input[type="password"]:focus {
            outline: none;
            border-color: #0073aa;
        }
        input[type="checkbox"] { 
            margin-right: 8px; 
            width: 18px;
            height: 18px;
        }
        .help-text { 
            font-size: 13px; 
            color: #666; 
            margin-top: 5px; 
            font-style: italic;
        }
        .btn { 
            background: #0073aa; 
            color: white; 
            padding: 12px 30px; 
            border: none; 
            border-radius: 4px; 
            cursor: pointer; 
            font-size: 16px;
            font-weight: 600;
            transition: background 0.3s;
        }
        .btn:hover { 
            background: #005a87; 
        }
        .alert { 
            padding: 15px; 
            margin-bottom: 20px; 
            border-radius: 4px; 
            border-left: 4px solid;
        }
        .alert-success { 
            background: #d4edda; 
            color: #155724; 
            border-color: #28a745;
        }
        .alert-warning { 
            background: #fff3cd; 
            color: #856404; 
            border-color: #ffc107;
        }
        .info-box { 
            background: #e7f3ff; 
            border-left: 4px solid #0073aa; 
            padding: 20px; 
            margin-top: 30px; 
            border-radius: 4px;
        }
        .info-box h3 {
            margin-top: 0;
            color: #0073aa;
        }
        .info-box ul { 
            margin: 10px 0; 
            padding-left: 25px; 
        }
        .info-box li {
            margin-bottom: 8px;
        }
        code {
            background: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            font-size: 13px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Ultahost DNS Settings</h1>
        <p style="color: #666; margin-bottom: 25px;">Configure PowerDNS v4 API integration for WHM/cPanel DNS management.</p>
        
        $saved_msg
        
        <form method="POST" action="?action=save">
            <div class="form-group">
                <label for="api_url">PowerDNS v4 API URL *</label>
                <input type="text" id="api_url" name="api_url" value="$api_url_escaped" required placeholder="https://dns.example.com:8081">
                <div class="help-text">Full URL to your PowerDNS v4 API server (e.g., https://dns.example.com:8081)</div>
            </div>
            
            <div class="form-group">
                <label for="api_key">API Key *</label>
                <input type="password" id="api_key" name="api_key" value="$api_key_escaped" required placeholder="Enter your API key">
                <div class="help-text">PowerDNS v4 API authentication key</div>
            </div>
            
            <div class="form-group">
                <label style="display: flex; align-items: center; cursor: pointer;">
                    <input type="checkbox" name="enabled" value="1"$enabled_checked>
                    <span>Enable Plugin</span>
                </label>
                <div class="help-text">When enabled, this plugin will replace the default DNS module for all DNS operations</div>
            </div>
            
            <button type="submit" class="btn">Save Settings</button>
        </form>
        
        <div class="info-box">
            <h3>Information</h3>
            <ul>
                <li><strong>API URL:</strong> Enter the full URL to your PowerDNS v4 API server</li>
                <li><strong>API Key:</strong> Your PowerDNS v4 API authentication key</li>
                <li><strong>Enable Plugin:</strong> When enabled, all DNS zone and record management will be handled through PowerDNS v4 API</li>
            </ul>
            <p style="margin-top: 15px; margin-bottom: 0;"><strong>Note:</strong> After enabling, test the connection to ensure your API settings are correct. Logs are available at <code>/var/log/ultahost_dns/ultahost_dns.log</code></p>
        </div>
    </div>
</body>
</html>
HTML
