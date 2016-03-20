import sys
sys.path[0:0] = ['/usr/share/opensipkd/modules']
from tools import (
    round_up,
    FixLength,
    )
from base_models import DBSession
from datetime import datetime
from models import Invoice
sys.path[0:0] = ['/etc/opensipkd']
from padl_fix_conf import persen_denda


INVOICE_ID = [
    ('Tahun', 4),
    ('Usaha', 2),
    ('Urutan', 5),
    ]

class Common(object):
    def is_paid(self):
        return self.invoice.status_bayar == 1 


def get_invoice(invoice_id):
    q = DBSession.query(Invoice).filter_by(nomor_tagihan=invoice_id).\
            order_by(Invoice.id.desc())
    return q.first()


class CalculateInvoice(Common):
    def __init__(self, invoice_id):
        self.invoice_id = invoice_id
        self.invoice = get_invoice(invoice_id)
        if self.invoice:
            self.paid = self.is_paid()
            if not self.paid:
                self.hitung()

    def hitung(self):
        pokok_tagihan = self.invoice.total - self.invoice.bunga
        self.tagihan = round_up(pokok_tagihan - self.invoice.denda)
        denda_telat_bayar = self.hitung_denda(pokok_tagihan)
        self.denda = round_up(self.invoice.bunga + self.invoice.denda + denda_telat_bayar)
        self.total = self.tagihan + self.denda

    def hitung_denda(self, pokok_tagihan):
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
        return bln_tunggakan * persen_denda / 100.0 * pokok_tagihan 

    def set_paid(self):
        self.invoice.status_bayar = 1
 
def decode_invoice_id_raw(raw):
    struct = FixLength(INVOICE_ID)
    struct.set_raw(raw)
    return struct
