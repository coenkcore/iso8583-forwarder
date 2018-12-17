import sys
from optparse import OptionParser
from config import module_name 


def main(argv):
    name = '.'.join(['bphtb', module_name, 'init_db'])
    module = __import__(name)
    area_module = getattr(module, module_name)
    init_db = getattr(area_module, 'init_db')
    init_db.setup()
