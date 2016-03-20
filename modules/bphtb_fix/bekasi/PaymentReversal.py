import sys
from datetime import date
sys.path[0:0] = ['/usr/share/opensipkd-forwarder/modules/bphtb_fix']
from bphtb_fix_db_transaction import BaseIsoReversal 
sys.path[0:0] = ['/usr/share/opensipkd/modules']
from base_models import DBSession
from CalculateInvoice import (
    Common,
    query_invoice,
    )
from models import (
    OtherDBSession,
    Payment,
    Invoice,
    IsoPayment,
    IsoReversal,
    )


def get_last_payment(kd_booking):
    return OtherDBSession.query(Payment).filter_by(kd_booking=kd_booking).\
        order_by(Payment.pembayaran_bphtb_ke.desc()).first()


class ReversalCommon(object):
    def set_unpaid(self, tgl):
        self.invoice.status_bayar = '0'
        self.bayar.reversal = 1 
        self.bayar.tanggal_reversal = tgl 
        self.bayar.bphtb_di_bayar =  0
        OtherDBSession.add(self.bayar)
        OtherDBSession.add(self.invoice)
        OtherDBSession.flush()


class PaymentReversal(Common, ReversalCommon):
    def __init__(self, payment):
        self.payment = payment
        self.bayar = get_last_payment(payment.invoice_no)
        if not self.bayar:
            return
        q = query_invoice(payment.invoice_no)
        self.invoice = q.first()


class IsoPaymentReversal(BaseIsoReversal, PaymentReversal):
    def __init__(self, from_iso):
        BaseIsoReversal.__init__(self, from_iso)
        q = DBSession.query(IsoPayment).filter_by(
                invoice_no=from_iso.get_invoice_id(),
                ntb=from_iso.get_ntb())
        payment = q.first()
        PaymentReversal.__init__(self, payment)

    def set_unpaid(self):
        tgl = self.from_iso.get_settlement_date()
        PaymentReversal.set_unpaid(self, tgl)
        reversal = IsoReversal()
        reversal.id = self.payment.id
        reversal.iso_request = self.reversal_iso_request
        DBSession.add(reversal)


class ReversalByQuery(PaymentReversal):
    def __init__(self, invoice_id):
        q = DBSession.query(IsoPayment).filter_by(invoice_no=invoice_id).\
                order_by('id DESC').limit(1)
        payment = q.first()
        PaymentReversal.__init__(self, payment)

    def set_unpaid(self):
        tgl = date.today()
        PaymentReversal.set_unpaid(self, tgl)
        OtherDBSession.commit()
