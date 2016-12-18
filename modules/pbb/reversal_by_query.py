from optparse import OptionParser
import conf


def main(argv):
    help_force = 'tetap batalkan meski belum ada pembayaran'
    pars = OptionParser()
    pars.add_option('-i', '--invoice-id')
    pars.add_option('', '--force', action='store_true', help=help_force)
    option, remain = pars.parse_args(argv)
    name = '.'.join(['pbb', conf.module_name, 'ReversalByQuery'])
    module = __import__(name)
    area_module = getattr(module, conf.module_name)
    rbq_module = getattr(area_module, 'ReversalByQuery')
    ReversalByQuery = rbq_module.ReversalByQuery
    rbq = ReversalByQuery(option.invoice_id)
    if not rbq.invoice:
        print('Tagihan tidak ditemukan.')
        return
    if not rbq.is_paid() and not option.force:
        print('Status memang belum dibayar, tidak perlu dilanjutkan.')
        return
    if not rbq.payment and not option.force:
        print('Memang belum ada pembayaran, tidak perlu dilanjutkan.')
        print('Gunakan --force jika tetap ingin membuat tagihan menjadi belum '\
              'lunas.')
        return
    rbq.set_unpaid()
    print('Berhasil dibatalkan.')
