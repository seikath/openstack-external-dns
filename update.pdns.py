import datetime
import MySQLdb

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

cnx_nova = MySQLdb.connect(**config_nova)
cnx_pdns = MySQLdb.connect(**config_pdns)
cursor_nova = cnx_nova.cursor()
cursor_pdns = cnx_pdns.cursor()

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


query = ("""select
i.id
, i.hostname
-- , i.host
-- , i.vm_state
-- , m.uuid
-- , f.id
-- , f.address as fixed_ip
, s.address as floating_ip
from
instances i  left join instance_id_mappings m on i.id=m.id
left join fixed_ips f on m.uuid=f.instance_uuid
left join floating_ips s on f.id=s.fixed_ip_id
where
i.vm_state != 'deleted'
and i.host is not null""")



cursor_nova.execute(query)
for (id,hostname,floating_ip) in cursor_nova:
  query_pdns = (
"delete from records where name= '%s.openstack.hi.inet';"
"insert into records (domain_id, name, content, type,ttl,prio,last_update) "
"VALUES (2,'%s.openstack.hi.inet','%s','A',120,NULL,now());"
)

  query_pdns_delete = (
"delete from records where name= '%s.openstack.hi.inet';"
)
  query_pdns_insert = (
"insert into records (domain_id, name, content, type,ttl,prio,last_update) "
"VALUES (2,'%s.openstack.hi.inet','%s','A',120,NULL,now());"
)
  cursor_pdns.execute(query_pdns_delete  % (hostname))
  cursor_pdns.execute(query_pdns_insert  % (hostname,floating_ip))
  print (query_pdns % (hostname,hostname,floating_ip)) 
cnx_pdns.commit()
cursor_nova.close()
cursor_pdns.close()
cnx_pdns.close()
cnx_nova.close()

