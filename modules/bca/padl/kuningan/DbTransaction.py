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
    ERR_REVERSAL_DONE,
    ERR_PAYMENT_NOT_FOUND,
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
    OtherDBSession,
    OtherBase,
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
    PAYMENT_SEQ,
    )


def get_payment_id(prefix=''):
    max_loop = 10
    loop = 0
    while True:
        acak = randrange(11111111, 99999999)
        acak = str(acak)
        trx_id = ''.join([prefix, acak])
        found = OtherDBSession.query(IsoPayment).filter_by(ntp=trx_id).first()
        if not found:
            return trx_id
        loop += 1
        if loop == max_loop:
            raise Exception('*** Max loop for create payment ID. Call your programmer please.')

def get_payment_id():
    return PAYMENT_SEQ.execute(OtherDBSession.bind)

class DbTransaction(Transaction):
    def transaction_init(self):
        self.invoice_id_raw = None # Cache
        self.invoice_profile = FixLength(INVOICE_PROFILE)

    def get_invoice(self):
        self.invoice_id_raw = self.from_iso.get_value(61).strip()
        tahun, sptno = decode_invoice_id_raw(self.invoice_id_raw)
        self.calc = CalculateInvoice(tahun, sptno)
        if self.calc.invoice:
            return self.calc.invoice
        return self.ack(RC_NOT_AVAILABLE,
                ERR_NOT_AVAILABLE.format(invoice_id=self.invoice_id_raw))

    def set_invoice_profile(self):
        invoice = self.calc.invoice
        cust_usaha = OtherDBSession.query(CustomerUsaha).\
                        filter_by(id=invoice.customer_usaha_id).first()
        cust = OtherDBSession.query(Customer).\
                filter_by(id=cust_usaha.customer_id).first()
        if cust_usaha.kelurahan_id:
            kelurahan = OtherDBSession.query(Kelurahan).\
                            filter_by(id=cust_usaha.kelurahan_id).first()
            kecamatan = OtherDBSession.query(Kecamatan).\
                            filter_by(id=kelurahan.kecamatan_id).first()
            alamat2 = ','.join([kelurahan.kelurahannm,kecamatan.kecamatannm])
        else:
            alamat2 = ''
        pajak = OtherDBSession.query(Pajak).filter_by(id=invoice.pajak_id).first()
        rek = OtherDBSession.query(Rekening).filter_by(id=pajak.rekening_id).first()
        self.invoice_profile.from_dict({
            'NPWPD': cust.npwpd,
            'Nama': invoice.r_nama or cust.customernm,
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

    def set_total(self, total=0):
        self.setBit(4, total)

    def inquiry_response(self):
        self.transaction_init()
        self.set_total()
        inv = self.get_invoice()
        if not inv:
            return
        if self.calc.total > 0:
            self.set_total(self.calc.total)
        self.set_invoice_profile()
        self.setBit(62, self.invoice_profile.get_raw())
        if inv.status_pembayaran == 1:
            return self.ack(RC_ALREADY_PAID, ERR_ALREADY_PAID.format(
                invoice_id=self.invoice_id_raw))
        if self.calc.total <= 0:
            return self.ack(RC_ALREADY_PAID, ERR_AMOUNT.format(
                invoice_id=self.invoice_id_raw, nominal=self.calc.total))
        self.ack()
        return inv

    def payment_response(self):
        self.transaction_init()
        self.copy([4, 48, 62])
        inv = self.inquiry_response()
        if not inv:
            return
        ntp = get_payment_id()
        channel_id = self.get_channel_id()
        pay = self.create_payment(inv)
        pay.spt_id = inv.id
        OtherDBSession.add(pay)
        inv.status_pembayaran = 1 
        OtherDBSession.add(inv)
        self.setBit(47, ntp)
        iso_pay = self.save_payment(pay)
        iso_pay.ntp = ntp
        iso_pay.channel_id = channel_id
        DBSession.add(iso_pay)
        self.commit()

    def commit(self):
        OtherDBSession.flush() # INSERT
        DBSession.flush()
        DBSession.commit()
        OtherDBSession.commit()
        self.ack()

    def create_payment(self, inv):
        q = OtherDBSession.query(Payment).filter_by(tahun=inv.tahun).\
                order_by('sspdno DESC')
        paid = q.first()
        if paid:
            sspdno = paid.sspdno + 1
        else:
            sspdno = 1
        pay_id = get_payment_id()
        pay = Payment()
        pay.id = pay_id
        pay.sspdno = sspdno 
        pay.tahun = self.calc.tahun
        pay.denda = pay.bunga = self.calc.denda
        pay.jml_bayar = self.calc.total
        pay.sspdtgl = pay.create_date = pay.write_date = datetime.now() 
        pay.printed = 1
        return pay

    def save_payment(self, pay):
        iso_pay = IsoPayment()
        iso_pay.sspd_id = pay.id
        iso_pay.invoice_no = self.from_iso.get_value(61).strip() #pay.spt_id
        iso_pay.iso_request = self.from_iso.getRawIso().upper()
        iso_pay.transmission = self.from_iso.get_transmission()
        iso_pay.settlement = self.from_iso.get_settlement()
        iso_pay.stan = self.from_iso.get_value(11)
        iso_pay.ntb = self.from_iso.get_value(48)
        iso_pay.bank_ip = self.get_bank_ip()
        iso_pay.bank_id = self.get_bank_id()
        return iso_pay

    def reversal_response(self):
        self.transaction_init()
        self.copy([4, 58, 107])
        iso_request = self.from_iso.raw.upper()
        iso_request = '0400' + iso_request[4:]
        self.invoice_id_raw = self.from_iso.get_value(61).strip()
        q = DBSession.query(IsoPayment).filter_by(invoice_no=self.invoice_id_raw,
                    ntb = self.from_iso.get_value(48))
        iso_pay = q.first()
        if not iso_pay:
            return self.ack_not_available()
        iso_rev = DBSession.query(IsoReversal).filter_by(id=iso_pay.id).first()
        if iso_rev:
            return self.ack_reversal_done()
        self.save_reversal(iso_pay, iso_request)

    def save_reversal(self, iso_pay, iso_request):
        q = DBSession.query(Payment).filter_by(id=iso_pay.sspd_id)
        payment = q.first()
        if not payment:
            return self.ack_payment_not_found()
        payment.denda  = 0
        payment.jml_bayar  = 0
        q = DBSession.query(Invoice).filter_by(id=payment.spt_id)
        invoice = q.first()
        invoice.status_pembayaran = 0  
        iso_rev = IsoReversal()
        iso_rev.id = iso_pay.id
        iso_rev.iso_request = iso_request
        DBSession.add(iso_rev)
        DBSession.flush()
        DBSession.commit()
        self.ack()

    def get_bank_id(self):
        return self.conf['id']

    def get_bank_ip(self):
        return self.conf['ip']

    def get_channel_id(self):
        return int(self.get_value(18))

    # Acknowledgement
    def ack_not_available(self):
        msg = ERR_NOT_AVAILABLE.format(invoice_id=self.invoice_id_raw)
        return self.ack(RC_NOT_AVAILABLE, msg)

    def ack_reversal_done(self):
        msg = ERR_REVERSAL_DONE.format(invoice_id=self.invoice_id_raw)
        return self.ack(RC_ALREADY_PAID, msg) 

    def ack_payment_not_found(self):
        msg = ERR_PAYMENT_NOT_FOUND.format(invoice_id=self.invoice_id_raw)
        return self.ack(RC_NOT_AVAILABLE, msg)
