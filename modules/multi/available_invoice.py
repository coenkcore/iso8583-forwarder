import sys
from optparse import OptionParser
from .conf import module_name as conf_module_name


def main(argv):
    if not argv:
        print('Caranya: {c} multi <module>'.format(c=sys.argv[0]))
        return
    module_name = argv[0]
    argv = argv[1:]
    name = '.'.join(['multi', conf_module_name, module_name,
            'AvailableInvoice'])
    module = __import__(name)
    area_module = getattr(module, conf_module_name)
    sub_area_module = getattr(area_module, module_name)
    available_inv_module = getattr(sub_area_module, 'AvailableInvoice')
    AvailableInvoice = available_inv_module.AvailableInvoice
    ai = AvailableInvoice()
    pars = OptionParser()
    sample_count = 40
    help_count = 'default {count}'.format(count=sample_count)
    pars.add_option('-c', '--sample-count', default=sample_count,
        help=help_count)
    try:
        add_option = getattr(ai, 'add_option')
        add_option(pars)
    except AttributeError:
        pass
    option, remain = pars.parse_args(argv)
    sample_count = int(option.sample_count)
    ai.show(option)
