import sys
sys.path[0:0] = ['/etc/opensipkd']
from bphtb_fix_conf import module_name
sys.path[0:0] = ['/usr/share/opensipkd-forwarder/modules/bphtb_fix']
 
print('Module: ' + module_name)
module = __import__(module_name)
DbTransaction = module.DbTransaction
