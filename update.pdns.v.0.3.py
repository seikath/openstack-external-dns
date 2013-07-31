# coding=utf8 ================================================================================================
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
"""
# ================================================================================================
import MySQLdb
import socket
import sys
from datetime import datetime

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
#epg_debug = True

if not epg_debug : print "["+str(datetime.now())+"] : Debug set to false at /home/epg/bin/epg-pdns-03/update.pdns.v.0.3.py"

# CONFIGs, SQL etc ========= [ end ] 

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
	# construct the SQL 
	query_pdns_delete = (
		"delete from records where name= '%s.openstack.hi.inet';"
		)
	# execute the SQL 
	try:
		cursor_pdns.execute(query_pdns_delete  % (hostname))
		if epg_debug : print ("["+str(datetime.now())+"] : " + "Executed : " + query_pdns_delete % (hostname)) 
	except MySQLdb.Error, e:
		print "["+str(datetime.now())+"] : " + "Error %d: %s" % (e.args[0], e.args[1])
		sys.exit (1)

# inject the new ones 
for (id,hostname,floating_ip) in cursor_nova:
	query_pdns_insert = (
	"insert into records (domain_id, name, content, type,ttl,prio,last_update) "
	"VALUES (2,'%s.openstack.hi.inet','%s','A',120,NULL,now());"
	)
	# debug 
	try:
		socket.inet_aton(floating_ip)
		if debug : print ("["+str(datetime.now())+"] : " + "test : " + floating_ip)
		# execute the SQL 
		try:
			cursor_pdns.execute(query_pdns_insert  % (hostname,floating_ip))
			if epg_debug : print ("["+str(datetime.now())+"] : " + "Executed : " + query_pdns_insert % (hostname,floating_ip))			
		except MySQLdb.Error, e:
			print "["+str(datetime.now())+"] : " + "Error %d: %s" % (e.args[0], e.args[1])
			sys.exit (1)
	except socket.error : 
		if debug : print ("["+str(datetime.now())+"] : " + "Skipping this one : {}".format(query_pdns_insert))
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
