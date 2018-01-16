from datetime import date
from sqlalchemy.sql import func
from tools import (
    round_up,
    FixLength,
    DbTransactionID,
    )
from sismiop.db_tools import hitung_denda
from structure import INVOICE_ID
from conf import persen_denda


MAX_PORSI_DENDA = 0.48


class Query(object):
    def __init__(self, models, DBSession):
        self.models = models
        self.DBSession = DBSession

    def query_invoice(self, tahun, sptno):
        return self.DBSession.query(self.models.Invoice).filter_by(
                tahun=tahun, sptno=sptno)

    def get_payment(self, invoice):
        q = self.DBSession.query(self.models.Payment).filter_by(
                spt_id=invoice.id)
        q = q.order_by(self.models.Payment.id.desc())
        return q.first()

    def get_iso_payment(self, payment):
        q = self.DBSession.query(self.models.IsoPayment).filter_by(
                sspd_id=self.payment.id).\
                order_by(self.models.IsoPayment.id.desc())
        return q.first()


class NTP(DbTransactionID):
    # Override
    def is_found(self, trx_id):
        q = self.DBSession.query(self.models.IsoPayment).filter_by(ntp=trx_id)
        return q.first()


class Invoice(Query):
    def __init__(self, models, DBSession, invoice_id_raw):
        Query.__init__(self, models, DBSession)
        self.invoice_id_raw = invoice_id_raw
        self.invoice_id = FixLength(INVOICE_ID)
        self.invoice_id.set_raw(invoice_id_raw)
        q = self.query_invoice(self.invoice_id['Tahun'],
                self.invoice_id['SPT No'])
        self.invoice = q.first()

    def is_paid(self):
        return self.invoice.status_pembayaran == 1 or self.total <= 0

    def get_payment(self):
        return Query.get_payment(self, self.invoice)


class CalculateInvoice(Invoice):
    def __init__(self, models, DBSession, invoice_id_raw, persen_denda):
        Invoice.__init__(self, models, DBSession, invoice_id_raw)
        if not self.invoice:
            return
        self.persen_denda = persen_denda
        if self.invoice:
            self.hitung()
            self.paid = self.is_paid()
            if self.paid:
                self.payment = self.get_payment()

    def hitung(self):
        self.tagihan = round_up(self.invoice.pajak_terhutang - self.invoice.bunga)
        bln, self.denda = self.hitung_denda()
        self.denda = round_up(self.denda)
        self.total = self.tagihan + self.denda
        total_payment = self.get_total_payment()
        self.total -= total_payment

    def hitung_denda(self):
        bln, denda = hitung_denda(self.tagihan, self.invoice.jatuhtempotgl,
                        self.persen_denda)
        total_denda = denda + self.invoice.bunga
        max_denda = MAX_PORSI_DENDA * self.tagihan
        if total_denda > max_denda:
            return bln, max_denda
        return bln, total_denda

    def get_iso_payment(self):
        return Query.get_iso_payment(self, self.payment)

    def get_total_payment(self):
        q = self.DBSession.query(func.sum(self.models.Payment.jml_bayar).\
                label('jml')).filter_by(spt_id=self.invoice.id)
        pay = q.first()
        return pay and pay.jml or 0

    def get_op(self):
        q = self.DBSession.query(self.models.CustomerUsaha).\
                filter_by(id=self.invoice.customer_usaha_id)
        return q.first()

    def get_wp(self, op):
        q = self.DBSession.query(self.models.Customer).\
                filter_by(id=op.customer_id)
        return q.first()

    def get_kelurahan(self, id):
        q = self.DBSession.query(self.models.Kelurahan).filter_by(id=id)
        return q.first()

    def get_kecamatan(self, id):
        q = self.DBSession.query(self.models.Kecamatan).filter_by(id=id)
        return q.first()

    ###########
    # Payment #
    ###########
    def get_pay_id(self):
        return self.models.PaymentSeq.execute(self.DBSession.bind)

    def get_pay_seq(self):
        q = self.DBSession.query(self.models.Payment).filter_by(
                tahun=self.invoice.tahun).\
                order_by(self.models.Payment.sspdno.desc())
        pay = q.first()
        if pay:
            return pay.sspdno + 1
        return 1

    def set_paid(self):
        self.invoice.status_pembayaran = 1
        self.DBSession.add(self.invoice)


class Reversal(Invoice):
    def __init__(self, *args, **kwargs):
        Invoice.__init__(self, *args, **kwargs)
        self.payment = self.get_payment()

    def get_iso_payment(self):
        return Query.get_iso_payment(self, self.payment)

    def set_unpaid(self):
        self.invoice.status_pembayaran = 0
        self.DBSession.add(self.invoice)
        if self.payment:
            self.payment.jml_bayar = self.payment.denda = self.payment.bunga = 0
            self.DBSession.add(self.payment)
        self.DBSession.flush()
