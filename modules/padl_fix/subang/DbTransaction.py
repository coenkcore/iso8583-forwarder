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
from CalculateInvoice import (
     CalculateInvoice,
     decode_invoice_id_raw,
    )
import sys
sys.path.insert(0, '/usr/share/opensipkd/modules')
from tools import FixLength
from base_models import (
    Base,
    DBSession,
    )
from models import (
    Customer,
    CustomerUsaha,
    InvoiceSpt,
    Payment,
    PaymentDet,
    )



ERR_MAX_LOOP = 'Max loop for create payment ID. Call your programmer please.'

def create_ntp(prefix=''):
    max_loop = 10
    loop = 0
    #while True:
    acak = randrange(11111111, 99999999)
    acak = str(acak)
    trx_id = ''.join([prefix, acak])
        #found = DBSession.query(IsoPayment).filter_by(ntp=trx_id).first()
        #if not found:
        #    return trx_id
        #loop += 1
        #if loop == max_loop:
        #    raise Exception(ERR_MAX_LOOP)

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
        if not self.calc.total or self.calc.total<0: #self.calc.paid:
            return self.ack(RC_ALREADY_PAID, ERR_ALREADY_PAID.format(
                invoice_id=self.invoice_id_raw))
        if self.calc.total > 0:
            self.set_amount(self.calc.total)
        return self.calc.invoice

    def set_invoice_profile(self):
        invoice = self.calc.invoice
        cust  = DBSession.query(Customer).filter_by(npwp_gab = invoice.no_pokok_wp,
                                          jn_wajib_pajak = invoice.jn_wajib_pajak).first()
        custu = DBSession.query(CustomerUsaha).\
                          filter_by(no_pokok_wp       = invoice.no_pokok_wp,
                                    jn_wajib_pajak    = invoice.jn_wajib_pajak,
                                    jn_usaha_wp       = invoice.jn_usaha_wp,
                                    kd_usaha          = invoice.kd_usaha).first()
        
        awal  = invoice.masa1.strftime('%d%m%Y')
        akhir = invoice.masa2.strftime('%d%m%Y')
        self.invoice_profile.from_dict({
            'NPWPD': invoice.no_pokok_wp.replace('.','').replace(' ',''),
            'Nama': cust.nama_wp, 
            'Alamat 1': custu.alamat_usaha,
            'Alamat 2': custu.alamat_usaha,
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
        
        if float(self.from_iso.get_value(4)) <>  float(self.calc.total):
            print self.from_iso.get_value(4), self.calc.total
            return
        
        if not inv:
            return
        inv_dicted = inv.to_dict()
        ntp = create_ntp(str(datetime.now().year))
        payment = Payment()
        payment.tahun           = datetime.now().year 
        payment.no_sspd         = self.from_iso.get_value(11)
        payment.tgl_sspd        = self.from_iso.get_settlement()
        payment.no_ketetapan    = 'no_ketetapan' in inv_dicted and inv_dicted['no_ketetapan'] or '00'
        payment.kd_urusan       = inv.kd_urusan      
        payment.kd_bidang       = inv.kd_bidang      
        payment.kd_unit         = inv.kd_unit        
        payment.kd_sub          = inv.kd_sub         
        payment.kd_setoran      = 1 #inv.kd_setoran     
        payment.jn_setoran      = 1 #inv.jn_setoran
        payment.jn_dokumen      = 'jns_surat' in inv_dicted and inv_dicted['jns_surat'] or 0     
        payment.no_bku          = ntp #inv.no_bku         
        payment.no_pokok_wp     = inv.no_pokok_wp    
        payment.jn_wajib_pajak  = inv.jn_wajib_pajak 
        payment.jn_usaha_wp     = inv.jn_usaha_wp    
        payment.kd_usaha        = inv.kd_usaha       
        payment.jn_pajak        = inv.jn_pajak       
        payment.jn_pemungutan   = inv.jn_pemungutan  
        payment.masa1           = inv.masa1          
        payment.masa2           = inv.masa2          
        payment.kd_bank         = self.from_iso.get_value(11)=='110' and 1 or 0
        #payment.nm_penerima     = inv.nm_penerima    
        payment.nip_penerima    = self.from_iso.get_value(48) #inv.nip_penerima   
        #payment.jbt_penerima    = inv.jbt_penerima   
        payment.nm_penyetor     = 'H2H'    
        payment.alamat_penyetor = 'BJB'
        #payment.keterangan      = inv.keterangan     
        
        DBSession.add(payment)
        DBSession.flush()
        paymentdet = PaymentDet()
        paymentdet.tahun          = payment.tahun 
        paymentdet.no_sspd        = payment.no_sspd
        paymentdet.no_id       = 1
        paymentdet.kd_rek_1    = inv.rekening_pokok[:1]
        paymentdet.kd_rek_2    = inv.rekening_pokok[1:2]
        paymentdet.kd_rek_3    = inv.rekening_pokok[2:3]
        paymentdet.kd_rek_4    = inv.rekening_pokok[3:5]
        paymentdet.kd_rek_5    = inv.rekening_pokok[5:7]
        paymentdet.kd_rek_6    = inv.rekening_pokok[7:9]
        paymentdet.nilai       = self.calc.tagihan
        DBSession.add(paymentdet)
        DBSession.flush()
        if self.calc.denda:
          paymentdet = PaymentDet()
          paymentdet.tahun          = payment.tahun 
          paymentdet.no_sspd        = payment.no_sspd
          paymentdet.no_id       = 2
          paymentdet.kd_rek_1    = 4
          paymentdet.kd_rek_2    = 1
          paymentdet.kd_rek_3    = 4
          paymentdet.kd_rek_4    = 7
          paymentdet.kd_rek_5    = inv.rekening_pokok[3:5]
          paymentdet.kd_rek_6    = 1
          paymentdet.nilai       = self.calc.denda
          DBSession.add(paymentdet)
          DBSession.flush()
        #paymentdet.keterangan  = Column(String(150))
        DBSession.flush()
        DBSession.commit()
        
        #bank_id = self.get_bank_id()
        #channel_id = self.get_channel_id()
        
        
        #iso_pay = self.save_payment()
        #iso_pay.ntp = ntp
        #iso_pay.bank_id = bank_id
        #iso_pay.channel_id = channel_id
        #iso_pay.bank_ip = self.get_bank_ip()
        #self.calc.set_paid()
        #DBSession.add(iso_pay)
        #DBSession.add(self.calc.invoice)
        #DBSession.flush()
        #DBSession.commit()
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
