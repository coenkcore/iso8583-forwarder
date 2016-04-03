import sys
# from CalculateInvoice import (
    # Common,
    # query_sppt,
    # )
#from DbTools import query_pembayaran
sys.path[0:0] = ['/usr/share/opensipkd-forwarder/modules/bca/']
from bphtb import BphtbDBSession
from bphtb.bphtb_models import Pembayaran, Invoice
from bphtb.bphtb_fix_structure import INVOICE_ID, INVOICE_PROFILE
from bphtb.bphtb_calculate_invoice import Common
from log_models import MyFixLength

sys.path[0:0] = ['/usr/share/opensipkd/modules']

def _pay2bayar(invoice_id):
    return BphtbDBSession.query(Pembayaran).filter_by(
                no_tagihan = invoice_id
                )
def pay2bayar(pay):
    q = _pay2bayar(pay.invoice_id)
    q = q.filter_by(pembayaran_ke=pay.ke)
    return q.first()


def pay2invoice(invoice_id):
    q = BphtbDBSession.query(Invoice).filter_by(
                tahun = invoice_id['tahun'],
                kode = invoice_id['kode'][-1],
                no_sspd = invoice_id['no_urut'])
    return q.first() 

class ReversalCommon(object):
    def set_unpaid(self):
        self.invoice.status_pembayaran = 0
        self.bayar.bayar = 0 
        self.bayar.denda = 0

class BphtbReversal(Common, ReversalCommon):
    def __init__(self, pay):
        self.invoice_id = MyFixLength(INVOICE_ID)
        self.pay = pay
        self.invoice_id.set_raw(pay.invoice_id)
        self.bayar = pay2bayar(pay)
        if not self.bayar:
            return
        self.invoice = pay2invoice(self.invoice_id)
        
    def is_paid(self):
        return int(self.invoice.status_pembayaran)
    
    def commit(self):
        BphtbDBSession.add(self.invoice)
        BphtbDBSession.add(self.bayar)
        BphtbDBSession.flush()
        BphtbDBSession.commit()

class BphtbReversalByQuery(Common, ReversalCommon):
    def __init__(self, invoice_id):
        q = pay2invoice(invoice_id)
        self.invoice = q.first()
        if not self.invoice:
            return
        q = _pay2bayar(invoice_id.get_raw())
        q = q.order_by('pembayaran_ke DESC')
        self.bayar = q.first()
