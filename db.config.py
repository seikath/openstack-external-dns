# condigs here 
# 2013-07-31.13.58.03
import ConfigParser

config = ConfigParser.SafeConfigParser()
config.read('db.config')

print config.items('pdns')
print config.get('nova', 'host')

#print dict(x[1:] for x in reversed(config.items('pdns')))

	