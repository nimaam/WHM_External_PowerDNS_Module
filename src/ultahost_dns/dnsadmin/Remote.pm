package Cpanel::Dnsadmin::Plugins::UltahostDns::Remote;

use strict;
use warnings;

# cPanel dnsadmin Remote module for Ultahost DNS (PowerDNS v4 API)
# This module handles all DNS operations via PowerDNS API

sub new {
    my ($class, $node_config) = @_;
    my $self = bless {
        node_config => $node_config,
    }, $class;
    return $self;
}

sub listzones {
    my ($self) = @_;

    # List zones from PowerDNS API
    my $output = `python3 /usr/local/cpanel/bin/ultahost_dns/list_zones_api.py 2>&1`;
    my @zones = split(/\n/, $output);
    return grep { $_ } @zones;
}

sub fetchzone {
    my ($self, $zone) = @_;

    # Fetch zone from PowerDNS API
    my $output = `python3 /usr/local/cpanel/bin/ultahost_dns/fetch_zone_api.py '$zone' 2>&1`;
    return $output;
}

sub createzone {
    my ($self, $zone, $template) = @_;

    # Create zone in PowerDNS API
    my $result = system("python3", "/usr/local/cpanel/scripts/ultahost_dns/dns_create_zone", 
                        $zone, $zone, $template || "default", "root");
    return $result == 0;
}

sub deletezone {
    my ($self, $zone) = @_;

    # Delete zone from PowerDNS API
    my $result = system("python3", "/usr/local/cpanel/scripts/ultahost_dns/dns_delete_zone", 
                        $zone, "root");
    return $result == 0;
}

sub addrecord {
    my ($self, $zone, $name, $type, $data, $ttl, $priority) = @_;

    # Add record to PowerDNS API
    my $result = system("python3", "/usr/local/cpanel/scripts/ultahost_dns/dns_add_record",
                        $zone, $name, $type, $data, $ttl || 3600, $priority || 0, "root");
    return $result == 0;
}

sub deleterecord {
    my ($self, $zone, $name, $type) = @_;

    # Delete record from PowerDNS API
    my $result = system("python3", "/usr/local/cpanel/scripts/ultahost_dns/dns_delete_record",
                        $zone, $name, $type, "root");
    return $result == 0;
}

sub editrecord {
    my ($self, $zone, $name, $type, $data, $ttl, $priority) = @_;

    # Update record in PowerDNS API
    my $result = system("python3", "/usr/local/cpanel/scripts/ultahost_dns/dns_update_record",
                        $zone, $name, $type, $data, $ttl || 3600, $priority || 0, "root");
    return $result == 0;
}

1;

