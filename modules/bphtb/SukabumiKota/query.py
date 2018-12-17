from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
from tools import round_up
from .models import (
    Invoice,
    Payment,
    )
from config import (
    bphtb as conf,
    db_pool_size,
    db_max_overflow,
    )


engine = create_engine(
            conf['db_url'], pool_size=db_pool_size,
            max_overflow=db_max_overflow)
session_factory = sessionmaker(bind=engine)


class Query:
    def __init__(self):
        self.session = session_factory()

    def query_invoice(self, invoice_id):
        return self.session.query(Invoice).filter_by(no_tagihan=invoice_id)

    def get_invoice(self, invoice_id):
        q = self.query_invoice(invoice_id)
        return q.first()

    def get_payment(self, invoice):
        q = self.session.query(Payment).filter_by(id_tagihan=invoice.id)
        q = q.order_by(Payment.id.desc())
        return q.first()
    
    def sum_payment(self, invoice):
        return self.session.query(func.sum(Payment.jumlah_yg_dibayar)).\
                filter(Payment.id_tagihan==invoice.id).scalar()

    def is_paid(self, invoice):
        return invoice.status_pembayaran == 1

    def commit(self):
        self.session.flush()
        self.session.commit()


class InvoiceQuery(Query):
    def __init__(self, invoice_id):
        Query.__init__(self)
        self.invoice_id = invoice_id 
        self.invoice = self.get_invoice()

    def get_invoice(self):
        return Query.get_invoice(self, self.invoice_id)

    def is_paid(self):
        return Query.is_paid(self, self.invoice)

    def get_payment(self):
        return Query.get_payment(self, self.invoice)

    def sum_payment(self):
        return Query.sum_payment(self, self.invoice)


class CalculateInvoice(InvoiceQuery):
    def __init__(self, invoice_id):
        InvoiceQuery.__init__(self, invoice_id)
        if not self.invoice:
            return
        self.hitung()
        if self.is_paid():
            self.payment = self.get_payment()

    def is_paid(self):
        return InvoiceQuery.is_paid(self) or self.total < 1

    def hitung(self):
        self.tagihan = round_up(self.invoice.bphtb_hrs_bayar)
        payment = self.sum_payment()
        if payment :
            self.tagihan -= payment
        self.denda = self.invoice.jumlah_denda and \
            round_up(self.invoice.jumlah_denda) or 0
        self.total = self.tagihan + self.denda

    def set_paid(self, **kwargs):
        tgl_bayar = kwargs['tgl_bayar']
        self.invoice.status_pembayaran = 1
        self.session.add(self.invoice)
        pay = Payment()
        pay.id_tagihan = self.invoice.id
        pay.jumlah_yg_dibayar = self.total
        pay.tgl_pembayaran = tgl_bayar 
        pay.tgl_rekam = datetime.now()
        self.session.add(pay)
        self.commit()
        return pay
        

class Reversal(InvoiceQuery):
    def __init__(self, invoice_id):
        InvoiceQuery.__init__(self, invoice_id)
        if self.invoice:
            self.payment = self.get_payment()

    def set_unpaid(self, amount=None):
        self.invoice.status_pembayaran = 0
        self.session.add(self.invoice)
        if self.payment:
            if not amount or amount == self.payment.jumlah_yg_dibayar:
                self.payment.jumlah_yg_dibayar = 0
                self.session.add(self.payment)
        self.commit()
