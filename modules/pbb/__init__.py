import sys
sys.path[0:0] = ['/etc/opensipkd']
from pbb_conf import module_name
sys.path[0:0] = ['/usr/share/opensipkd-forwarder/modules/pbb']

print('Module: ' + module_name)
module = __import__(module_name)
DbTransaction = module.DbTransaction
