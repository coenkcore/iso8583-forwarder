import sys
import os


sys.path.insert(0, 'modules')
module_name = sys.argv[1]
name = module_name + '.test_payment'
module = __import__(name)
sub_module = getattr(module, 'test_payment')
sub_module.main(sys.argv[2:])
