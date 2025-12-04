package Api2::UltahostDns::Dns;

use strict;
use warnings;

# Custom API2 module for DNS operations via PowerDNS API
# This replaces the default Api2::Dns module when plugin is enabled

use Cpanel::JSON ();

# Check if plugin is enabled
sub _is_enabled {
    my $config_file = '/var/cpanel/ultahost_dns_config.json';
    return 0 unless -f $config_file;
    
    eval {
        open(my $fh, '<', $config_file) or return 0;
        my $json_content = do { local $/; <$fh> };
        close $fh;
        my $config = Cpanel::JSON::decode_json($json_content);
        
        my $enabled = $config->{enabled};
        if (ref($enabled) eq '') {
            $enabled = lc($enabled) eq 'true' || $enabled eq '1';
        }
        
        return $enabled && $config->{api_url} && $config->{api_key};
    };
    
    return 0;
}

sub listzones {
    my ($self, $api, $opts) = @_;
    
    return unless _is_enabled();
    
    # Call our Python script to list zones
    my $output = `python3 /usr/local/cpanel/scripts/ultahost_dns/dns_list_zones 2>&1`;
    my $result = eval { Cpanel::JSON::decode_json($output) };
    
    if ($result && $result->{status} == 1) {
        return {
            data => $result->{data}->{zones} || [],
        };
    }
    
    return;
}

sub fetchzone {
    my ($self, $api, $opts) = @_;
    
    return unless _is_enabled();
    
    my $zone = $opts->{zone} || $opts->{domain};
    return unless $zone;
    
    # Call our Python script to fetch zone
    my $output = `python3 /usr/local/cpanel/scripts/ultahost_dns/dns_fetch_zone '$zone' 2>&1`;
    my $result = eval { Cpanel::JSON::decode_json($output) };
    
    if ($result && $result->{status} == 1) {
        return {
            data => $result->{data} || {},
        };
    }
    
    return;
}

1;

