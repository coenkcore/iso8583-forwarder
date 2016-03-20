import sys
sys.path.insert(0, '/etc/opensipkd')
from padl_fix_conf import module_name
sys.path.insert(0, '/usr/share/opensipkd-forwarder/modules/padl_fix')
  
print('Module: ' + module_name)
module = __import__(module_name)
DbTransaction = module.DbTransaction
