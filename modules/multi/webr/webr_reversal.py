import sys
sys.path[0:0] = ['/usr/share/opensipkd-forwarder/modules/bca/']
from webr import WebrDBSession
from webr.webr_models import Pembayaran, Invoice
from webr.webr_structure import  INVOICE_ID, INVOICE_PROFILE 
#from webr.webr_calculate_invoice import Common
from log_models import MyFixLength

def pay2bayar(inv,pay):
    q = WebrDBSession.query(Pembayaran).filter_by(
                arinvoice_id = inv.id,
                pembayaran_ke = pay.ke
                )
    return q.first()

def pay2invoice(invoice_id):
    q = WebrDBSession.query(Invoice).filter_by(
                kode = invoice_id,
                )
    return q.first() 
    
class ReversalCommon(object):
    def set_unpaid(self):
        self.invoice.status_bayar = 0
        self.bayar.bayar = 0 
        self.bayar.bunga = 0

class WebrReversal(ReversalCommon):
    def __init__(self, pay):
        self.invoice_id = MyFixLength(INVOICE_ID)
        self.pay = pay
        self.invoice_id.set_raw(pay.invoice_id)
        self.invoice = pay2invoice(pay.invoice_id)
        if not self.invoice:
            return
        self.bayar = pay2bayar(self.invoice,pay)
        
    def is_paid(self):
        return int(self.invoice.status_bayar)
    
    def commit(self):
        WebrDBSession.add(self.invoice)
        WebrDBSession.add(self.bayar)
        WebrDBSession.flush()
        WebrDBSession.commit()
