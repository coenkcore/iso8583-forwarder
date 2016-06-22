import sys


sys.path.insert(0, 'modules')
if sys.argv[1:]:
    argv = sys.argv[1:]
else:
    argv = ['pbb']
module_name = argv[0]
name = module_name + '.available_invoice'
module = __import__(name)
sub_module = getattr(module, 'available_invoice')
sub_module.main(argv[1:])
