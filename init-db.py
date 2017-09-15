import sys


sys.path.insert(0, 'modules')
if not sys.argv[1:]:
    print('Caranya: {c} <module>'.format(c=sys.argv[0]))
    sys.exit()
argv = sys.argv[1:]
module_name = argv[0]
name = module_name + '.init_db'
module = __import__(name)
sub_module = getattr(module, 'init_db')
sub_module.main(argv[1:])
