# ================================================================================================
"""
epg@epg-bind:[Thu Aug 01 11:36:18][~/bin/openstack-powerdns] [v6-Bash-Awk]$ scripts/dns_alta ep-rushstack.openstack.hi.inet. 10.95.158.4
prereq nxrrset ep-rushstack.openstack.hi.inet. IN A
update add ep-rushstack.openstack.hi.inet. 86400 IN A 10.95.158.4
send
update delete 4.158.95.10.in-addr.arpa. IN PTR
update add 4.158.95.10.in-addr.arpa. 86400 IN PTR ep-rushstack.openstack.hi.inet.
send
root@epg-bind:[Thu Aug 01 13:20:25][/etc]$ dnssec-keygen -a HMAC-MD5 -b 512 -n HOST openstack.hi.inet 
Kopenstack.hi.inet.+157+62199
-rw-------.  1 root root   229 Aug  1 13:26 Kopenstack.hi.inet.+157+62199.private
-rw-------.  1 root root   126 Aug  1 13:26 Kopenstack.hi.inet.+157+62199.key
import paramiko
ssh = paramiko.SSHClient()
ssh.connect('127.0.0.1', username='jesse', 
    password='lol')
"""
# ================================================================================================
import MySQLdb
import socket
import sys
from datetime import datetime
import ConfigParser
import os
import paramiko
from  remote_execute import MySSH

# CONFIGs, SQL etc ========= [ start ] 
config = ConfigParser.SafeConfigParser()
# get the config at the db.config file in the same directory 
config.read(os.path.dirname(os.path.abspath(__file__))+'/db.config')
# assign the db configs
config_nova = dict(config.items("nova"))

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

debug = False
#debug = True
epg_debug = False
epg_debug = True
ssh_debug = False

if not epg_debug : print "["+str(datetime.now())+"] : Debug set to false at " + os.path.abspath(__file__)

def run_ssh_cmd(cmd, indata=None,epg_debug=False):
	'''
        Run a command with optional input.
 
        @param cmd    The command to execute.
        @param indata The input data.
        @returns The command exit status and output.
                 Stdout and stderr are combined.
        '''
        if epg_debug : print
        if epg_debug : print '=' * 64
        if epg_debug : print 'command: %s' % (cmd)
        status, output = ssh.run(cmd, indata)
        if epg_debug : print 'status : %d' % (status)
        if epg_debug : print 'output : %d bytes' % (len(output))
        if epg_debug : print '=' * 64
        return output.strip('\r\n')

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
	ssh = MySSH()
	ssh.set_verbosity(False)
	ssh.connect(hostname=config.get("ssh-epg-ns1-tic-key","hostname"),
		username=config.get("ssh-epg-ns1-tic-key","username"),
		password=config.get("ssh-epg-ns1-tic-key","password"),
		port=config.getint("ssh-epg-ns1-tic-key","port"),
	)
	#ssh.connect(**config_ssh)
	if ssh.connected() is False:
		print 'ERROR: connection failed to % as user %' % (config.get("ssh-epg-ns1-tic-key","hostname"),config.get("ssh-epg-ns1-tic-key","username"))
		sys.exit(1)
except Exception, e:
	print "["+str(datetime.now())+"] : like 92 " + repr(e)
	sys.exit (1)
	

# inject the new ones 
for (id,hostname,floating_ip) in cursor_nova:

	try:
		socket.inet_aton(floating_ip)
		reverse_ip = '.'.join(floating_ip.split('.')[::-1])
		query_nsupdate_insert = (
		"prereq nxrrset {0!s}.openstack.hi.inet. IN A\n"
		"update add {0!s}.openstack.hi.inet. 86400 IN A {1!s}\n"
		"send\n"
		"update delete {2!s}.in-addr.arpa. IN PTR\n"
		"update add {2!s}.in-addr.arpa. 86400 IN PTR {0!s}.openstack.hi.inet.\n"
		"send\n"
		).format(hostname,floating_ip,reverse_ip)
		cmd_nsupdate = 'sudo su -c "echo \\"{0!s}\\" | nsupdate -k {1!s}"'.format(query_nsupdate_insert,config.get("dns-epg-ns1-tic-key","dns_key"))
		ssh_result =  run_ssh_cmd(cmd_nsupdate,None,ssh_debug)
		if epg_debug : print ("["+str(datetime.now())+"] : " + "Executed: {0!s} with result [{1!s}]".format(query_nsupdate_insert,ssh_result))
	except socket.error : 
		if debug : print ("["+str(datetime.now())+"] : " + "Skipping this one : {0}".format(query_nsupdate_insert))
	except TypeError : 
		if debug : print ("["+str(datetime.now())+"] : " + "cursor_nova: Skipping this one due to Null values for hostname" + hostname)

cursor_nova.close()
cnx_nova.close()

#2013-07-26.14.22.47