from datetime import datetime
from random import randrange
from padl_structure import INVOICE_ID, INVOICE_PROFILE
from padl_calculate_invoice import (
    CalculateInvoice,
    decode_invoice_id_raw,
    )
from padl_models import (
    Invoice,
    Customer,
    CustomerUsaha,
    Kelurahan,
    Kecamatan,
    Pajak,
    Rekening,
    Pembayaran,
    )

import sys
sys.path.insert(0, '/usr/share/opensipkd/modules')
from tools import FixLength
sys.path.insert(0, '/usr/share/opensipkd-forwarder/modules/bca')
from log_models import MyFixLength

from padl import PadlDBSession

class PadlDbTransaction():
    def __init__(self, *args, **kwargs):
        self.invoice_id = MyFixLength(INVOICE_ID)
        self.invoice_id_raw = None # Cache
        self.invoice_profile = MyFixLength(INVOICE_PROFILE)
        if 'invoice_id' in kwargs:
            self.invoice_id_raw = kwargs['invoice_id']
        if 'conf' in kwargs:
            self.conf = kwargs['conf']
        if 'channel' in kwargs:
            self.channel = kwargs['channel']

    def get_invoice(self):
        #self.invoice_id = decode_invoice_id_raw(self.invoice_id_raw)
        if not self.invoice_id.set_raw(self.invoice_id_raw):
            return 
            
        self.calc = CalculateInvoice(self.invoice_id['tahun'],
                        self.invoice_id['spt_no'])
        if self.calc.invoice:
            self.calc.hitung()
            self.set_invoice_profile()
        return self.calc
        
    def set_invoice_profile(self):
        cust, alamat2, cust_usaha = self.get_customer()
        rek = self.get_rek()
        nama = self.calc.invoice.r_nama or cust.customernm
        nama_ = []
        if cust_usaha.opnm:
            nama_.append(cust_usaha.opnm) 
            
        if nama:
            nama_.append(nama)
            
        nama_lengkap = '/'.join(nama_)
        self.invoice_profile.from_dict({
            'npwpd': cust.npwpd,
            'nama': nama_lengkap,
            'alamat': cust.alamat,
            #'alamat': alamat2,
            'kode_pajak': rek.rekeningkd,
            'nama_pajak': rek.rekeningnm,
            'tagihan': self.calc.tagihan,
            'denda': self.calc.denda,
            'jumlah': self.calc.total,
            'jth_tempo': self.invoice.tgl_jatuh_tempo,
            'masa': " s.d ".join([self.calc.invoice.masadari.strftime('%Y%m%d'),
                                  self.calc.invoice.masasd.strftime('%Y%m%d')]),
            })

    def commit(self):
        PadlDBSession.flush()
        PadlDBSession.commit()
        self.ack()

    def get_sspdno(self):
        q = PadlDBSession.query(Pembayaran).filter_by(tahun=self.calc.invoice.tahun).\
                order_by(Pembayaran.sspdno.desc())
        pay = q.first()
        if pay:
            return pay.sspdno + 1
        return 1

    def save_payment(self):
        sspdno = self.get_sspdno()
        bank_id = self.get_bank_id()
        channel_id = self.get_channel_id()
        pay = Pembayaran()
        pay.tahun = self.invoice_id['Tahun']
        pay.sspdno = sspdno 
        pay.spt_id = self.calc.invoice.id
        pay.denda = pay.bunga = self.calc.denda
        pay.jml_bayar = self.calc.total
        pay.create_date = pay.write_date = pay.sspdtgl = datetime.now()
        pay.printed = 1 
        PadlDBSession.add(pay)
        self.calc.set_paid()
        PadlDBSession.flush()
        return pay

    # Invoice Profile #
    def get_customer(self):
        q = PadlDBSession.query(CustomerUsaha).\
                filter_by(id=self.calc.invoice.customer_usaha_id)
        cust_usaha = q.first()
        q_cust = PadlDBSession.query(Customer).filter_by(id=cust_usaha.customer_id)
        cust = q_cust.first()
        if not cust_usaha.kelurahan_id:
            return cust, '', cust_usaha 
        q_kel = PadlDBSession.query(Kelurahan).filter_by(id=cust_usaha.kelurahan_id)
        kelurahan = q_kel.first()
        q_kec = PadlDBSession.query(Kecamatan).filter_by(id=kelurahan.kecamatan_id)
        kecamatan = q_kec.first()
        alamat2 = ','.join([kelurahan.kelurahannm, kecamatan.kecamatannm])
        return cust, alamat2, cust_usaha

    def get_rek(self):
        q_pajak = PadlDBSession.query(Pajak).\
                    filter_by(id=self.calc.invoice.pajak_id)
        pajak = q_pajak.first()
        q_rek = PadlDBSession.query(Rekening).filter_by(id=pajak.rekening_id)
        return q_rek.first()
