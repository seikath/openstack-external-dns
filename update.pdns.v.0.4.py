# coding=utf8
# vim: set fileencoding=utf8
# -*- coding: utf8 -*-
# ================================================================================================
"""
mysql pdns@epg-pdns-03:[Wed Jul 24 15:37:36 2013][nova]> select 
    -> i.id, i.hostname
    -> , i.host
    -> ,i.vm_state
    -> , m.uuid 
    -> , f.id
    -> , f.address as fixed_ip
    -> , s.address as floating_ip
    -> from 
    -> instances i  left join instance_id_mappings m on i.id=m.id  
    -> left join fixed_ips f on m.uuid=f.instance_uuid
    -> left join floating_ips s on f.id=s.fixed_ip_id
    -> where 
    -> i.vm_state != 'deleted'
    -> and i.host is not null ;
+----+---------------------------------------+-----------------+----------+--------------------------------------+------+------------+--------------+
| id | hostname                              | host            | vm_state | uuid                                 | id   | address    | address      |
+----+---------------------------------------+-----------------+----------+--------------------------------------+------+------------+--------------+
| 11 | ep-heat                               | epg-openstack07 | active   | 8ca01409-04d7-4fbc-8266-c0cc8ae97aaf |    3 | 10.200.0.2 | 10.95.158.10 |
| 20 | epg-pdns-03                           | epg-openstack07 | active   | eb51314b-1472-4c52-9bf2-73940018c2d4 |    8 | 10.200.0.7 | 10.95.158.14 |
| 21 | epg-bind                              | epg-openstack09 | active   | 5c947d57-f49d-4c6e-8d46-ad4d59925cf4 |    4 | 10.200.0.3 | 10.95.158.3  |
| 22 | ep-horizon                            | epg-openstack09 | active   | 3296c158-0a30-4262-ad40-38e102ce6a5c |    6 | 10.200.0.5 | 10.95.158.15 |
| 23 | stackdeprueba-myinstance-2x55twpyrork | epg-openstack07 | active   | 239e0a64-63cf-442d-ac58-55d99b665c52 |    5 | 10.200.0.4 | NULL         |
+----+---------------------------------------+-----------------+----------+--------------------------------------+------+------------+--------------+
5 rows in set (0.01 sec)


mysql pdns_user@epg-pdns-03:[Wed Jul 31 11:03:52 2013][pdns]> 
insert into records (domain_id,name,type,content,ttl) values (2,'116.96.95.10.in-addr.arpa','PTR','epg-openstack-06.hi.inet','120');Query OK, 1 row affected (0.02 sec)



BAJA del host “inventado.hi.inet”: à “Kns1-ns1.+157+29057.private” es la clave privada de bind (disponible por defecto en /etc/bind/)
dns_baja inventado.hi.inet.| nsupdate -k /etc/bind/Kns1-ns1.+157+29057.private
ALTA del host “inventado.hi.inet” con IP 10.95.95.95: à “Kns1-ns1.+157+29057.private” es la clave privada de bind
dns_alta inventado.hi.inet. 10.95.95.95| nsupdate -k /etc/bind/Kns1-ns1.+157+29057.private

epg@epg-bind:[Wed Jul 31 09:14:49][~/bin/openstack-powerdns/scripts]$ ./dns_alta test.openstack.hi.inet. 10.95.158.5
prereq nxrrset test.openstack.hi.inet. IN A
update add test.openstack.hi.inet. 86400 IN A 10.95.158.5
send
update delete 5.158.95.10.in-addr.arpa. IN PTR
update add 5.158.95.10.in-addr.arpa. 86400 IN PTR test.openstack.hi.inet.
send

yum search python ipaddr
ipaddress
http://docs.python.org/dev/library/ipaddress


Jul 31 11:12:02 epg-pdns-03 pdns[11567]: Remote 10.95.146.80 wants '116.96.95.10.in-addr.arpa|PTR', do = 0, bufsize = 512: packetcache MISS
Jul 31 11:12:02 epg-pdns-03 pdns[11567]: Query: select content,ttl,prio,type,domain_id,name from records where type='SOA' and name='116.96.95.10.in-addr.arpa'
Jul 31 11:12:02 epg-pdns-03 pdns[11567]: Query: select max(change_date) from records where domain_id=2
Jul 31 11:12:02 epg-pdns-03 pdns[11567]: Query: select content,ttl,prio,type,domain_id,name from records where name='116.96.95.10.in-addr.arpa' and domain_id=2

ivan@ivan.hi.inet:[Wed Jul 31 11:10:55][~/Private/Boxes.Solomon.Engel/VPN]$ host 10.95.96.116 10.95.158.14
Using domain server:
Name: 10.95.158.14
Address: 10.95.158.14#53
Aliases: 

116.96.95.10.in-addr.arpa has no PTR record


ivan@ivan.hi.inet:[Wed Jul 31 11:14:59][~/Private/Boxes.Solomon.Engel/VPN]$ host 10.95.96.116 10.95.158.14
Using domain server:
Name: 10.95.158.14
Address: 10.95.158.14#53
Aliases: 

116.96.95.10.in-addr.arpa domain name pointer epg-openstack-06.hi.inet.
Jul 31 11:17:33 epg-pdns-03 pdns[11567]: Remote 10.95.146.80 wants '116.96.95.10.in-addr.arpa|PTR', do = 0, bufsize = 512: packetcache MISS
Jul 31 11:17:33 epg-pdns-03 pdns[11567]: Query: select content,ttl,prio,type,domain_id,name from records where type='SOA' and name='116.96.95.10.in-addr.arpa'
Jul 31 11:17:33 epg-pdns-03 pdns[11567]: Query: select content,ttl,prio,type,domain_id,name from records where name='116.96.95.10.in-addr.arpa' and domain_id=2

insert into records (domain_id,name,type,content,ttl) values (2,'116.96.95.10.in-addr.arpa','SOA','localhost epgbcn4@tid.es 1','120');
insert into records (domain_id,name,type,content,ttl) values (2,'116.96.95.10.in-addr.arpa','PTR','epg-openstack-06.hi.inet','120');

"""
# ================================================================================================
import MySQLdb
import socket
import sys
from datetime import datetime
#import ipaddr

#print datetime.now()
# CONFIGs, SQL etc ========= [ start ] 
config_nova = {
  'user': 'pdns',
  'passwd': 'pdns_user_passwd',
  'host': '172.16.0.1',
  'db': 'nova',
}

config_pdns = {
  'user': 'pdns_user',
  'passwd': 'pdns_user_passwd',
  'host': '127.0.0.1',
  'db': 'pdns',

}

query = ("""select
i.id
, i.hostname
-- , i.host
-- , i.vm_state
-- , m.uuid
-- , f.id
-- , lower(f.address) as fixed_ip
, lower(s.address) as floating_ip
from
instances i  left join instance_id_mappings m on i.id=m.id
left join fixed_ips f on m.uuid=f.instance_uuid
left join floating_ips s on f.id=s.fixed_ip_id
where true
-- and i.vm_state != 'deleted'
and i.host is not null""")

query_pdns_clean = ("delete from records where content = 'None';")
debug = False
#debug = True
epg_debug = False
# epg_debug = True

if not epg_debug : print "["+str(datetime.now())+"] : Debug set to false at /home/epg/bin/epg-pdns-03/update.pdns.v.0.3.py"

# CONFIGs, SQL etc ========= [ end ] 

#floating_ip = '10.95.158.5'
##print ipaddr.IPv4Address('10.95.158.5/32').explode
#reversed_fip= '.'.join(floating_ip.split('.')[::-1])
#print '.'.join(floating_ip.split('.')[::-1]), reversed_fip



#sys.exit (0)


# initialize db conection to nova
try:
	cnx_nova = MySQLdb.connect(**config_nova)
	# open nova cursor
	cursor_nova = cnx_nova.cursor()
except MySQLdb.Error, e:
	print "["+str(datetime.now())+"] : " + "Error %d: %s" % (e.args[0], e.args[1])
	sys.exit (1)
	
# start the data processing
try:
	cursor_nova.execute(query)
	# initialize db conection to pdns
	try:
		cnx_pdns = MySQLdb.connect(**config_pdns)
		# open pdns cursor
		cursor_pdns = cnx_pdns.cursor()
	except MySQLdb.Error, e:
		print "["+str(datetime.now())+"] : " + "Error %d: %s" % (e.args[0], e.args[1])
		sys.exit (1)
except Exception, e:
	print "["+str(datetime.now())+"] : " + repr(e)
	sys.exit (1)
	
# general clen up 
try:
	cursor_pdns.execute(query_pdns_clean)
	if epg_debug : print ("["+str(datetime.now())+"] : " + "Executed : " + query_pdns_clean) 
except MySQLdb.Error, e:
	print "["+str(datetime.now())+"] : " + "Error %d: %s" % (e.args[0], e.args[1])
	sys.exit (1)

# clean the old records 
for (id,hostname,floating_ip) in cursor_nova:
	# check if the IP is not null
	try:
		socket.inet_aton(floating_ip)
		# assign the reverse IP 
		reverse_ip = '.'.join(floating_ip.split('.')[::-1])
		# construct the SQL
		query_pdns_delete = (
			"delete from records where name= '%s.openstack.hi.inet';"
			)
		query_pdns_delete_ptr_and_soa = (
			"delete from records where name= '%s.in-addr.arpa';"
			)			
		# execute the SQL 
		try:
			cursor_pdns.execute(query_pdns_delete  % (hostname))
			if epg_debug : print ("["+str(datetime.now())+"] : " + "Executed : " + query_pdns_delete % (hostname)) 
		except MySQLdb.Error, e:
			print "["+str(datetime.now())+"] : " + "Error %d: %s" % (e.args[0], e.args[1])
			sys.exit (1)
		try:
			cursor_pdns.execute(query_pdns_delete_ptr_and_soa  % (reverse_ip))
			if epg_debug : print ("["+str(datetime.now())+"] : " + "Executed : " + query_pdns_delete_ptr_and_soa % (reverse_ip))
		except MySQLdb.Error, e:
			print "["+str(datetime.now())+"] : " + "Error %d: %s" % (e.args[0], e.args[1])
			sys.exit (1)	
	except socket.error : 
		if debug : print ("["+str(datetime.now())+"] : " + "Skipping this one : {1}".format(floating_ip))
	except TypeError : 
		if debug : print ("["+str(datetime.now())+"] : " + "cursor_nova: Skipping this one due to Null values for hostname" + hostname)

# inject the new ones 
for (id,hostname,floating_ip) in cursor_nova:
	query_pdns_insert = (
	"insert into records (domain_id, name, content, type,ttl,prio,last_update) "
	"VALUES (2,'%s.openstack.hi.inet','%s','A',120,NULL,now());"
	)
	query_pdns_insert_ptr_soa = (
	"insert into records (domain_id, name, content, type,ttl,prio,last_update,change_date) "
	"VALUES (2,'%s.in-addr.arpa','%s','SOA',120,NULL,now(),unix_timestamp(now()));"
	)
	query_pdns_insert_ptr = (
	"insert into records (domain_id, name, content, type,ttl,prio,last_update,change_date) "
	"VALUES (2,'%s.in-addr.arpa','%s.openstack.hi.inet','PTR',120,NULL,now(),unix_timestamp(now()));"
	)	
	# debug 
	try:
		socket.inet_aton(floating_ip)
		reverse_ip = '.'.join(floating_ip.split('.')[::-1])
		if debug : print ("["+str(datetime.now())+"] : " + "test : " + floating_ip)
		# execute the SQL DNS
		try:
			cursor_pdns.execute(query_pdns_insert  % (hostname,floating_ip))
			if epg_debug : print ("["+str(datetime.now())+"] : " + "Executed : " + query_pdns_insert % (hostname,floating_ip))			
		except MySQLdb.Error, e:
			print "["+str(datetime.now())+"] : " + "Error %d: %s" % (e.args[0], e.args[1])
			sys.exit (1)
		# executre DNS reverse SOA
		try:
			cursor_pdns.execute(query_pdns_insert_ptr_soa  % (reverse_ip,'openstack.hi.inet'))
			if epg_debug : print ("["+str(datetime.now())+"] : " + "Executed : " + query_pdns_insert_ptr_soa % (reverse_ip,'localhost epgbcn4@tid.es 1'))			
		except MySQLdb.Error, e:
			print "["+str(datetime.now())+"] : " + "Error %d: %s" % (e.args[0], e.args[1])
			sys.exit (1)
		# executre DNS reverse PTR
		try:
			cursor_pdns.execute(query_pdns_insert_ptr  % (reverse_ip,hostname))
			if epg_debug : print ("["+str(datetime.now())+"] : " + "Executed : " + query_pdns_insert_ptr % (reverse_ip,hostname))			
		except MySQLdb.Error, e:
			print "["+str(datetime.now())+"] : " + "Error %d: %s" % (e.args[0], e.args[1])
			sys.exit (1)			
	except socket.error : 
		if debug : print ("["+str(datetime.now())+"] : " + "Skipping this one : {1}".format(query_pdns_insert))
	except TypeError : 
		if debug : print ("["+str(datetime.now())+"] : " + "cursor_nova: Skipping this one due to Null values for hostname" + hostname)

# commint the change 
cnx_pdns.commit()
# closae the pdns 
cursor_pdns.close()
cnx_pdns.close()
# closae the nova 
cursor_nova.close()
cnx_nova.close()

#2013-07-26.14.22.47
