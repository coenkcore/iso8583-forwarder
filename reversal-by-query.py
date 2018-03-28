import sys
import os


sys.path.insert(0, 'modules')
module_name = sys.argv[1]
name = module_name + '.reversal_by_query'
module = __import__(name)
sub_module = getattr(module, 'reversal_by_query')
sub_module.main(sys.argv[2:])