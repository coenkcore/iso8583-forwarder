import sys
from datetime import date
from sqlalchemy.sql import func
from tools import (
    round_up,
    DbTransactionID,
    )
from sismiop.tools import hitung_denda


DEBUG = '--debug' in sys.argv


def print_debug(label, s):
    if DEBUG:
        print('*** DEBUG {l}: {s}'.format(l=label, s=s))


class Query(object):
    def __init__(self, models, DBSession):
        self.models = models
        self.DBSession = DBSession

    def query_invoice(self, invoice_id):
        return self.DBSession.query(self.models.Invoice).filter_by(
                kode=invoice_id)

    def query_payment(self, invoice):
        Payment = self.models.Payment
        return self.DBSession.query(Payment).filter_by(
                ar_invoice_id=invoice.id).filter(Payment.bayar > 0).\
                order_by(Payment.pembayaran_ke.desc())

    def get_payment(self, invoice):
        q = self.query_payment(invoice)
        return q.first()


SEQ_LENGTH = 6

class NTP(DbTransactionID):
    # Override
    def create(self, tgl):
        #besok = tgl + timedelta(1)
        y = str(tgl.year)
        m = str(tgl.month).zfill(2)
        like_pattern = '{y}{m}%'.format(y=y, m=m)
        Payment = self.models.Payment
        q = self.DBSession.query(Payment)
        q = q.filter(Payment.kode.like(like_pattern))
        #q = q.filter(Payment.tgl >= tgl).filter(Payment.tgl < besok).
        q = q.order_by(Payment.kode.desc())
        row = q.first()
        if row:
            last_seq = row.kode[SEQ_LENGTH:]
            new_seq = int(last_seq) + 1
        else:
            new_seq = 1
        return tgl.strftime('%Y%m') + str(new_seq).zfill(SEQ_LENGTH)


class Invoice(Query):
    def __init__(self, models, DBSession, invoice_id_raw):
        Query.__init__(self, models, DBSession)
        self.invoice_id_raw = invoice_id_raw
        q = self.query_invoice(self.invoice_id_raw)
        self.invoice = q.first()

    def get_payment(self):
        q = self.query_payment()
        return q.first()

    def query_payment(self):
        return Query.query_payment(self, self.invoice)

    def get_total_payment(self):
        q = self.DBSession.query(func.sum(self.models.Payment.bayar).label('jml')).\
                filter_by(ar_invoice_id=self.invoice.id)
        pay = q.first()
        return pay.jml or 0

    def is_paid(self):
        return self.invoice.status == 1


class CalculateInvoice(Invoice):
    def __init__(self, models, DBSession, invoice_id_raw, persen_denda):
        Invoice.__init__(self, models, DBSession, invoice_id_raw)
        self.persen_denda = persen_denda
        if not self.invoice:
            return
        if self.invoice:
            self.hitung()

    def hitung(self):
        bunga = self.invoice.bunga or 0
        bunga = round_up(bunga)
        self.tagihan = self.invoice.jumlah - bunga
        self.tagihan = round_up(self.tagihan)
        jth_tempo = self.invoice.jatuh_tempo==1 and self.invoice.jatuh_tempo or None
        bln, self.denda = hitung_denda(self.tagihan, jth_tempo,
                self.persen_denda)
        self.denda += bunga
        self.denda = round_up(self.denda)
        self.total = self.tagihan + self.denda
        total_pay = self.get_total_payment()
        if total_pay:
            self.total -= total_pay 
            self.paid = self.total <= 0
        else:
            self.paid = False

    def is_paid(self):
        return self.paid

    ###########
    # Payment #
    ###########
    def set_paid(self):
        self.invoice.status = 1
        self.DBSession.add(self.invoice)


class Reversal(Invoice):
    def __init__(self, *args, **kwargs):
        Invoice.__init__(self, *args, **kwargs)
        if self.invoice:
            self.payment = self.get_payment()

    def set_unpaid(self):
        self.invoice.status = 0
        self.DBSession.add(self.invoice)
        if self.payment:
            print_debug('bayar', self.payment.bayar)
            self.payment.bayar = 0
            self.DBSession.add(self.payment)
        self.DBSession.flush()
