import sys
sys.path[0:0] = ['/usr/share/opensipkd/modules']
from tools import round_up
from base_models import DBSession
from datetime import datetime
from models import Invoice
sys.path[0:0] = ['/etc/opensipkd']
from padl_fix_conf import persen_denda


class CalculateInvoice(object):
    def __init__(self, tahun, bulan, usaha_id, sptno):
        self.tahun = tahun
        self.bulan = bulan
        self.usaha_id = usaha_id
        self.sptno = sptno
        q = DBSession.query(Invoice).filter_by(
                tahun=self.tahun,
                bulan=self.bulan,
                usaha_id=self.usaha_id,
                sptno=self.sptno).order_by('tahun DESC')
        self.invoice = q.first()
        if self.invoice:
            self.hitung()
            self.paid = self.is_paid()

    def hitung(self):
        self.tagihan = round_up(self.invoice.pajak_terhutang)
        self.denda = round_up(self.hitung_denda())
        self.total = self.tagihan + self.denda

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
        return bln_tunggakan * persen_denda / 100 * self.tagihan

    def is_paid(self):
        return self.invoice.status_pembayaran == 1
