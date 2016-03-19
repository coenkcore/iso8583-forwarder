import sys
sys.path[0:0] = ['/usr/share/opensipkd/modules']
from base_models import DBSession
sys.path[0:0] = ['/usr/share/opensipkd-forwarder/modules/pbb']
from pbb_models import Payment
sys.path[0:0] = ['/usr/share/opensipkd-forwarder/modules/pbb/cikarang']
from models import Invoice
from CalculateInvoice import CalculateInvoice
from DbTransaction import sppt2nop


class AvailableInvoice(object):
    def __init__(self, sample_count=100, jenis=None):
        self.sample_count = sample_count
        self.jenis = jenis

    def show(self):
        q = DBSession.query(Invoice).filter_by(status_pembayaran_sppt = '0')
        q = q.filter(Invoice.pbb_yg_harus_dibayar_sppt >= 1000,
                     Invoice.pbb_yg_harus_dibayar_sppt < 10000)
        q = q.order_by(Invoice.thn_pajak_sppt.desc(),
                       Invoice.pbb_yg_harus_dibayar_sppt)
        offset = -1
        count = 0
        while True:
            if count >= self.sample_count:
                break
            offset += 1
            row = q.offset(offset).first()
            if not row:
                break
            calc = CalculateInvoice(row.kd_propinsi,
                    row.kd_dati2,
                    row.kd_kecamatan,
                    row.kd_kelurahan,
                    row.kd_blok,
                    row.no_urut,
                    row.kd_jns_op,
                    row.thn_pajak_sppt)
            if calc.total < 1:
                continue
            count += 1
            invoice_id_raw = sppt2nop(calc.invoice) + calc.invoice.thn_pajak_sppt 
            msg = '#{no}/{count} {id} Rp {total}'.format(no=count,
                    id=invoice_id_raw, total=calc.total,
                    count=self.sample_count)
            print(msg)
