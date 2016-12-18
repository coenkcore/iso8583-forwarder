from optparse import OptionParser
import conf


def main(argv):
    help_force = 'tetap batalkan meski belum ada pembayaran'
    pars = OptionParser()
    pars.add_option('-i', '--invoice-id')
    option, remain = pars.parse_args(argv)
    name = '.'.join(['pbb', conf.module_name, 'InquiryByQuery'])
    module = __import__(name)
    area_module = getattr(module, conf.module_name)
    ibq_module = getattr(area_module, 'InquiryByQuery')
    InquiryByQuery = ibq_module.InquiryByQuery
    ibq = InquiryByQuery(option.invoice_id)
    if not ibq.invoice:
        print('Tagihan tidak ditemukan.')
        return
    s = 'Atas nama ' + ibq.nama_wp
    if ibq.is_paid():
        s += ', sudah dibayar, '
    else:
        s += ', belum dibayar'
    if ibq.payment:
        if not ibq.is_paid():
            s += ', namun ada pembayaran '
        s += 'pada tanggal {tgl} senilai Rp {total}'.format(
                tgl=ibq.tgl_bayar.strftime('%d-%m-%Y'), total=int(ibq.total))
        if ibq.tempat_pembayaran:
            s += ', melalui ' + ibq.tempat_pembayaran['nama']
            if 'alamat' in ibq.tempat_pembayaran:
                s += ' - ' + ibq.tempat_pembayaran['alamat']
    if ibq.h2h:
        s += '\n'
        if not ibq.is_paid():
            s += 'namun ada '
        s += 'catatan pembayaran di host to host pada\n'
    elif ibq.payment:
        s += ', bukan host to host'
    for d in ibq.h2h:
        s += '  {tgl} {ket} Rp {total}\n'.format(
                tgl=d['tgl'].strftime('%d-%m-%Y'),
                ket=d['ket'], total=d['total'])
    if ibq.ket:
        s += ', ' + ibq.ket
    print(s)
