from datetime import datetime
from random import randrange
from webr_structure import (
    #INVOICE_ID, 
    INVOICE_PROFILE)
    
from webr_calculate_invoice import (
    CalculateInvoice,
    #decode_invoice_id_raw,
    )
from webr_models import (
    Invoice,
    # Customer,
    # CustomerUsaha,
    # Kelurahan,
    # Kecamatan,
    # Pajak,
    # Rekening,
    #Unit,
    Pembayaran,
    )

import sys
sys.path.insert(0, '/usr/share/opensipkd/modules')
from tools import FixLength
sys.path.insert(0, '/usr/share/opensipkd-forwarder/modules/multi')
from log_models import MyFixLength

from webr import WebrDBSession

class WebrDbTransaction():
    def __init__(self, *args, **kwargs):
        #self.invoice_id = MyFixLength(INVOICE_ID)
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
        # if not self.invoice_id.set_raw(self.invoice_id_raw):
            # return 
            
        self.calc = CalculateInvoice(self.invoice_id_raw)
        if self.calc.invoice:
            self.calc.hitung()
            self.set_invoice_profile()
            self.calc.invoice_profile = self.invoice_profile
            
        return self.calc
        
    def set_invoice_profile(self):
        pass
        # cust, alamat2, cust_usaha = self.get_customer()
        # rek = self.get_rek()
        # nama = self.calc.invoice.r_nama or cust.customernm
        # nama_ = []
        # if cust_usaha.opnm:
            # nama_.append(cust_usaha.opnm) 
            
        # if nama:
            # nama_.append(nama)
            
        # nama_lengkap = '/'.join(nama_)
        self.invoice_profile.from_dict({
            'npwpd': self.calc.invoice.op_kode,
            'nama': self.calc.invoice.op_nama,
            'alamat': self.calc.invoice.op_alamat_1,
            'alamat2': self.calc.invoice.op_alamat_2,
            'tagihan': self.calc.tagihan,
            'denda': self.calc.denda,
            'jumlah': self.calc.total,
            'kode_pajak': self.calc.invoice.rek_kode,
            'nama_pajak': self.calc.invoice.rek_nama,
            'kode_skpd': self.calc.invoice.rek_kode,
            'nama_skpd': self.calc.invoice.rek_nama,
            'masa_pajak': " s.d ".join([self.calc.invoice.periode_1.strftime('%d-%m-%Y'),
                                  self.calc.invoice.periode_2.strftime('%d-%m-%Y')]),
            #'jth_tempo': self.calc.invoice.jatuhtempotgl.strftime('%Y%m%d'),
            })
        
    def commit(self):
        #pass
        WebrDBSession.flush()
        WebrDBSession.commit()
        #self.ack()

    def get_sspdno(self):
        q = WebrDBSession.query(Pembayaran).filter_by(tahun=datetime.now().year).\
                order_by(Pembayaran.sspdno.desc())
        pay = q.first()
        if pay:
            return pay.sspdno + 1
        return 1
        
    def get_pay_seq(self):
        q = WebrDBSession.query(Pembayaran).filter_by(arinvoice_id=self.calc.invoice.id).\
                           order_by('pembayaran_ke desc')
        pay = q.first()
        if pay:
            return pay.pembayaran_ke + 1
        return 1
        
    def create_payment(self, *args, **kwargs):
        self.seq = kwargs['seq']
        self.bank_id = kwargs['bank_id']
        self.ntb = kwargs['ntb']
        self.ntp = kwargs['ntp']
        self.tgl_bayar = kwargs['tgl_bayar']
        self.channel_id = kwargs['channel_id']
        ke = self.get_pay_seq() 
        #self._create_payment()
        #sspdno = self.get_sspdno()
        pay = Pembayaran()
        pay.tahun_id = datetime.now().year #self.invoice_id['tahun']
        pay.unit_id = self.calc.invoice.unit_id
        pay.pembayaran_ke = ke 
        pay.tgl_bayar = self.tgl_bayar.date() 
        pay.arinvoice_id = self.calc.invoice.id
        pay.bunga = self.calc.denda
        pay.bayar = self.calc.total
        pay.create_date = pay.update_date = datetime.now()
        pay.tgl_bayar = self.tgl_bayar.date()
        pay.printed = 1 
        pay.bank_id = self.bank_id 
        pay.channel_id = self.channel_id 
        pay.ntb = self.ntb
        pay.ntp = self.ntp
        pay.posted = 0
        # pay.bulan_telat
        # pay.hitung_bunga
        #pay.sspdjam = self.tgl_bayar.time()
        WebrDBSession.add(pay)
        self.calc.set_paid()
        WebrDBSession.flush()
        return pay, ke

    # Invoice Profile #
    def get_customer(self):
        q = WebrDBSession.query(CustomerUsaha).\
                filter_by(id=self.calc.invoice.customer_usaha_id)
        cust_usaha = q.first()
        q_cust = WebrDBSession.query(Customer).filter_by(id=cust_usaha.customer_id)
        cust = q_cust.first()
        if not cust_usaha.kelurahan_id:
            return cust, '', cust_usaha 
        q_kel = WebrDBSession.query(Kelurahan).filter_by(id=cust_usaha.kelurahan_id)
        kelurahan = q_kel.first()
        q_kec = WebrDBSession.query(Kecamatan).filter_by(id=kelurahan.kecamatan_id)
        kecamatan = q_kec.first()
        alamat2 = ','.join([kelurahan.kelurahannm, kecamatan.kecamatannm])
        return cust, alamat2, cust_usaha

    def get_rek(self):
        q_pajak = WebrDBSession.query(Pajak).\
                    filter_by(id=self.calc.invoice.pajak_id)
        pajak = q_pajak.first()
        q_rek = WebrDBSession.query(Rekening).filter_by(id=pajak.rekening_id)
        return q_rek.first()
