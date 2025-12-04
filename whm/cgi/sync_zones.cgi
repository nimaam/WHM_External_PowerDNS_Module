#!/usr/bin/perl
# Sync zones from PowerDNS to cPanel - WHM Interface

use strict;
use warnings;
use lib '/usr/local/cpanel';
use Cpanel::JSON ();
use CGI qw(:standard);

my $q = CGI->new;

# Security check
my $user = $ENV{'REMOTE_USER'} || '';
if ($user ne 'root') {
    print $q->header(-type => 'application/json', -status => '403');
    print Cpanel::JSON::Dump({ success => 0, error => 'Access denied' });
    exit;
}

# Run sync script
my $output = `python3 /usr/local/cpanel/bin/ultahost_dns/sync_zones.py 2>&1`;
my $exit_code = $? >> 8;

my $result = {
    success => ($exit_code == 0) ? 1 : 0,
    message => $exit_code == 0 ? 'Zones synced successfully' : 'Zone sync completed with errors',
    output => $output,
};

print $q->header(-type => 'application/json');
print Cpanel::JSON::Dump($result);

