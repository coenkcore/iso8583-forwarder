from tools import DbTransactionID


class Query(object):
    def __init__(self, models, DBSession):
        self.models = models
        self.DBSession = DBSession

    def query_invoice(self, no_tagihan):
        return self.DBSession.query(self.models.Invoice).\
                filter_by(source_id=2, no_tagihan=no_tagihan).\
                order_by(self.models.Invoice.tahun.desc())

    def get_payment(self, invoice):
        q = self.DBSession.query(self.models.Payment).\
                filter_by(invoice_id=invoice.id).\
                order_by(self.models.Payment.pembayaran_ke.desc())
        return q.first()

    def get_iso_payment(self, payment):
        q = self.DBSession.query(self.models.IsoPayment).filter_by(
                id=self.payment.id)
        return q.first()

    def get_payment_from_iso(self, iso_pay):
        q = self.DBSession.query(self.models.Payment).filter_by(
                id=iso_pay.payment_id)
        return q.first()


class NTP(DbTransactionID):
    # Override
    def is_found(self, trx_id):
        q = self.DBSession.query(self.models.Payment).filter_by(ntp=trx_id)
        return q.first()


class Invoice(Query):
    def __init__(self, models, DBSession, invoice_id_raw):
        Query.__init__(self, models, DBSession)
        self.invoice_id_raw = invoice_id_raw
        q = self.query_invoice(invoice_id_raw)
        self.invoice = q.first()

    def is_paid(self):
        return self.invoice.status_bayar == 1

    def get_payment(self):
        return Query.get_payment(self, self.invoice)


class CalculateInvoice(Invoice):
    def __init__(self, models, DBSession, invoice_id_raw):
        Invoice.__init__(self, models, DBSession, invoice_id_raw)
        if not self.invoice:
            return
        self.hitung()
        self.paid = self.is_paid() or self.tagihan < 1
        if self.paid:
            self.payment = self.get_payment()

    def hitung(self):
        self.tagihan = int(self.invoice.jml_tagihan)

    def get_iso_payment(self):
        if self.invoice and self.paid and self.payment:
            return Query.get_iso_payment(self, self.payment)

    def get_nop(self):
        return self.invoice and self.nop.get_raw() or ''

    def get_pay_seq(self):
        pay = self.get_payment()
        if pay:
            return pay.pembayaran_ke + 1
        return 1

    def set_paid(self):
        self.invoice.status_bayar = 1
        self.DBSession.add(self.invoice)


class Reversal(Invoice):
    def __init__(self, *args, **kwargs):
        Invoice.__init__(self, *args, **kwargs)
        self.payment = self.get_payment()

    def get_iso_payment(self):
        return Query.get_iso_payment(self, self.payment)

    def set_unpaid(self):
        self.invoice.status_bayar = 0
        self.DBSession.add(self.invoice)
        if self.payment:
            self.payment.jml_tagihan = 0
            self.DBSession.add(self.payment)
        self.DBSession.flush()
