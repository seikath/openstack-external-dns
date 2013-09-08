openstack-external-dns
====================================
Two ways of offering DNS service with the OpenStack VMs records to an external to the OpenStack environment networks 

1. PowerDNS based - we run a cluster of two instances with PowerDNS collecting independently the floating IP data from the Nova DB tables.
We assing a floating IP registered as forwarder at the external DNS to the active PowerDNS instance.
In case its down, we reassign the IP to the second PowerDNS instance.

2. Direct updates at the repote network DNS server - BIND in this case useing dynamic DNS updates.
This method is slow, as each record should be deleted before each insert, this is a separate calls to nsupdate.


In general the Independent standalone PowerDNS based solution is preferable, 
as the updates are done in a single MySQL transaction, so we can push thousands of changes in one commit.

Anyway, the direct BIND update is still working alternative.

Cheers,

Slackware4Life !!!

  
