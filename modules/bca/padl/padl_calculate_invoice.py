import sys
from datetime import datetime
from sqlalchemy import func
sys.path.insert(0, '/usr/share/opensipkd/modules')
from tools import (
    round_up,
    FixLength,
    )
from base_models import DBSession
from padl_models import (
    Invoice,
    Pembayaran,
    )
sys.path.insert(0, '/etc/opensipkd')
from padl_fix_conf import persen_denda


class CalculateInvoice(object):
    def __init__(self, tahun, sptno):
        self.tahun = tahun
        self.sptno = sptno
        q = DBSession.query(Invoice).filter_by(tahun=self.tahun, sptno=sptno).\
                order_by(Invoice.sptno.desc())
        self.invoice = q.first()
        if self.invoice:
            self.paid = self.is_paid()
            #if not self.paid:
            #    self.hitung()

    def hitung(self):
        self.bunga = self.invoice.bunga or 0
        self.bunga = round_up(self.bunga)
        self.tagihan = self.invoice.pajak_terhutang - self.bunga
        self.tagihan = round_up(self.tagihan)
        self.denda = self.hitung_denda() + self.bunga
        self.denda = round_up(self.denda)
        self.total = self.tagihan + self.denda
        q = DBSession.query(func.sum(Pembayaran.jml_bayar).label('jml')).\
                filter_by(spt_id=self.invoice.id)
        pay = q.first()
        print('*** DEBUG: Total tagihan Rp {n}'.format(n=self.total))
        if pay and pay.jml:
            print('*** DEBUG: Sudah ada pembayaran sebesar Rp {n}'.format(n=pay.jml))
            self.total -= pay.jml
            print('*** DEBUG: Total tagihan menjadi Rp {n}'.format(n=self.total))
        else:
            print('*** DEBUG: Belum ada pembayaran.')

    def hitung_denda(self):
        if not self.invoice.jatuhtempotgl:
           return 0
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
        return bln_tunggakan * persen_denda / 100.0 * self.tagihan

    def is_paid(self):
        return self.invoice.status_pembayaran == 1

    def set_paid(self):
        self.invoice.status_pembayaran = 1
        DBSession.add(self.invoice)

    def set_unpaid(self):
        self.invoice.status_pembayaran = 0
        DBSession.add(self.invoice)


INVOICE_ID = [
    ('Tahun', 4, 'N'),
    ('SPT No', 6, 'N')
    ]

def decode_invoice_id_raw(raw):
    struct = FixLength(INVOICE_ID)
    struct.set_raw(raw)
    return struct
