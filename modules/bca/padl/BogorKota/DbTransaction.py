from datetime import datetime
from random import randrange
from padl_fix_structure import INVOICE_PROFILE
from padl_fix_transaction import Transaction
from CalculateInvoice import (
    CalculateInvoice,
    decode_invoice_id_raw,
    )
import sys
sys.path.insert(0, '/usr/share/opensipkd/modules')
from tools import FixLength
from base_models import DBSession
from models import (
    Invoice,
    Customer,
    CustomerUsaha,
    Kelurahan,
    Kecamatan,
    Pajak,
    Rekening,
    IsoPayment,
    Payment,
    IsoReversal,
    )


ERR_MAX_LOOP = '*** Max loop for create payment ID. '\
               'Call your programmer please.'

# Nomor Transaksi Pemda
def get_ntp():
    max_loop = 10
    loop = 0
    while True:
        acak = randrange(11111111, 99999999)
        ntp = str(acak)
        q = DBSession.query(IsoPayment).filter_by(ntp=ntp)
        if not q.first():
            return ntp 
        loop += 1
        if loop == max_loop:
            raise Exception(ERR_MAX_LOOP)


class DbTransaction(Transaction):
    def transaction_init(self):
        self.invoice_id_raw = None # Cache
        self.invoice_profile = FixLength(INVOICE_PROFILE)

    def get_invoice(self):
        self.invoice_id_raw = self.from_iso.get_invoice_id()
        self.invoice_id = decode_invoice_id_raw(self.invoice_id_raw)
        if not self.invoice_id.set_raw(self.invoice_id_raw):
            return self.ack_invalid_invoice_id()
        self.calc = CalculateInvoice(self.invoice_id['Tahun'],
                        self.invoice_id['SPT No'])
        if self.calc.invoice:
            self.calc.hitung()
            return True
        return self.ack_invoice_not_available()

    def set_invoice_profile(self):
        cust, alamat2, cust_usaha = self.get_customer()
        rek = self.get_rek()
        nama = self.calc.invoice.r_nama or cust.customernm
        nama_ = []
        if cust_usaha.opnm:
            nama_.append(cust_usaha.opnm) 
        if nama:
            nama_.append(nama)
        nama_lengkap = ','.join(nama_)
        self.invoice_profile.from_dict({
            'NPWPD': cust.npwpd,
            'Nama': nama_lengkap,
            'Alamat 1': cust.alamat,
            'Alamat 2': alamat2,
            'Kode Rekening': rek.rekeningkd,
            'Nama Rekening': rek.rekeningnm,
            'Tagihan': self.calc.tagihan,
            'Denda': self.calc.denda,
            'Total': self.calc.total,
            'Masa 1': self.calc.invoice.masadari.strftime('%Y%m%d'),
            'Masa 2': self.calc.invoice.masasd.strftime('%Y%m%d'),
            })
        Transaction.set_invoice_profile(self)

    def _inquiry(self):
        if not self.get_invoice():
            return
        if self.calc.total > 0:
            self.set_amount(self.calc.total)
        self.set_invoice_profile()
        if self.calc.paid:
            return self.ack_already_paid()
        if self.calc.total <= 0:
            return self.ack_invalid_amount()
        return True

    # Override 
    def inquiry_response(self):
        self.transaction_init()
        if not self._inquiry():
            self.set_amount(0)
            return
        self.set_amount(self.calc.total)
        self.ack()

    # Override
    def payment_response(self):
        Transaction.payment_response(self)
        self.transaction_init()
        if not self._inquiry():
            return
        pay = self.save_payment()
        iso_pay = self.save_iso_payment(pay)
        self.set_ntp(iso_pay.ntp)
        self.commit()

    def commit(self):
        DBSession.flush()
        DBSession.commit()
        self.ack()

    def get_sspdno(self):
        q = DBSession.query(Payment).filter_by(tahun=self.calc.invoice.tahun).\
                order_by(Payment.sspdno.desc())
        pay = q.first()
        if pay:
            return pay.sspdno + 1
        return 1

    def save_payment(self):
        sspdno = self.get_sspdno()
        bank_id = self.get_bank_id()
        channel_id = self.get_channel_id()
        pay = Payment()
        pay.tahun = self.invoice_id['Tahun']
        pay.sspdno = sspdno 
        pay.spt_id = self.calc.invoice.id
        pay.denda = pay.bunga = self.calc.denda
        pay.jml_bayar = self.calc.total
        pay.create_date = pay.write_date = pay.sspdtgl = datetime.now()
        pay.printed = 1 
        DBSession.add(pay)
        self.calc.set_paid()
        DBSession.flush()
        return pay

    def save_iso_payment(self, pay):
        ntp = get_ntp()
        iso_pay = IsoPayment()
        iso_pay.id = pay.id
        iso_pay.invoice_id = pay.spt_id
        iso_pay.iso_request = self.from_iso.raw.upper()
        iso_pay.transmission = self.from_iso.get_transmission()
        iso_pay.settlement = self.from_iso.get_settlement()
        iso_pay.stan = self.from_iso.get_stan()
        iso_pay.ntb = self.from_iso.get_ntb()
        iso_pay.ntp = ntp
        iso_pay.bank_id = self.get_bank_id()
        iso_pay.channel_id = self.get_channel_id()
        iso_pay.bank_ip = self.get_bank_ip()
        DBSession.add(iso_pay)
        DBSession.flush()
        return iso_pay 

    # Override
    def reversal_response(self):
        self.invoice_id_raw = self.from_iso.get_invoice_id()
        self.invoice_id = decode_invoice_id_raw(self.invoice_id_raw)
        if not self.invoice_id.set_raw(self.invoice_id_raw):
            return self.ack_invalid_invoice_id()
        self.calc = CalculateInvoice(self.invoice_id['Tahun'],
                        self.invoice_id['SPT No'])
        if not self.calc.invoice:
            return self.ack_invoice_not_available()
        ntb = self.from_iso.get_ntb()
        q = DBSession.query(IsoPayment).filter_by(
                invoice_id=self.calc.invoice.id, ntb=ntb) 
        iso_pay = q.first()
        if not iso_pay:
            return self.ack_invoice_not_available()
        q = DBSession.query(IsoReversal).filter_by(id=iso_pay.id)
        iso_rev = q.first()
        if iso_rev:
            return self.ack_already_canceled()
        self.save_reversal(iso_pay)

    def save_reversal(self, iso_pay):
        q = DBSession.query(Payment).filter_by(id=iso_pay.id)
        pay = q.first()
        if not pay:
            return self.ack_payment_not_found()
        iso_request = self.from_iso.raw.upper()
        iso_request = '0400' + iso_request[4:]
        pay.denda = pay.bunga = pay.jml_bayar = 0
        DBSession.add(pay)
        self.calc.set_unpaid()
        iso_rev = IsoReversal()
        iso_rev.id = iso_pay.id
        iso_rev.iso_request = iso_request
        DBSession.add(iso_rev)
        self.commit()

    # Invoice Profile #
    def get_customer(self):
        q = DBSession.query(CustomerUsaha).\
                filter_by(id=self.calc.invoice.customer_usaha_id)
        cust_usaha = q.first()
        q_cust = DBSession.query(Customer).filter_by(id=cust_usaha.customer_id)
        cust = q_cust.first()
        if not cust_usaha.kelurahan_id:
            return cust, '', cust_usaha 
        q_kel = DBSession.query(Kelurahan).filter_by(id=cust_usaha.kelurahan_id)
        kelurahan = q_kel.first()
        q_kec = DBSession.query(Kecamatan).filter_by(id=kelurahan.kecamatan_id)
        kecamatan = q_kec.first()
        alamat2 = ','.join([kelurahan.kelurahannm, kecamatan.kecamatannm])
        return cust, alamat2, cust_usaha

    def get_rek(self):
        q_pajak = DBSession.query(Pajak).\
                    filter_by(id=self.calc.invoice.pajak_id)
        pajak = q_pajak.first()
        q_rek = DBSession.query(Rekening).filter_by(id=pajak.rekening_id)
        return q_rek.first()
