import sys
sys.path[0:0] = ['/usr/share/opensipkd-forwarder/modules/bphtb_fix']
from bphtb_fix_db_transaction import BaseIsoReversal
from CalculateInvoice import (
    Common,
    query_invoice,
    DBSession,
    )
from models import (
    Payment,
    IsoPayment,
    IsoReversal,
    )
from DbTools import query_pembayaran


def pay2bayar(pay):
    q = query_pembayaran(pay.id)
    return q.first()


class ReversalCommon(object):
    def set_unpaid(self):
        self.invoice.status_bayar = 0
        self.bayar.jml_bayar = 0
        DBSession.add(self.bayar)
        DBSession.add(self.invoice)


class PaymentReversal(Common, ReversalCommon):
    def __init__(self, payment):
        self.payment = payment
        self.bayar = pay2bayar(payment)
        if not self.bayar:
            return
        q = query_invoice(self.bayar.no_tagihan)
        self.invoice = q.first()


class IsoPaymentReversal(BaseIsoReversal, PaymentReversal):
    def __init__(self, from_iso):
        BaseIsoReversal.__init__(self, from_iso)
        q = DBSession.query(IsoPayment).filter(
                IsoPayment.payment_id=Payment.id,
                Payment.no_tagihan=from_iso.get_invoice_id(),
                Payment.ntb=from_iso.get_ntb()).order_by(
                IsoPayment.id.desc())
        payment = q.first()
        PaymentReversal.__init__(self, payment)

    def set_unpaid(self):
        ReversalCommon.set_unpaid(self)
        reversal = IsoReversal()
        reversal.payment_id = self.payment.id
        reversal.iso_request = self.reversal_iso_request
        # Biarkan diisi tanggal saat ini. Toh untuk mendapatkan
        # settlement date bisa extract dari field iso_request.
        #reversal.tgl = tgl # settlement date
        DBSession.add(reversal)


class ReversalByQuery(PaymentReversal):
    def __init__(self, invoice_id):
        q = DBSession.query(IsoPayment).filter(
                IsoPayment.payment_id == Payment.id,
                Payment.no_tagihan == invoice_id).order_by(
                Payment.pembayaran_ke.desc()).limit(1)
        payment = q.first()
        PaymentReversal.__init__(self, payment)

    def set_unpaid(self):
        ReversalCommon.set_unpaid(self)
        DBSession.flush()
        DBSession.commit()
