import sys
from datetime import datetime
from sqlalchemy.sql.expression import text
sys.path.insert(0, '/usr/share/opensipkd/modules')
from tools import round_up
from base_models import DBSession
sys.path.insert(0, '/etc/opensipkd')
from padl_fix_conf import persen_denda
from models import InvoiceView


class CalculateInvoice(object):
    def __init__(self, invoice_id):
        engine = DBSession.bind
        q = DBSession.query(InvoiceView).filter_by(kode_bayar=invoice_id)
        self.invoice = q.first()
        if self.invoice:
            self.paid = self.is_paid()

    def hitung(self):
        self.tagihan = self.invoice.jumlah_pajak
        self.tagihan = round_up(self.tagihan)
        self.denda = self.hitung_denda()
        self.denda = round_up(self.denda)
        self.total = self.tagihan + self.denda
    
    def hitung_denda(self):
        jatuh_tempo = self.invoice.jatuh_tempo
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
        self.bln_tunggakan = bln_tunggakan
        self.persen_denda = persen_denda
        return bln_tunggakan * persen_denda / 100.0 * self.tagihan

    def is_paid(self):
        return self.invoice.is_bayar == 't'
