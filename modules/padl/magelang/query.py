from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from tools import round_up
from db_tools import hitung_denda
from config import (
    db_url,
    db_pool_size,
    db_max_overflow,
    persen_denda,
    )
from .models import (
    Customer,
    CustomerUsaha,
    Rekening,
    Pajak,
    Invoice,
    Payment,
    IsoPayment,
    )


MAX_PORSI_DENDA = 0.48

engine = create_engine(
    db_url, pool_size=db_pool_size, max_overflow=db_max_overflow)
session_factory = sessionmaker(bind=engine)


# Hanya ambil 2 digit di belakang koma
def float_(n):
    return int(n * 100) / 100.0


class Query:
    def __init__(self):
        self.DBSession = session_factory()

    def query_invoice(self, tahun, sptno):
        q = self.DBSession.query(Invoice).filter_by(
                tahun=self.tahun, sptno=self.sptno)
        return q.order_by(Invoice.id.desc())

    def get_invoice(self, tahun, sptno):
        q = self.query_invoice(tahun, sptno)
        return q.first()

    def is_paid(self, invoice):
        return invoice.status_pembayaran == 1

    def get_customer(self, invoice):
        q = self.DBSession.query(CustomerUsaha).filter_by(
                id=invoice.customer_usaha_id)
        cust_usaha = q.first()
        q = self.DBSession.query(Customer).filter_by(
                id=cust_usaha.customer_id)
        return q.first()

    def get_rekening(self, invoice):
        q = self.DBSession.query(Pajak).filter_by(id=invoice.pajak_id)
        pajak = q.first()
        q = self.DBSession.query(Rekening).filter_by(id=pajak.rekening_id)
        return q.first()

    def get_payment(self, invoice):
        q = self.DBSession.query(Payment).filter_by(
                spt_id=invoice.id, enabled=1).order_by(
                Payment.sspdno.desc())
        return q.first()

    def get_new_sspdno(self, invoice):
        q = self.DBSession.query(Payment).filter_by(tahun=invoice.tahun).\
                order_by(Payment.sspdno.desc())
        pay = q.first()
        if pay:
            return pay.sspdno + 1
        return 1


class InvoiceQuery(Query):
    def __init__(self, tahun, sptno):
        Query.__init__(self)
        self.tahun = tahun
        self.sptno = sptno
        self.invoice = self.get_invoice()

    def get_invoice(self):
        return Query.get_invoice(self, self.tahun, self.sptno)

    def is_paid(self):
        return Query.is_paid(self, self.invoice)

    def get_customer(self):
        return Query.get_customer(self, self.invoice)

    def get_rekening(self):
        return Query.get_rekening(self, self.invoice)

    def get_new_sspdno(self):
        return Query.get_new_sspdno(self, self.invoice)

    def set_paid(self, total, denda):
        sspdno = self.get_new_sspdno()
        pay = Payment()
        pay.tahun = self.tahun
        pay.sspdno = sspdno
        pay.spt_id = self.invoice.id
        pay.sspdtgl = pay.create_date = pay.write_date = datetime.now()
        pay.denda = pay.bunga = denda
        pay.jml_bayar = total
        pay.printed = pay.enabled = self.invoice.status_pembayaran = 1
        self.DBSession.add(pay)
        self.DBSession.add(self.invoice)
        self.DBSession.flush()
        return pay

    def get_payment(self):
        return Query.get_payment(self, self.invoice)

    def set_unpaid(self, pay=None):
        if not pay:
            pay = self.get_payment()
        if pay:
            pay.enabled = 0
            self.DBSession.add(pay)
        self.invoice.status_pembayaran = 0
        self.DBSession.add(self.invoice)
        self.DBSession.flush()


class CalculateInvoice(InvoiceQuery):
    def __init__(self, tahun, sptno):
        InvoiceQuery.__init__(self, tahun, sptno)
        if self.invoice:
            self.hitung()

    def is_paid(self):
        return InvoiceQuery.is_paid(self) or self.total < 1

    def hitung(self):
        self.tagihan = self.hitung_tagihan()
        self.tagihan = round_up(self.tagihan)
        self.denda = self.hitung_denda()
        self.denda = round_up(self.denda)
        self.total = self.tagihan + self.denda

    def hitung_tagihan(self):
        return self.invoice.dasar * self.invoice.tarif \
               + self.invoice.denda \
               + self.invoice.kenaikan - self.invoice.kompensasi \
               + self.invoice.lain2 - self.invoice.setoran

    def hitung_denda(self):
        bulan, denda = hitung_denda(
            self.tagihan, self.invoice.jatuhtempotgl, persen_denda)
        denda = float_(denda)
        total_denda = denda + self.invoice.bunga
        max_denda = MAX_PORSI_DENDA * self.tagihan
        if total_denda > max_denda:
            return max_denda
        return total_denda

    def set_paid(self):
        return InvoiceQuery.set_paid(self, self.total, self.denda)
