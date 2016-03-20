import re
import sys
from random import randrange
sys.path.insert(0, '/usr/share/opensipkd/modules')
from tools import FixLength
from base_models import (
    Base,
    DBSession,
    )
from datetime import datetime
sys.path.insert(0, '')
from padl_fix_structure import (
    INVOICE_PROFILE,
    INVOICE_ID,
    )
from padl_fix_transaction import Transaction
from CalculateInvoice import CalculateInvoice
from models import (
    Invoice,
    Customer,
    CustomerUsaha,
    Kelurahan,
    Kecamatan,
    Invoice,
    Pajak,
    Rekening,
    IsoPayment,
    PaymentSequence,
    Payment,
    IsoReversal,
    )


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
            raise Exception('*** Max loop for create payment ID. '\
                            'Call your programmer please.')

def create_payment_id():
    return PaymentSequence.execute(Base.metadata.bind)


class DbTransaction(Transaction):
    def __init__(self, *args, **kwargs):
        self.invoice_profile = FixLength(INVOICE_PROFILE)
        self.invoice_id = FixLength(INVOICE_ID)
        Transaction.__init__(self, *args, **kwargs)

    def get_invoice(self):
        self.invoice_profile.set_raw(self.from_iso.get_value(48).strip())
        self.invoice_id_raw = self.invoice_profile.get('ID Billing').strip()
        self.invoice_id.set_raw(self.invoice_id_raw)
        self.tahun = self.invoice_id.get('Tahun')
        sptno = self.invoice_id.get('SPT No')
        self.calc = CalculateInvoice(self.tahun, sptno)
        if not self.calc.invoice:
            return self.ack_invoice_not_available()
        self.calc.hitung()
        self.set_invoice_profile()
        self.setBit(48, self.invoice_profile.get_raw())
        if self.calc.paid:
            return self.ack_already_paid()
        self.set_amount(self.calc.total)
        return self.calc.invoice

    def set_invoice_profile(self):
        invoice = self.calc.invoice
        cust_usaha = DBSession.query(CustomerUsaha).\
                        filter_by(id=invoice.customer_usaha_id).first()
        cust = DBSession.query(Customer).\
                filter_by(id=cust_usaha.customer_id).first()
        if cust_usaha.kelurahan_id:
            kelurahan = DBSession.query(Kelurahan).\
                            filter_by(id=cust_usaha.kelurahan_id).first()
            kecamatan = DBSession.query(Kecamatan).\
                            filter_by(id=kelurahan.kecamatan_id).first()
            alamat2 = ','.join([kelurahan.kelurahannm,kecamatan.kecamatannm])
        else:
            alamat2 = ''
        pajak = DBSession.query(Pajak).filter_by(id=invoice.pajak_id).first()
        rek = DBSession.query(Rekening).filter_by(id=pajak.rekening_id).first()
        self.ntp = create_ntp()
        self.invoice_profile.from_dict({
            'NPWPD': cust.npwpd,
            'Nama OP': cust.customernm,
            'Bulan': invoice.masadari.strftime('%m'),
            'Tahun': invoice.masadari.strftime('%Y'),
            'Tanggal Penetapan': invoice.terimatgl.strftime('%d-%m-%Y'),
            'Tanggal Jatuh Tempo': invoice.jatuhtempotgl.strftime('%d-%m-%Y'),
            'NTPD': self.ntp,
            'Tagihan Pokok': self.calc.tagihan,
            'Jenis Pajak': ' '.join([re.sub('[^0-9]', '', rek.rekeningkd),
                                     rek.rekeningnm]),
            'Masa Pajak': ' s.d '.join([invoice.masadari.strftime('%d-%m-%Y'),
                                        invoice.masasd.strftime('%d-%m-%Y')]),
            'Uraian Kegiatan': '',
            'Denda': self.calc.denda,
            })
        self.setBit(48, self.invoice_profile.get_raw())
        if self.calc.total > 0:
            self.setBit(4, self.calc.total)

    def inquiry_response(self):
        self.setBit(4, 0)
        if self.get_invoice():
            self.ack()

    def payment_response(self):
        self.copy([4, 48, 62])
        inv = self.get_invoice()
        if not inv:
            return
        pay = DBSession.query(Payment).filter_by(tahun=inv.tahun).\
                order_by('sspdno DESC').first()
        if pay:
            sspdno = pay.sspdno + 1
        else:
            sspdno = 1
        bank_id = self.get_bank_id()
        channel_id = self.get_channel_id()
        pay_id = create_payment_id()
        pay = Payment()
        pay.id = pay_id
        pay.tahun = self.tahun
        pay.sspdno = sspdno 
        pay.spt_id = inv.id
        pay.sspdtgl = datetime.now() 
        pay.denda = pay.bunga = self.calc.denda
        pay.jml_bayar = self.calc.total
        pay.create_date = pay.write_date = pay.sspdtgl
        pay.printed = pay.enabled = 1
        DBSession.add(pay)
        iso_pay = self.save_payment(pay)
        iso_pay.ntp = self.ntp
        iso_pay.bank_id = bank_id
        iso_pay.channel_id = channel_id
        iso_pay.bank_ip = self.get_bank_ip()
        iso_pay.invoice_id = inv.id
        DBSession.add(iso_pay)
        DBSession.flush()
        DBSession.commit()
        self.ack()

    def save_payment(self, pay):
        iso_pay = IsoPayment()
        iso_pay.sspd_id = pay.id
        iso_pay.invoice_no = self.invoice_id.get_raw() #pay.spt_id
        iso_pay.iso_request = self.from_iso.raw.upper()
        iso_pay.transmission = self.from_iso.get_transmission()
        iso_pay.settlement = self.from_iso.get_settlement()
        iso_pay.stan = self.from_iso.get_value(11)
        iso_pay.ntb = self.from_iso.get_value(37)
        iso_pay.original_data_element = self.from_iso.get_value(90)
        return iso_pay

    def reversal_response(self):
        self.copy()
        iso_request = self.from_iso.raw.upper()
        iso_request = '0400' + iso_request[4:]
        self.invoice_profile.set_raw(self.from_iso.get_value(48).strip())
        self.invoice_id_raw = self.invoice_profile.get('ID Billing').strip()
        self.invoice_id.set_raw(self.invoice_id_raw)
        q = DBSession.query(IsoPayment).filter_by(
                invoice_no = self.invoice_id_raw,
                original_data_element = self.from_iso.get_value(90),
                bank_id = self.get_bank_id())
        iso_pay = q.first()
        if not iso_pay:
            return self.ack_invoice_not_available()
        iso_rev = DBSession.query(IsoReversal).filter_by(id=iso_pay.id).first()
        if iso_rev:
            return self.ack_already_canceled()
        if not self.execute_reversal(iso_pay, iso_request):
            return self.ack('99')
        self.ack()

    def execute_reversal(self, iso_pay, iso_request):
        payment = DBSession.query(Payment).filter_by(id=iso_pay.sspd_id).first()
        if not payment:
            return self.ack_payment_not_found()
        payment.denda = 0
        payment.jml_bayar = 0
        payment.enabled = 0
        payment.is_valid =0
        invoice = DBSession.query(Invoice).filter_by(id=payment.spt_id).first()
        if not invoice:
            return self.ack_invoice_not_available()
        invoice.status_pembayaran = 0  
        self.save_reversal(iso_pay, iso_request)
        return True

    def save_reversal(self, iso_pay, iso_request):
        iso_rev = IsoReversal()
        iso_rev.id = iso_pay.id
        iso_rev.iso_request = iso_request
        DBSession.add(iso_rev)
        DBSession.flush()
        DBSession.commit()

    def get_bank_id(self):
        return self.conf['id']

    def get_bank_ip(self):
         return self.conf['ip']

    def get_channel_id(self):
        return self.from_iso.get_value(18)

    # Override
    def set_transaction_response(self):
        self.setMTI('0210')
        self.copy()
