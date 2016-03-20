import sys
sys.path.insert(0, '/usr/share/opensipkd/modules')
from base_models import DBSession
from models import (
    IsoPayment,
    Invoice,
    )
from CalculateInvoice import (
    Common,
    get_invoice,
    )


class ReversalCommon(object):
    def set_unpaid(self):
        self.invoice.status_bayar = 0
        if self.payment:
            self.payment.tagihan = 0
            self.payment.denda = 0
            self.payment.total_bayar = 0

class PaymentReversal(Common, ReversalCommon):
    def __init__(self, payment):
        self.payment = payment
        q = DBSession.query(Invoice).filter_by(id=payment.invoice_id)
        self.invoice = q.first()

class ReversalByQuery(Common, ReversalCommon):
    def __init__(self, invoice_id):
        self.invoice = get_invoice(invoice_id)
        if self.invoice:
            q = DBSession.query(IsoPayment).filter_by(invoice_id=self.invoice.id).\
                    order_by(IsoPayment.id.desc())
            self.payment = q.first()
        else:
            self.payment = None
