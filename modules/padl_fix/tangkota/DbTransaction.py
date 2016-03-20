import re
import calendar
from datetime import datetime
from random import randrange
from ISO8583.ISO8583 import ISO8583
from padl_fix_structure import (
    INVOICE_PROFILE,
    RC_NOT_AVAILABLE,
    RC_ALREADY_PAID,
    ERR_NOT_AVAILABLE,
    ERR_ALREADY_PAID,
    )
from padl_fix_transaction import Transaction
from CalculateInvoice import CalculateInvoice
import sys
sys.path.insert(0, '/usr/share/opensipkd/modules')
from tools import FixLength
from base_models import (
    Base,
    DBSession,
    )
from models import (
    Invoice,
    IsoPayment,
    PaymentSequence,
    IsoReversal,
    )
from PaymentReversal import PaymentReversal


ERR_MAX_LOOP = 'Max loop for create payment ID. Call your programmer please.'

def create_ntp(prefix=''):
    max_loop = 10
    loop = 0
    while True:
        acak = randrange(11111111, 99999999)
        acak = str(acak)
        trx_id = ''.join([prefix, acak])
        found = DBSession.query(IsoPayment).filter_by(ntp=trx_id).first()
        if not found:
            return trx_id
        loop += 1
        if loop == max_loop:
            raise Exception(ERR_MAX_LOOP)

def create_payment_id():
    return PaymentSequence.execute(Base.metadata.bind)


NAMA_BULAN = ('', 'Januari', 'Pebruari', 'Maret', 'April', 'Mei', 'Juni',
              'Juli', 'Agustus', 'September', 'Oktober', 'Nopember',
              'Desember')

class DbTransaction(Transaction):
    def __init__(self, *args, **kwargs):
        self.invoice_id_raw = None # Cache
        self.invoice_profile = FixLength(INVOICE_PROFILE)
        Transaction.__init__(self, *args, **kwargs)

    def get_invoice(self):
        self.invoice_id_raw = self.from_iso.get_invoice_id()
        self.calc = CalculateInvoice(self.invoice_id_raw)
        if not self.calc.invoice:
            return self.ack(RC_NOT_AVAILABLE,
                ERR_NOT_AVAILABLE.format(invoice_id=self.invoice_id_raw))
        self.calc.hitung()
        self.set_invoice_profile()
        if self.calc.paid:
            return self.ack(RC_ALREADY_PAID, ERR_ALREADY_PAID.format(
                invoice_id=self.invoice_id_raw))
        if self.calc.total > 0:
            self.set_amount(self.calc.total)
        return self.calc.invoice

    def set_invoice_profile(self):
        invoice = self.calc.invoice
        nama_bulan, tahun = invoice.periode.split()
        bulan = NAMA_BULAN.index(nama_bulan)
        bulan_zfill = str(bulan).zfill(2)
        awal = tahun + bulan_zfill + '01'
        tgl_akhir = calendar.monthrange(int(tahun), int(bulan))[1]
        akhir = tahun + bulan_zfill + str(tgl_akhir).zfill(2)
        self.invoice_profile.from_dict({
            'NPWPD': invoice.npwpd,
            'Nama': invoice.nama_wp, 
            'Alamat 1': invoice.alamat_wp,
            'Alamat 2': invoice.alamat_op,
            'Kode Rekening': invoice.rekening_pokok,
            'Nama Rekening': invoice.nama_pokok, 
            'Tagihan': self.calc.tagihan,
            'Denda': self.calc.denda,
            'Total': self.calc.total,
            'Masa 1': awal, 
            'Masa 2': akhir,
            })
        self.setBit(62, self.invoice_profile.get_raw())

    def inquiry_response(self):
        self.set_amount(0)
        if self.get_invoice():
            self.ack()

    def payment_response(self):
        self.copy([4, 48, 62])
        inv = self.get_invoice()
        if not inv:
            return
        ntp = create_ntp()
        bank_id = self.get_bank_id()
        channel_id = self.get_channel_id()
        iso_pay = self.save_payment()
        iso_pay.ntp = ntp
        iso_pay.bank_id = bank_id
        iso_pay.channel_id = channel_id
        iso_pay.bank_ip = self.get_bank_ip()
        self.calc.set_paid()
        DBSession.add(iso_pay)
        DBSession.add(self.calc.invoice)
        DBSession.flush()
        DBSession.commit()
        self.set_ntp(ntp)
        self.ack()

    def save_payment(self):
        pay_id = create_payment_id()
        iso_pay = IsoPayment()
        iso_pay.id = pay_id
        iso_pay.invoice_id = self.calc.invoice.id 
        iso_pay.iso_request = ISO8583.getRawIso(self.from_iso)
        iso_pay.transmission = self.from_iso.get_transmission()
        iso_pay.settlement = self.from_iso.get_settlement()
        iso_pay.stan = self.from_iso.get_value(11)
        iso_pay.ntb = self.from_iso.get_ntb()
        iso_pay.tagihan = self.calc.tagihan
        iso_pay.denda = self.calc.denda
        iso_pay.total_bayar = self.calc.total
        return iso_pay

    def reversal_response(self):
        self.invoice_id_raw = self.get_invoice_id()
        ntb = self.get_ntb()
        q = DBSession.query(IsoPayment).filter_by(bank_id=self.conf['id'],
                ntb=ntb)
        iso_pay = q.first()
        if not iso_pay:
            return self.ack(RC_NOT_AVAILABLE,
                ERR_NOT_AVAILABLE.format(invoice_id=self.invoice_id_raw))
        pr = PaymentReversal(iso_pay)
        if not pr.is_paid():
            msg = 'Status {id} memang belum dibayar.'.format(
                    id=self.invoice_id_raw)
            return self.ack(RC_ALREADY_PAID, msg)
        iso_rev = DBSession.query(IsoReversal).filter_by(id=iso_pay.id).first()
        if iso_rev:
            return self.ack(RC_ALREADY_PAID, 'Memang sudah dibatalkan.')
        iso_rev = IsoReversal()
        iso_rev.id = iso_pay.id
        iso_rev.iso_request = ISO8583.getRawIso(self.from_iso)
        pr.set_unpaid()
        DBSession.add(pr.payment)
        DBSession.add(pr.invoice)
        DBSession.flush()
        DBSession.commit()
        self.ack()
