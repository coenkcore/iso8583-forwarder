import sys
from datetime import date
sys.path.insert(0, '/usr/share/opensipkd-forwarder/modules/bphtb_fix')
from bphtb_fix_db_transaction import BaseIsoReversal 
sys.path.insert(0, '/usr/share/opensipkd/modules')
from base_models import DBSession
from CalculateInvoice import (
    Common,
    CommonInvoice,
    query_invoice,
    get_last_payment,
    )
from models import (
    Payment,
    Invoice,
    IsoPayment,
    IsoReversal,
    )


class PaymentReversal(Common):
    def __init__(self, payment):
        self.payment = payment
        q = DBSession.query(Invoice).filter_by(id=payment.sspd_id)
        self.invoice = q.first()

    def set_unpaid(self):
        Common.set_unpaid(self)
        self.payment.bayar = self.payment.denda = 0
        DBSession.add(self.payment)


class IsoPaymentReversal(BaseIsoReversal, PaymentReversal):
    def __init__(self, from_iso):
        BaseIsoReversal.__init__(self, from_iso)
        q = DBSession.query(IsoPayment).filter_by(
                invoice_no = from_iso.get_invoice_id(),
                ntb = from_iso.get_ntb())
        self.iso_pay = q.first()
        if not self.iso_pay:
            return
        q = DBSession.query(Payment).filter_by(id=self.iso_pay.id)
        payment = q.first()
        PaymentReversal.__init__(self, payment)

    def is_reversal_ready(self):
        return self.iso_pay and self.payment and Common.is_paid(self)

    def set_unpaid(self):
        PaymentReversal.set_unpaid(self)
        reversal = IsoReversal()
        reversal.id = self.payment.id
        reversal.iso_request = self.reversal_iso_request
        DBSession.add(reversal)


class ReversalByQuery(CommonInvoice, PaymentReversal):
    def __init__(self, invoice_id):
        CommonInvoice.__init__(self, invoice_id)
        if self.invoice:
            payment = get_last_payment(self.invoice)
            if payment:
                PaymentReversal.__init__(self, payment)

    def set_unpaid(self):
        PaymentReversal.set_unpaid(self)
        DBSession.flush()
        DBSession.commit()
