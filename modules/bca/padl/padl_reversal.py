import sys
sys.path[0:0] = ['/usr/share/opensipkd-forwarder/modules/bca/']
from padl import PadlDBSession
from padl.padl_models import Pembayaran, Invoice
from padl.padl_structure import INVOICE_ID, INVOICE_PROFILE
#from padl.padl_calculate_invoice import Common
from log_models import MyFixLength

def _pay2bayar(invoice_id):
    return PadlDBSession.query(Pembayaran).filter_by(
                spt_id = invoice_id,
                enabled = 1
                )
def pay2bayar(pay):
    q = _pay2bayar(pay.id)
    #q = q.filter_by(pembayaran_ke=pay.ke)
    return q.first()

def pay2invoice(invoice_id):
    q = PadlDBSession.query(Invoice).filter_by(
                tahun = invoice_id['tahun'],
                #kode = invoice_id['kode'][-1],
                sptno = invoice_id['spt_no'])
    return q.first() 
    
class ReversalCommon(object):
    def set_unpaid(self):
        self.invoice.status_pembayaran = 0
        self.bayar.jml_bayar = 0 
        self.bayar.denda = 0
        self.bayar.bunga = 0
        self.bayar.enabled = 0

class PadlReversal(ReversalCommon):
    def __init__(self, pay):
        self.invoice_id = MyFixLength(INVOICE_ID)
        self.pay = pay
        self.invoice_id.set_raw(pay.invoice_id)
        self.invoice = pay2invoice(self.invoice_id)
        if not self.invoice:
            return
        self.bayar = pay2bayar(self.invoice)
        
    def is_paid(self):
        return int(self.invoice.status_pembayaran)
    
    def commit(self):
        PadlDBSession.add(self.invoice)
        PadlDBSession.add(self.bayar)
        PadlDBSession.flush()
        PadlDBSession.commit()

        

