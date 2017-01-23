from datetime import date
from sqlalchemy.sql import func
from tools import (
    round_up,
    FixLength,
    DbTransactionID,
    )
from common.pbb.structure import NOP
from sismiop.tools import hitung_denda
from conf import persen_denda


class Query(object):
    def __init__(self, models, DBSession):
        self.models = models
        self.DBSession = DBSession

    def query_invoice(self, tahun, kode, no_sspd):
        return self.DBSession.query(self.models.Invoice).filter_by(tahun=tahun,
                kode=kode, no_sspd=no_sspd)

    def get_payment(self, invoice):
        q = self.DBSession.query(self.models.Payment).filter_by(
                sspd_id=invoice.id)
        q = q.order_by(self.models.Payment.id.desc())
        return q.first()

    def get_iso_payment(self, payment):
        q = self.DBSession.query(self.models.IsoPayment).filter_by(
                id=self.payment.id)
        return q.first()


class NTP(DbTransactionID):
    # Override
    def is_found(self, trx_id):
        q = self.DBSession.query(self.models.IsoPayment).filter_by(ntp=trx_id)
        return q.first()


class Invoice(Query):
    def __init__(self, models, DBSession, invoice_id):
        Query.__init__(self, models, DBSession)
        self.invoice_id = invoice_id 
        self.invoice = False 
        try:
            kode = int(self.invoice_id['Kode'])
        except TypeError:
            return
        except ValueError:
            return
        q = self.query_invoice(self.invoice_id['Tahun'], str(kode),
                self.invoice_id['SSPD No'])
        self.invoice = q.first()

    def is_paid(self):
        return self.invoice.status_pembayaran == 1

    def get_payment(self):
        return Query.get_payment(self, self.invoice)


class CalculateInvoice(Invoice):
    def __init__(self, models, DBSession, invoice_id, persen_denda):
        Invoice.__init__(self, models, DBSession, invoice_id)
        if not self.invoice:
            return
        self.persen_denda = persen_denda
        self.nop = FixLength(NOP)
        self.nop.from_dict({
            'Propinsi': self.invoice.kd_propinsi,
            'Kabupaten': self.invoice.kd_dati2,
            'Kecamatan': self.invoice.kd_kecamatan,
            'Kelurahan': self.invoice.kd_kelurahan,
            'Blok': self.invoice.kd_blok,
            'Urut': self.invoice.no_urut,
            'Jenis': self.invoice.kd_jns_op,
            })
        self.hitung()
        self.paid = self.is_paid() or self.total < 1
        if self.paid:
            self.payment = self.get_payment()

    def hitung(self):
        self.tagihan = round_up(self.invoice.bphtb_harus_dibayarkan)
        bln, self.denda = hitung_denda(self.tagihan,
            self.invoice.tgl_jatuh_tempo.date(), self.persen_denda)
        self.denda = round_up(self.denda)
        self.total = self.tagihan + self.denda

    def get_iso_payment(self):
        if not self.invoice or not self.paid or not self.payment:
            return
        return Query.get_iso_payment(self, self.payment)

    def get_nop(self):
        return self.invoice and self.nop.get_raw() or ''

    def get_customer(self):
        q = self.DBSession.query(self.models.Customer).filter_by(
                id=self.invoice.ppat_id)
        return q.first()

    def get_kecamatan(self):
        q = self.DBSession.query(self.models.Kecamatan).filter_by(
                kd_propinsi = self.invoice.kd_propinsi,
                kd_dati2 = self.invoice.kd_dati2,
                kd_kecamatan = self.invoice.kd_kecamatan)
        return q.first()

    def get_kelurahan(self):
        q = self.DBSession.query(self.models.Kelurahan).filter_by(
                kd_propinsi = self.invoice.kd_propinsi,
                kd_dati2 = self.invoice.kd_dati2,
                kd_kecamatan = self.invoice.kd_kecamatan,
                kd_kelurahan = self.invoice.kd_kelurahan)
        return q.first()

    def get_pay_seq(self):
        q = self.DBSession.query(self.models.Payment).filter_by(
                sspd_id=self.invoice.id)
        pay = q.first()
        if pay:
            return pay.pembayaran_ke + 1
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
            self.payment.bayar = self.payment.denda = 0
            self.DBSession.add(self.payment)
        self.DBSession.flush()
