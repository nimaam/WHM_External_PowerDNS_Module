#!/usr/bin/perl
# Ultahost DNS Settings - Simple WHM Interface
# Compatible with cPanel/WHM 130.x.x

use strict;
use warnings;
use Cpanel::JSON ();
use CGI qw(:standard);

my $q = CGI->new;
my $config_file = '/var/cpanel/ultahost_dns_config.json';

# Check root access
if ($ENV{'REMOTE_USER'} ne 'root') {
    print $q->header(-status => '403 Forbidden');
    print "Access denied. Root access required.";
    exit;
}

# Load configuration
my $config = {
    api_url => '',
    api_key => '',
    enabled => 0,
};

if (-f $config_file) {
    open(my $fh, '<', $config_file) or die "Cannot read $config_file: $!";
    my $json_content = do { local $/; <$fh> };
    close $fh;
    eval {
        $config = Cpanel::JSON::decode_json($json_content);
    };
}

# Handle form submission
if ($q->param('action') eq 'save') {
    my $api_url = $q->param('api_url') || '';
    my $api_key = $q->param('api_key') || '';
    my $enabled = $q->param('enabled') ? 1 : 0;

    # Validate
    unless ($api_url =~ m{^https?://}) {
        print $q->header;
        print "<html><body><h1>Error</h1><p>Invalid API URL format. Must start with http:// or https://</p>";
        print "<p><a href='?'>Go Back</a></p></body></html>";
        exit;
    }

    # Save
    my $json_data = Cpanel::JSON::encode_json({
        api_url => $api_url,
        api_key => $api_key,
        enabled => $enabled,
    });

    open(my $fh, '>', $config_file) or die "Cannot write $config_file: $!";
    print $fh $json_data;
    close $fh;
    chmod 0600, $config_file;

    # Test connection if enabled
    my $test_result = '';
    if ($enabled) {
        my $test_output = `python3 /usr/local/cpanel/bin/ultahost_dns/test_connection.py 2>&1`;
        if ($? != 0) {
            $test_result = "<div class='alert alert-warning'>Configuration saved, but connection test failed. Please verify your API settings.</div>";
        } else {
            $test_result = "<div class='alert alert-success'>Configuration saved successfully and connection test passed!</div>";
        }
    } else {
        $test_result = "<div class='alert alert-success'>Configuration saved successfully.</div>";
    }

    print $q->redirect("?saved=1&test=" . ($? == 0 ? "1" : "0"));
    exit;
}

# Display form
print $q->header(-type => 'text/html', -charset => 'UTF-8');

my $saved_msg = '';
if ($q->param('saved')) {
    if ($q->param('test') eq '1') {
        $saved_msg = '<div class="alert alert-success">Configuration saved and connection test passed!</div>';
    } else {
        $saved_msg = '<div class="alert alert-warning">Configuration saved, but connection test failed. Please verify your API settings.</div>';
    }
}

print <<HTML;
<!DOCTYPE html>
<html>
<head>
    <title>Ultahost DNS Settings</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        h1 { color: #333; border-bottom: 2px solid #0073aa; padding-bottom: 10px; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; color: #555; }
        input[type="text"], input[type="password"] { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 3px; box-sizing: border-box; }
        input[type="checkbox"] { margin-right: 5px; }
        .help-text { font-size: 12px; color: #666; margin-top: 5px; }
        .btn { background: #0073aa; color: white; padding: 10px 20px; border: none; border-radius: 3px; cursor: pointer; font-size: 14px; }
        .btn:hover { background: #005a87; }
        .alert { padding: 10px; margin-bottom: 15px; border-radius: 3px; }
        .alert-success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .alert-warning { background: #fff3cd; color: #856404; border: 1px solid #ffeaa7; }
        .info-box { background: #e7f3ff; border-left: 4px solid #0073aa; padding: 15px; margin-top: 20px; }
        .info-box ul { margin: 10px 0; padding-left: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Ultahost DNS Settings</h1>
        <p>Configure PowerDNS v4 API integration for WHM/cPanel DNS management.</p>
        
        $saved_msg
        
        <form method="POST" action="?action=save">
            <div class="form-group">
                <label for="api_url">PowerDNS v4 API URL *</label>
                <input type="text" id="api_url" name="api_url" value="$config->{api_url}" required>
                <div class="help-text">Full URL to your PowerDNS v4 API (e.g., https://dns.example.com:8081)</div>
            </div>
            
            <div class="form-group">
                <label for="api_key">API Key *</label>
                <input type="password" id="api_key" name="api_key" value="$config->{api_key}" required>
                <div class="help-text">PowerDNS v4 API authentication key</div>
            </div>
            
            <div class="form-group">
                <label>
                    <input type="checkbox" name="enabled" value="1" $config->{enabled} ? 'checked' : ''>
                    Enable Plugin
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
            <p><strong>Note:</strong> After enabling, test the connection to ensure your API settings are correct. Logs are available at <code>/var/log/ultahost_dns/ultahost_dns.log</code></p>
        </div>
    </div>
</body>
</html>
HTML

