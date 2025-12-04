#!/usr/bin/perl
# cPanel - WHM API 1.0
# Copyright 2024 cPanel, L.L.C.
# All rights reserved.
# cpanel.net

use strict;
use warnings;
use Cpanel::JSON ();
use Cpanel::JSON::XS ();
use Cpanel::Whostmgr::UI ();
use Cpanel::Whostmgr::UI::Request ();
use Cpanel::Whostmgr::UI::Response ();
use Cpanel::Whostmgr::UI::Template ();
use Cpanel::Whostmgr::UI::Widget ();
use Cpanel::Whostmgr::UI::Widget::Form ();
use Cpanel::Whostmgr::UI::Widget::Form::Field ();
use Cpanel::Whostmgr::UI::Widget::Form::Field::Text ();
use Cpanel::Whostmgr::UI::Widget::Form::Field::Password ();
use Cpanel::Whostmgr::UI::Widget::Form::Field::Checkbox ();
use Cpanel::Whostmgr::UI::Widget::Form::Field::Submit ();

my $request = Cpanel::Whostmgr::UI::Request->new();
my $response = Cpanel::Whostmgr::UI::Response->new();

# Check root access
unless ( $request->user() eq 'root' ) {
    $response->error("Access denied. Root access required.");
    $response->print();
    exit;
}

my $action = $request->param('action') || 'display';
my $config_file = '/var/cpanel/ultahost_dns_config.json';

if ( $action eq 'save' ) {
    my $api_url = $request->param('api_url') || '';
    my $api_key = $request->param('api_key') || '';
    my $enabled = $request->param('enabled') ? 1 : 0;

    # Validate inputs
    unless ( $api_url =~ m{^https?://} ) {
        $response->error("Invalid API URL format. Must start with http:// or https://");
        $response->print();
        exit;
    }

    # Save configuration using Python script
    my $json_data = Cpanel::JSON::encode_json({
        api_url => $api_url,
        api_key => $api_key,
        enabled => $enabled,
    });

    open( my $fh, '>', $config_file ) or do {
        $response->error("Failed to save configuration: $!");
        $response->print();
        exit;
    };
    print $fh $json_data;
    close $fh;
    chmod 0600, $config_file;

    # Test connection if enabled
    if ( $enabled ) {
        my $test_result = `python3 /usr/local/cpanel/bin/ultahost_dns/test_connection.py 2>&1`;
        if ( $? != 0 ) {
            $response->warning("Configuration saved, but connection test failed. Please verify your API settings.");
        } else {
            $response->success("Configuration saved successfully and connection test passed.");
        }
    } else {
        $response->success("Configuration saved successfully.");
    }

    $response->redirect('/cgi/ultahost_dns_settings.cgi');
    $response->print();
    exit;
}

# Load current configuration
my $config = {
    api_url => '',
    api_key => '',
    enabled => 0,
};

if ( -f $config_file ) {
    my $json_content = do {
        local $/;
        open( my $fh, '<', $config_file ) or die "Cannot read $config_file: $!";
        <$fh>;
    };
    eval {
        $config = Cpanel::JSON::decode_json($json_content);
    };
}

# Display form
my $form = Cpanel::Whostmgr::UI::Widget::Form->new(
    action => '/cgi/ultahost_dns_settings.cgi',
    method => 'POST',
    fields => [
        Cpanel::Whostmgr::UI::Widget::Form::Field::Text->new(
            name => 'api_url',
            label => 'PowerDNS v4 API URL',
            value => $config->{api_url},
            required => 1,
            help => 'Full URL to your PowerDNS v4 API (e.g., https://dns.example.com:8081)',
        ),
        Cpanel::Whostmgr::UI::Widget::Form::Field::Password->new(
            name => 'api_key',
            label => 'API Key',
            value => $config->{api_key},
            required => 1,
            help => 'PowerDNS v4 API authentication key',
        ),
        Cpanel::Whostmgr::UI::Widget::Form::Field::Checkbox->new(
            name => 'enabled',
            label => 'Enable Plugin',
            value => 1,
            checked => $config->{enabled},
            help => 'Enable Ultahost DNS plugin to replace default DNS module',
        ),
        Cpanel::Whostmgr::UI::Widget::Form::Field::Submit->new(
            name => 'submit',
            value => 'Save Settings',
        ),
    ],
);

my $template = Cpanel::Whostmgr::UI::Template->new();
$template->set_template('ultahost_dns_settings');
$template->set_vars(
    form => $form,
    config => $config,
);

$response->content($template->render());
$response->print();

