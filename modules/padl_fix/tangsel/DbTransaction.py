import re
from datetime import datetime
from random import randrange
from padl_fix_structure import (
    INVOICE_PROFILE,
    RC_OK,
    RC_INVALID_NUMBER,
    RC_NOT_AVAILABLE,
    RC_ALREADY_PAID,
    RC_INSUFFICIENT_FUND,
    RC_OTHER_ERROR,
    RC_LINK_DOWN,
    ERR_INVALID_NUMBER,
    ERR_NOT_AVAILABLE,
    ERR_ALREADY_PAID,
    ERR_ALREADY_PAID_2,
    ERR_AMOUNT,
    ERR_INSUFFICIENT_FUND,
    ERR_OTHER,
    )
from padl_fix_transaction import Transaction
from CalculateInvoice import (
    CalculateInvoice,
    decode_invoice_id_raw,
    )
import sys
sys.path[0:0] = ['/usr/share/opensipkd/modules']
from tools import (
    FixLength,
    create_datetime,
    )
from base_models import (
    Base,
    DBSession,
    )
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
    Bank,
    Channel,
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
            raise Exception('*** Max loop for create payment ID. Call your programmer please.')

def create_payment_id():
    return PaymentSequence.execute(Base.metadata.bind)


class DbTransaction(Transaction):
    def __init__(self, *args, **kwargs):
        self.invoice_id_raw = None # Cache
        self.invoice_profile = FixLength(INVOICE_PROFILE)
        Transaction.__init__(self, *args, **kwargs)

    def get_invoice(self):
        self.invoice_id_raw = self.from_iso.get_value(61).strip()
        self.tahun, sptno = decode_invoice_id_raw(self.invoice_id_raw)
        self.calc = CalculateInvoice(self.tahun, sptno)
        if not self.calc.invoice:
            return self.ack(RC_NOT_AVAILABLE,
                ERR_NOT_AVAILABLE.format(invoice_id=self.invoice_id_raw))
        self.calc.hitung()
        self.set_invoice_profile()
        self.setBit(62, self.invoice_profile.get_raw())
        if self.calc.paid:
            return self.ack(RC_ALREADY_PAID, ERR_ALREADY_PAID.format(
                invoice_id=self.invoice_id_raw))
        self.set_amount()
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
        self.invoice_profile.from_dict({
            'NPWPD': cust.npwpd,
            'Nama': cust.customernm,
            'Alamat 1': cust.alamat,
            'Alamat 2': alamat2,
            'Kode Rekening': re.sub('[^0-9]', '', rek.rekeningkd),
            'Nama Rekening': rek.rekeningnm,
            'Tagihan': self.calc.tagihan,
            'Denda': self.calc.denda,
            'Total': self.calc.total,
            'Masa 1': invoice.masadari.strftime('%Y%m%d'),
            'Masa 2': invoice.masasd.strftime('%Y%m%d'),
            })
        self.setBit(62, self.invoice_profile.get_raw())

    def set_amount(self):
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
        ntp = create_ntp()
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
        self.setBit(47, ntp)
        iso_pay = self.save_payment(pay)
        iso_pay.ntp = ntp
        iso_pay.bank_id = bank_id
        iso_pay.channel_id = channel_id
        iso_pay.bank_ip = self.get_bank_ip()
        DBSession.add(iso_pay)
        DBSession.flush()
        DBSession.commit()
        self.ack()

    def save_payment(self, pay):
        iso_pay = IsoPayment()
        iso_pay.sspd_id = pay.id
        iso_pay.invoice_no = self.from_iso.get_value(61).strip() #pay.spt_id
        iso_pay.iso_request = self.from_iso.getRawIso().upper()
        iso_pay.transmission = self.from_iso.get_transmission()
        iso_pay.settlement = self.from_iso.get_settlement()
        iso_pay.stan = self.from_iso.get_value(11)
        iso_pay.ntb = self.from_iso.get_value(48)
        return iso_pay

    def reversal_response(self):
        self.copy([4, 58, 107])
        iso_request = self.from_iso.raw.upper()
        iso_request = '0400' + iso_request[4:]
        self.invoice_id_raw = self.from_iso.get_value(61).strip()
        q = DBSession.query(IsoPayment).filter_by(invoice_no=self.invoice_id_raw,
                    ntb = self.from_iso.get_value(48))
        iso_pay = q.first()
        if not iso_pay:
            return self.ack(RC_NOT_AVAILABLE,
                ERR_NOT_AVAILABLE.format(invoice_id=self.invoice_id_raw))
        iso_rev = DBSession.query(IsoReversal).filter_by(id=iso_pay.id).first()
        if iso_rev:
            return self.ack(RC_ALREADY_PAID, 'Memang sudah dibatalkan.')
        if not self.execute_reversal(iso_pay, iso_request):
            return self.ack('91')
        self.ack()

    def execute_reversal(self, iso_pay, iso_request):
        payment = DBSession.query(Payment).filter_by(id=iso_pay.sspd_id).first()
        if not payment:
            return self.ack(RC_NOT_AVAILABLE,
                    'Data pembayaran tidak ditemukan')
        payment.denda  = 0
        payment.jml_bayar  = 0
        invoice = DBSession.query(Invoice).filter_by(id=payment.spt_id).first()
        if not invoice:
            return self.ack(RC_NOT_AVAILABLE,
                'Data tagihan tidak Ditemukan')
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
        return self.ack()

    def get_bank_id(self):
        name = self.conf.get('name').upper()
        q = DBSession.query(Bank).filter_by(singkatan=name)
        row = q.first()
        if not row:
            raise Exception('Tidak ada bank dengan singkatan {name}'.format(
                name=name))
        return row.id

    def get_bank_ip(self):
         return self.conf['ip']

    def get_channel_id(self):
        channel_id = self.from_iso.get_value(18)
        q = DBSession.query(Channel).filter_by(id=channel_id)
        channel = q.first()
        if channel:
            return channel.id
