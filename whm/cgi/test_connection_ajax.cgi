#!/usr/bin/perl
# AJAX endpoint for testing PowerDNS connection

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

# Test connection
my $test_output = `python3 /usr/local/cpanel/bin/ultahost_dns/test_connection.py 2>&1`;
my $exit_code = $? >> 8;

my $result = {
    success => ($exit_code == 0) ? 1 : 0,
    message => '',
    output => $test_output,
};

if ($exit_code == 0) {
    $result->{message} = 'Connection test successful!';
} else {
    $result->{message} = 'Connection test failed. Please check your API settings.';
    $result->{error} = $test_output;
}

print $q->header(-type => 'application/json');
print Cpanel::JSON::Dump($result);

