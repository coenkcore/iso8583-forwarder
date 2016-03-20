import sys
from datetime import datetime
from sqlalchemy import (
    func,
    and_,
    )
sys.path.insert(0, '/usr/share/opensipkd/modules')
from tools import (
    round_up,
    FixLength,
    )
from base_models import DBSession
sys.path.insert(0, '/etc/opensipkd')
from padl_fix_conf import persen_denda
from models import (
    Rekening,
    InvoiceSpt,
    InvoiceSkp,
    InvoiceSkpDet,
    Payment,
    PaymentDet,
    Hotel,
    Restoran,
    Hiburan,
    PJalan,
    Galian,
    Parkir,
    Walet,
    )


INVOICE_ID = [
    ('table_no', 2),
    ('invoice_no', 30)
    ]


# ObjekPajak
OP_CLASS = {
    1: Hotel,
    2: Restoran,
    3: Hiburan,
    5: PJalan,
    6: Galian,
    7: Parkir,
    9: Walet,
    }


def get_invoice(invoice_id):
    q = DBSession.query(InvoiceSpt).filter_by(no_spt=invoice_id).\
            order_by(InvoiceSpt.no_spt.desc())
    row = q.first()
    if row:
        return row
    q = DBSession.query(InvoiceSkp).filter_by(no_ketetapan=invoice_id).\
            order_by(InvoiceSkp.no_ketetapan.desc())
    return q.first()


class CalculateInvoice(object):
    def __init__(self, invoice_id):
        self.invoice_id = invoice_id
        self.invoice = get_invoice(invoice_id)
        if self.invoice:
            self.hitung()
            self.paid = self.total <= 0

    def hitung(self):
        self.denda = 0
        self.tagihan = 0
        if self.invoice.jn_pemungutan == 1:
            r_inv = self.set_tagihan_op()
        else: # SKPD
            r_inv = self.set_tagihan_skpd()
        if r_inv: # Final check 
            self.set_rekening(r_inv)
        self.total = self.tagihan + self.denda

    def hitung_denda(self, pokok_tagihan):
        jatuh_tempo = self.invoice.tgl_jatuh_tempo
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

    def get_inv_op(self):
        op_cls = OP_CLASS[self.invoice.jn_pajak]
        f_no_spt = getattr(op_cls, 'no_spt')
        q = DBSession.query(op_cls).filter_by(no_spt=self.invoice_id).\
                order_by(f_no_spt.desc())
        return q.first()

    def get_pay_op(self):
        q = DBSession.query(func.sum(PaymentDet.nilai).label('nilai')).\
                join(Payment, and_(Payment.tahun   == PaymentDet.tahun,
                                   Payment.no_sspd == PaymentDet.no_sspd)).\
                filter(Payment.no_pokok_wp    == self.invoice.no_pokok_wp,
                       Payment.jn_wajib_pajak == self.invoice.jn_wajib_pajak,
                       Payment.jn_usaha_wp    == self.invoice.jn_usaha_wp,   
                       Payment.kd_usaha       == self.invoice.kd_usaha,      
                       Payment.jn_pajak       == self.invoice.jn_pajak,      
                       Payment.jn_pemungutan  == self.invoice.jn_pemungutan, 
                       Payment.masa1          == self.invoice.masa1,         
                       Payment.masa2          == self.invoice.masa2)
        return q.first()

    def set_tagihan_op(self):
        r_inv = self.get_inv_op()
        if r_inv: # Cek payment
            self.tagihan = round_up(r_inv.pajakterhutang)
            r_pay = self.get_pay_op()
            if r_pay.nilai:
                self.tagihan -= round_up(r_pay.nilai)
        return r_inv

    def get_inv_skpd(self):
        q = DBSession.query(InvoiceSkpDet).filter_by(no_ketetapan=self.invoice_id).\
                order_by(InvoiceSkpDet.no_ketetapan.desc())
        return q.first()

    def get_pay_skpd(self):
        q = DBSession.query(func.sum(PaymentDet.nilai).label('nilai')).\
                join(Payment, and_(Payment.tahun   == PaymentDet.tahun,
                                   Payment.no_sspd == PaymentDet.no_sspd)).\
                filter(Payment.no_ketetapan == self.invoice.no_ketetapan)
        return q.first()

    def set_tagihan_skpd(self):
        r_inv = self.get_inv_skpd()
        if r_inv: # Cek payment
            self.tagihan = round_up(r_inv.jumlah)
            r_pay = self.get_pay_skpd()
            if r_pay.nilai:
                self.tagihan -= round_up(r_pay.nilai)
            self.denda = self.hitung_denda(self.tagihan)
            self.denda = round_up(self.denda)
        return r_inv

    def set_rekening(self, row):
        self.invoice.rekening_pokok = ''.join(row.kd_rek_1, row.kd_rek_2,
            row.kd_rek_3, str(row.kd_rek_4).zfill(2),
            str(row.kd_rek_5).zfill(2), str(row.kd_rek_6).zfill(2))
        q = DBSession.query(Rekening.nm_rek_6).filter_by(kd_rek_1=row.kd_rek_1,
                kd_rek_2=row.kd_rek_2, kd_rek_3=row.kd_rek_3,
                kd_rek_4=row.kd_rek_4, kd_rek_5=row.kd_rek_5,
                kd_rek_6=row.kd_rek_6)
        self.invoice.nama_pokok = q.scalar()

 
def decode_invoice_id_raw(raw):
    struct = FixLength(INVOICE_ID)
    struct.set_raw(raw)
    return struct
