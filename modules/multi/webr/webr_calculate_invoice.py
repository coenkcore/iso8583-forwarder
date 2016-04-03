import sys
from datetime import datetime
from sqlalchemy import func
sys.path.insert(0, '/usr/share/opensipkd/modules')
from tools import (
    round_up,
    FixLength,
    )
from webr import WebrDBSession
from webr_models import (
    Invoice,
    Pembayaran,
    )
sys.path.insert(0, '/etc/opensipkd')
from multi_conf import persen_denda


class CalculateInvoice(object):
    def __init__(self, invoice_no):
        #self.tahun = tahun
        #self.sptno = sptno
        q = WebrDBSession.query(Invoice).filter_by(kode=invoice_no)
        #.\
        #        order_by(Invoice.sptno.desc())
        self.invoice = q.first()
        if self.invoice:
            self.paid = self.is_paid()
            #if not self.paid:
            #    self.hitung()

    def hitung(self):
        self.bunga = self.invoice.bunga or 0
        self.bunga = round_up(self.bunga)
        self.tagihan = self.invoice.jumlah - self.bunga
        self.tagihan = round_up(self.tagihan)
        self.denda = self.hitung_denda() + self.bunga
        self.denda = round_up(self.denda)
        self.total = self.tagihan + self.denda
        q = WebrDBSession.query(func.sum(Pembayaran.bayar).label('jml')).\
                filter_by(arinvoice_id=self.invoice.id)
        pay = q.first()
        print('*** DEBUG: Total tagihan Rp {n}'.format(n=self.total))
        if pay and pay.jml:
            print('*** DEBUG: Sudah ada pembayaran sebesar Rp {n}'.format(n=pay.jml))
            self.total -= pay.jml
            print('*** DEBUG: Total tagihan menjadi Rp {n}'.format(n=self.total))
            if self.total<=0:
                self.paid = True
         
        else:
            print('*** DEBUG: Belum ada pembayaran.')

    def hitung_denda(self):
        if not self.invoice.jatuh_tempo:
           return 0
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
        return bln_tunggakan * persen_denda / 100.0 * self.tagihan

    def is_paid(self):
        return self.invoice.status_bayar == 1

    def set_paid(self):
        self.invoice.status_bayar = 1
        WebrDBSession.add(self.invoice)

    def set_unpaid(self):
        self.invoice.status_bayar = 0
        WebrDBSession.add(self.invoice)


# def decode_invoice_id_raw(raw):
    # struct = FixLength(INVOICE_ID)
    # struct.set_raw(raw)
    # return struct
