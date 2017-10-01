import sys
from optparse import OptionParser
import conf


def main(argv):
    name = '.'.join(['bni', conf.module_name, 'init_db'])
    module = __import__(name)
    area_module = getattr(module, conf.module_name)
    init_db = getattr(area_module, 'init_db')
    init_db.setup()
