import sys
from optparse import OptionParser
import conf


def main(argv):
    name = '.'.join(['pbb', conf.module_name, 'AvailableInvoice'])
    module = __import__(name)
    area_module = getattr(module, conf.module_name)
    available_inv_module = getattr(area_module, 'AvailableInvoice')
    AvailableInvoice = available_inv_module.AvailableInvoice
    ai = AvailableInvoice()
    pars = OptionParser()
    sample_count = 10
    help_count = 'default {count}'.format(count=sample_count)
    pars.add_option('-c', '--sample-count', default=sample_count,
        help=help_count)
    option, remain = pars.parse_args(argv)
    ai.show(option)
