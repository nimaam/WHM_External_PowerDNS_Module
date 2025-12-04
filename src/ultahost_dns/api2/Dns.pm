package Api2::Dns;

use strict;
use warnings;

# Override default Api2::Dns module for PowerDNS API
# This module extends/replaces the default DNS API2 module

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
    
    # Only override if plugin is enabled
    unless (_is_enabled()) {
        # Call parent method if it exists
        if (my $parent = $self->can('SUPER::listzones')) {
            return $self->$parent($api, $opts);
        }
        return;
    }
    
    # Call our Python script to list zones
    my $output = `python3 /usr/local/cpanel/scripts/ultahost_dns/dns_list_zones 2>&1`;
    my $result = eval { Cpanel::JSON::decode_json($output) };
    
    if ($result && $result->{status} == 1 && $result->{data}->{zone}) {
        # Return in cPanel API2 format
        return {
            data => {
                zone => $result->{data}->{zone} || [],
            },
        };
    }
    
    return;
}

sub fetchzone {
    my ($self, $api, $opts) = @_;
    
    # Only override if plugin is enabled
    unless (_is_enabled()) {
        # Call parent method if it exists
        if (my $parent = $self->can('SUPER::fetchzone')) {
            return $self->$parent($api, $opts);
        }
        return;
    }
    
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

