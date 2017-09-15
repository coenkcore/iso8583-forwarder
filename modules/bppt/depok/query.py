from sqlalchemy import func
from tools import (
    round_up,
    DbTransactionID,
    )


class BaseQuery(object):
    def __init__(self, models, DBSession):
        self.models = models
        self.DBSession = DBSession


class OtherQuery(BaseQuery):
    def query_invoice(self, invoice_id_raw):
        return self.DBSession.query(self.models.Invoice).filter_by(
                no_bayar=invoice_id_raw).order_by(
                self.models.Invoice.date_entry.desc())

    def get_payment(self, invoice):
        q = self.query_payment(invoice)
        return q.first()

    def query_payment(self, invoice):
        q = self.DBSession.query(self.models.Payment)
        return self.filter_payment(q, invoice)
 
    def filter_payment(self, q, invoice):
         return q.filter_by(id_pendaftaran=invoice.id_pendaftaran)


class NTP(DbTransactionID):
    # Override
    def is_found(self, trx_id):
        q = self.DBSession.query(self.models.IsoPayment).filter_by(ntp=trx_id)
        return q.first()


class Invoice(OtherQuery):
    def __init__(self, models, DBSession, invoice_id_raw):
        OtherQuery.__init__(self, models, DBSession)
        self.invoice_id_raw = invoice_id_raw
        q = self.query_invoice(invoice_id_raw)
        self.invoice = q.first()


class CalculateInvoice(Invoice):
    def __init__(self, *args, **kwargs):
        Invoice.__init__(self, *args, **kwargs)
        if self.invoice:
            self.hitung()
            self.paid = self.is_paid()

    def hitung(self):
        self.tagihan = self.invoice.nominal and round_up(self.invoice.nominal) or 0
        self.denda = self.invoice.denda and round_up(self.invoice.denda) or 0
        self.total = self.tagihan + self.denda

    def is_paid(self):
        q = self.DBSession.query(func.sum(self.models.Payment.jumlah_bayar).\
                label('bayar'))
        q = self.filter_payment(q, self.invoice)
        pay = q.first()
        total_bayar = pay.bayar or 0
        return total_bayar >= self.total


FIELD_ARSIP = ('no_ssrd', 'date_ssrd', 'no_sts', 'date_sts', 'jumlah_bayar',
    'cara_bayar', 'ref_bayar', 'date_bayar')


class Reversal(CalculateInvoice):
    def __init__(self, *args, **kwargs):
        CalculateInvoice.__init__(self, *args, **kwargs)
        self.payment = self.get_payment()

    # Override
    def get_payment(self):
        if self.invoice:
            return CalculateInvoice.get_payment(self, self.invoice)

    def set_unpaid(self, arsip=None):
        if arsip:
            self.arsip(arsip)
        q = self.query_payment(self.invoice)
        q.delete()
        self.DBSession.flush()

    def arsip(self, row):
        source = self.payment.to_dict()
        target = dict()
        for field in FIELD_ARSIP:
            if field in source:
                target[field] = source[field]
        row.from_dict(target)


class Query(BaseQuery):
    def get_izin_by_name(self, nama):
        q = self.DBSession.query(self.models.Izin).filter_by(nama=nama)
        return q.first()

    def get_iso_payment(self, pay):
        q = self.DBSession.query(self.models.IsoPayment).filter_by(
                id_pendaftaran=pay.id_pendaftaran).order_by(
                self.models.IsoPayment.id.desc())
        return q.first()
