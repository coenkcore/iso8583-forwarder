import sys
import sys
sys.path[0:0] = ['/usr/share/opensipkd/modules']
from tools import round_up
from datetime import datetime
from sqlalchemy import func
from models import (
    OtherDBSession,
    Invoice,
    Payment,
    )
sys.path[0:0] = ['/etc/opensipkd']
from padl_fix_conf import persen_denda


MAX_PORSI_DENDA = 0.48

class CalculateInvoice(object):
    def __init__(self, tahun, sptno):
        self.tahun = tahun
        self.sptno = sptno
        q = OtherDBSession.query(Invoice).filter_by(tahun=self.tahun,
                sptno=self.sptno).order_by(Invoice.sptno.desc())
        self.invoice = q.first()
        if self.invoice:
            self.hitung()
            self.paid = self.is_paid()

    def hitung(self):
        self.tagihan = round_up(self.invoice.pajak_terhutang - self.invoice.bunga)
        self.denda = round_up(self.hitung_denda())
        self.total = self.tagihan + self.denda
        q = OtherDBSession.query(func.sum(Payment.jml_bayar).label('jml')).\
                filter_by(spt_id=self.invoice.id)
        pay = q.first()
        if pay and pay.jml:
            self.total -= pay.jml

    def hitung_denda(self):
        jatuh_tempo = self.invoice.jatuhtempotgl
        kini = datetime.now()
        x = (kini.year - jatuh_tempo.year) * 12
        y = kini.month - jatuh_tempo.month
        bln_tunggakan = x + y + 1
        if kini.day <= jatuh_tempo.day:
            bln_tunggakan -= 1
        if bln_tunggakan < 1:
            bln_tunggakan = 0
        if bln_tunggakan > 24:
            bln_tunggakan = 24
        denda = bln_tunggakan * persen_denda / 100.0 * self.tagihan  
        total_denda = denda + self.invoice.bunga
        max_denda = MAX_PORSI_DENDA * self.tagihan
        if total_denda > max_denda:
            return max_denda
        return total_denda

    def is_paid(self):
        return self.invoice.status_pembayaran == 1 and self.total <= 0


def decode_invoice_id_raw(raw):
    tahun = raw[:4]
    sptno = raw[4:]
    return tahun, sptno.strip()
