import sys
#import traceback
#from StringIO import StringIO
#from random import randrange
#from types import DictType
#from ISO8583.ISO8583 import ISO8583

from datetime import datetime
from types import DictType

sys.path[0:0] = ['/etc/opensipkd']
from bca_conf import (
    #host,
    is_update_sppt,
    nip_rekam_byr_sppt,
    )
sys.path[0:0] = ['/usr/share/opensipkd-forwarder/modules/bca/']
from pbb import PbbDbSession
from log_models import MyFixLength

sys.path[0:0] = ['/usr/share/opensipkd/modules']
from tools import FixLength

#LOCAL CLASS
from pbb_structure import INVOICE_ID, INVOICE_PROFILE
from CalculateInvoice import (
    CalculateInvoice,
    query_sppt,
    )
   
from models import (
    Invoice,
    Pembayaran,
    Kelurahan,
    Kecamatan,
    Kabupaten,
    Propinsi,
    )
    
from DbTools import query_pembayaran

def cari_kelurahan(propinsi, kabupaten, kecamatan, kelurahan):
    q = PbbDbSession.query(Kelurahan).filter_by(
            kd_propinsi=propinsi,
            kd_dati2=kabupaten,
            kd_kecamatan=kecamatan,
            kd_kelurahan=kelurahan)
    r = q.first()
    return r and r.nm_kelurahan or ''

def cari_kecamatan(propinsi, kabupaten, kecamatan):
    q = PbbDbSession.query(Kecamatan).filter_by(
            kd_propinsi=propinsi,
            kd_dati2=kabupaten,
            kd_kecamatan=kecamatan)
    r = q.first()
    return r and r.nm_kecamatan or ''

def cari_propinsi(propinsi):
    q = PbbDbSession.query(Propinsi).filter_by(kd_propinsi=propinsi)
    r = q.first()
    return r and r.nm_propinsi or ''

def nama_jalan_op(sppt):
    return sppt.jln_wp_sppt

# def inquiry_id():
    # return INQUIRY_SEQ.execute(DBSession.bind)

def create_payment_id(prefix):
    max_loop = 10
    loop = 0
    while True:
        acak = randrange(11111111, 99999999)
        acak = str(acak)
        trx_id = ''.join([prefix, acak])
        print('Check Trx ID %s' % trx_id)
        q = DBSession.query(Payment).filter_by(id=trx_id)
        found = q.first()
        if not found:
            return trx_id
        loop += 1
        if loop == max_loop:
            print('*** Max loop for create payment ID. Call your programmer please.')
            return

# def pay2invoice_id(pay):
    # return ''.join([pay.propinsi, pay.kabupaten, pay.kecamatan,
        # pay.kelurahan, pay.blok, pay.urut, pay.jenis, str(pay.tahun)])

def inq2bayar(inv):
    q = query_pembayaran(inv.kd_propinsi,
            inv.kd_dati2,
            inv.kd_kecamatan,
            inv.kd_kelurahan,
            inv.kd_blok,
            inv.no_urut,
            inv.kd_jns_op,
            inv.thn_pajak_sppt)
            
    q = q.order_by('pembayaran_sppt_ke DESC')
    return q.first()
    
def sppt2nop(sppt):
    return sppt.kd_propinsi + sppt.kd_dati2 + sppt.kd_kecamatan + \
           sppt.kd_kelurahan + sppt.kd_blok + sppt.no_urut + sppt.kd_jns_op

FIELD_BANK = ['kd_kanwil', 'kd_kantor', 'kd_tp']
FIELD_BANK_NON_TP = FIELD_BANK[:-1]

           
class PbbDbTransaction(): #
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
        #Transaction.__init__(self, *args, **kwargs)

    def get_invoice(self):
        #self.invoice_id_raw = invoice_id_raw
        if not self.invoice_id.set_raw(self.invoice_id_raw):
            return self.ack_invalid_number()
        self.invoice_id2profile()
        
        self.calc = CalculateInvoice(
            self.invoice_id['Propinsi'],
            self.invoice_id['Kabupaten'],
            self.invoice_id['Kecamatan'],
            self.invoice_id['Kelurahan'],
            self.invoice_id['Blok'],
            self.invoice_id['Urut'],
            self.invoice_id['Jenis'],
            self.invoice_id['Tahun Pajak'])
            
        if self.calc.invoice:
            inv = self.calc.invoice
            self.invoice_profile.from_dict({
                'Nama': inv.nm_wp_sppt,
                'Luas Tanah': int(inv.luas_bumi_sppt),
                'Luas Bangunan': int(inv.luas_bng_sppt),
                'Lokasi': nama_jalan_op(inv),
                'Jatuh Tempo': inv.tgl_jatuh_tempo_sppt.strftime('%d%m%Y'),
                'Tagihan': self.calc.tagihan,
                'Denda': self.calc.denda,
                'Total Bayar': self.calc.total})
            self.calc.invoice_profile=self.invoice_profile
            #self.channel = self.get_channel()
        return self.calc

    def invoice_id2profile(self):
        nama_kelurahan = self.nama_kelurahan()
        nama_kecamatan = self.nama_kecamatan()
        nama_propinsi = self.nama_propinsi()
        self.invoice_profile.from_dict({
            'Propinsi': self.invoice_id['Propinsi'],
            'Kabupaten': self.invoice_id['Kabupaten'],
            'Kecamatan': self.invoice_id['Kecamatan'],
            'Kelurahan': self.invoice_id['Kelurahan'],
            'Blok': self.invoice_id['Blok'],
            'Urut': self.invoice_id['Urut'],
            'Jenis': self.invoice_id['Jenis'],
            'Tahun Pajak': self.invoice_id['Tahun Pajak'],
            'Nama Kelurahan': nama_kelurahan,
            'Nama Kecamatan': nama_kecamatan,
            'Nama Propinsi': nama_propinsi})

    ###########
    # Profile #
    ###########
    def nama_kelurahan(self):
        return cari_kelurahan(
            self.invoice_id['Propinsi'],
            self.invoice_id['Kabupaten'],
            self.invoice_id['Kecamatan'],
            self.invoice_id['Kelurahan'])

    def nama_kecamatan(self):
        return cari_kecamatan(
            self.invoice_id['Propinsi'],
            self.invoice_id['Kabupaten'],
            self.invoice_id['Kecamatan'])

    def nama_propinsi(self):
        return cari_propinsi(self.invoice_id['Propinsi'])

    def create_payment(self, *args, **kwargs):
        total_bayar = kwargs['total_bayar']
        transaction_date = kwargs['tgl_bayar']
        self.transaction_date = transaction_date.date()
        bayar, urutan_bayar = self.bayar(total_bayar)
        return bayar, urutan_bayar
        
    def bayar(self, total_bayar):
        pay = self.calc.invoice
        bayar = inq2bayar(pay)
        if bayar:
            ke = bayar.pembayaran_sppt_ke + 1
        else:
            ke = 1
        bayar = Pembayaran()
        bayar.kd_propinsi = pay.kd_propinsi #self.invoice_id['Propinsi']
        bayar.kd_dati2 = pay.kd_dati2 #self.invoice_id['Kabupaten']
        bayar.kd_kecamatan = pay.kd_kecamatan #self.invoice_id['Kecamatan']
        bayar.kd_kelurahan = pay.kd_kelurahan #self.invoice_id['Kelurahan']
        bayar.kd_blok = pay.kd_blok #self.invoice_id['Blok']
        bayar.no_urut = pay.no_urut #self.invoice_id['Urut']
        bayar.kd_jns_op = pay.kd_jns_op #self.invoice_id['Jenis']
        bayar.thn_pajak_sppt = pay.thn_pajak_sppt #self.invoice_id['Tahun Pajak']
        bayar.pembayaran_sppt_ke = ke
        bayar.tgl_rekam_byr_sppt = datetime.now()
        bayar.tgl_pembayaran_sppt = self.transaction_date
        bayar.jml_sppt_yg_dibayar = self.calc.total #total_bayar 
        bayar.denda_sppt = self.calc.denda #inq.denda
        bayar.nip_rekam_byr_sppt = nip_rekam_byr_sppt
        for fieldname in FIELD_BANK:
            value = self.conf[fieldname]
            value = self.get_real_value(value)
            bayar.from_dict({fieldname: value})
        print pay.to_dict()
        pay.status_pembayaran_sppt='1'
        PbbDbSession.add(bayar)
        PbbDbSession.add(pay)
        return bayar, ke
        
    def commit(self):
        PbbDbSession.flush()
        PbbDbSession.commit()
        #self.ack()
       
    def get_real_value(self, value):
        if type(value) is not DictType:
            return value
        if self.channel in value:
            return value[self.channel]
        if 'default' in value:
            return value['default']
        return '00'

    def get_field_bank(self):
        return FIELD_BANK

    def get_field_bank_non_tp(self):
        return FIELD_BANK_NON_TP


 