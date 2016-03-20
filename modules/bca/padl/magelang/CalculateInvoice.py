import sys
sys.path[0:0] = ['/usr/share/opensipkd/modules']
from tools import round_up
from base_models import DBSession
from datetime import datetime
from models import (
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
        q = DBSession.query(Invoice).filter_by(tahun=self.tahun,
                sptno=self.sptno).order_by(Invoice.id.desc())
        self.invoice = q.first()
        if self.invoice:
            self.paid = self.is_paid()
            if not self.paid:
                self.hitung()

    def hitung(self):
        self.tagihan = round_up(self.hitung_tagihan())
        self.denda = round_up(self.hitung_denda())
        self.total = self.tagihan + self.denda

    def hitung_tagihan(self):
        return self.invoice.dasar * self.invoice.tarif \
               + self.invoice.denda \
               + self.invoice.kenaikan - self.invoice.kompensasi \
               + self.invoice.lain2 - self.invoice.setoran

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
        q = DBSession.query(Payment).filter_by(spt_id=self.invoice.id,
                enabled=1)
        pay = q.first()
        return pay and pay.enabled == 1 
    
def decode_invoice_id_raw(raw):
    tahun = raw[:4]
    sptno = raw[4:10]
    return tahun, sptno

