from optparse import OptionParser
import conf


def main(argv):
    module_name = 'pbb'
    sample_count = 10
    pars = OptionParser()
    help_module = 'default {m}, other: bphtb, padl'.format(m=module_name)
    help_count = 'default {count}'.format(count=sample_count)
    pars.add_option('-m', '--module', default=module_name, help=help_module)
    pars.add_option('-c', '--sample-count', default=sample_count, help=help_count)
    option, remain = pars.parse_args(argv)
    module_name = option.module
    sample_count = int(option.sample_count)
    name = '.'.join(['multi', conf.module_name, module_name,
            'AvailableInvoice'])
    module = __import__(name)
    area_module = getattr(module, conf.module_name)
    sub_area_module = getattr(area_module, module_name)
    available_inv_module = getattr(sub_area_module, 'AvailableInvoice')
    AvailableInvoice = available_inv_module.AvailableInvoice
    ai = AvailableInvoice(int(option.sample_count))
    ai.show()
