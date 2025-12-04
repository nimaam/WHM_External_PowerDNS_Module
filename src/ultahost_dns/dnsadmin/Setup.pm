package Cpanel::Dnsadmin::Plugins::UltahostDns;

use strict;
use warnings;

# cPanel dnsadmin Setup module for Ultahost DNS (PowerDNS v4 API)

sub setup {
    my ($class, $node_name, $node_config) = @_;

    # This is called when setting up a DNS node
    # For PowerDNS API, we don't need traditional node setup
    # The configuration is stored in /var/cpanel/ultahost_dns_config.json

    return 1;  # Success
}

sub validate {
    my ($class, $node_config) = @_;

    # Validate the node configuration
    # For PowerDNS API, we validate the API URL and key
    require Cpanel::JSON;
    my $config_file = '/var/cpanel/ultahost_dns_config.json';

    if (-f $config_file) {
        open(my $fh, '<', $config_file) or return 0;
        my $json_content = do { local $/; <$fh> };
        close $fh;

        my $config = eval { Cpanel::JSON::decode_json($json_content) };
        return 0 unless $config;

        # Validate API URL and key exist
        return 1 if $config->{api_url} && $config->{api_key} && $config->{enabled};
    }

    return 0;  # Invalid configuration
}

1;

