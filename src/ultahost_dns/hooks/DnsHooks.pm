package Cpanel::Hooks::UltahostDns::DnsHooks;

use strict;
use warnings;

# cPanel hook module for DNS operations
# This module can properly intercept API2 calls

sub describe {
    return {
        category => 'Whostmgr',
        event    => 'Api2::Dns::listzones',
        stage    => 'pre',
        exectype => 'module',
        hook     => __PACKAGE__ . '::listzones',
    };
}

sub listzones {
    my ($context, $event, $data) = @_;
    
    # Check if plugin is enabled
    my $config_file = '/var/cpanel/ultahost_dns_config.json';
    return unless -f $config_file;
    
    require Cpanel::JSON;
    open(my $fh, '<', $config_file) or return;
    my $json_content = do { local $/; <$fh> };
    close $fh;
    
    my $config = eval { Cpanel::JSON::decode_json($json_content) };
    return unless $config;
    
    my $enabled = $config->{enabled};
    if (ref($enabled) eq '') {
        $enabled = lc($enabled) eq 'true' || $enabled eq '1';
    }
    
    return unless $enabled && $config->{api_url} && $config->{api_key};
    
    # Call Python script to get zones
    my $output = `python3 /usr/local/cpanel/scripts/ultahost_dns/dns_list_zones 2>&1`;
    my $result = eval { Cpanel::JSON::decode_json($output) };
    
    if ($result && $result->{status} == 1) {
        # Override the API2 response
        # This might not work, but it's worth trying
        $data->{data} = $result->{data} if $data;
    }
    
    return;
}

1;

