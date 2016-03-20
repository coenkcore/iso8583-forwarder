import sys
from datetime import datetime
from sqlalchemy.sql import func
sys.path.insert(0, '/usr/share/opensipkd/modules')
from tools import (
    round_up,
    FixLength,
    )
from base_models import DBSession
sys.path.insert(0, '/usr/share/opensipkd-forwarder/modules/bphtb_fix')
from bphtb_fix_structure import NOP
from models import (
    Invoice,
    Payment,
    IsoPayment,
    )
from structure import INVOICE_ID
sys.path.insert(0, '/etc/opensipkd')
from bphtb_fix_conf import persen_denda


def query_invoice(tahun, kode, no_sspd):
    return DBSession.query(Invoice).filter_by(
            tahun = tahun, kode = kode, no_sspd = no_sspd)

def get_last_payment(invoice):
    q = DBSession.query(Payment).filter_by(sspd_id=invoice.id)
    q = q.order_by(Payment.id.desc())
    return q.first()


class Common(object):
    def is_paid(self):
        return self.invoice.status_pembayaran == 1

    def set_paid(self):
        self.invoice.status_pembayaran = 1
        DBSession.add(self.invoice)

    def set_unpaid(self):
        self.invoice.status_pembayaran = 0
        DBSession.add(self.invoice)


class CommonInvoice(Common):
    def __init__(self, invoice_id):
        self.invoice_id = invoice_id
        self.invoice_struct = FixLength(INVOICE_ID)
        self.invoice_struct.set_raw(invoice_id)
        q = query_invoice(self.invoice_struct['Tahun'],
                str(int(self.invoice_struct['Kode'])),
                self.invoice_struct['SSPD No'])
        self.invoice = q.first()


class CalculateInvoice(CommonInvoice):
    def __init__(self, invoice_id):
        CommonInvoice.__init__(self, invoice_id)
        if not self.invoice:
            return
        self.nop_struct = FixLength(NOP)
        self.nop_struct.from_dict({
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
            # Dapatkan NTPD untuk bit 57
            self.payment = self.get_payment()

    def hitung(self):
        kini = datetime.now()
        jatuh_tempo = self.invoice.tgl_jatuh_tempo
        self.tagihan = round_up(self.invoice.bphtb_harus_dibayarkan)
        x = (kini.year - jatuh_tempo.year) * 12
        y = kini.month - jatuh_tempo.month
        bln_tunggakan = x + y + 1
        if kini.day <= jatuh_tempo.day:
            bln_tunggakan -= 1
        if bln_tunggakan < 1:
            bln_tunggakan = 0
        if bln_tunggakan > 24:
            bln_tunggakan = 24
        self.denda = bln_tunggakan * persen_denda / 100.0 * self.tagihan
        self.denda = round_up(self.denda)
        self.total = self.tagihan + self.denda

    def get_ntp(self):
        if not self.invoice:
            return
        if not self.paid:
            return
        if not self.payment:
            return
        q = DBSession.query(IsoPayment).filter_by(id=self.payment.id)
        iso_pay = q.first()
        return iso_pay.ntp

    def get_nop(self):
        return self.invoice and self.nop_struct.get_raw() or ''

    def get_payment(self):
        return get_last_payment(self.invoice)
