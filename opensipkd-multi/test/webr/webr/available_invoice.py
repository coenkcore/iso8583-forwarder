import sys
sys.path[0:0] = ['/usr/share/opensipkd/modules']
from base_models import DBSession
sys.path[0:0] = ['/usr/share/opensipkd-forwarder/modules/bca']
from log_models import Payment
sys.path[0:0] = ['/usr/share/opensipkd-forwarder/modules/bca/padl']
from padl_models import Invoice
from padl_calculate_invoice import CalculateInvoice
#from bphtb_db_transaction import sppt2nop


class AvailableInvoice(object):
    def __init__(self, sample_count=100, jenis=None):
        self.sample_count = sample_count
        self.jenis = jenis

    def show(self):
        q = DBSession.query(Invoice).filter_by(status_pembayaran = '0')
        # q = q.filter(Invoice.pbb_yg_harus_dibayar_sppt >= 100,
                     # Invoice.pbb_yg_harus_dibayar_sppt < 1000)
        q = q.order_by(Invoice.tahun.desc(),
                       Invoice.nospt)
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
