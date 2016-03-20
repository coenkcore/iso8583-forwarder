import sys
#import traceback
#from StringIO import StringIO
#from random import randrange
#from datetime import datetime
#from ISO8583.ISO8583 import ISO8583

from datetime import datetime

sys.path[0:0] = ['/usr/share/opensipkd/modules']
sys.path[0:0] = ['/etc/opensipkd']
from bca_conf import host



sys.path[0:0] = ['/usr/share/opensipkd-forwarder/modules/bca/']
from bphtb import BphtbDBSession
from log_models import MyFixLength

sys.path[0:0] = ['/usr/share/opensipkd/modules']
from tools import FixLength

#LOCAL CLASS
from bphtb_fix_structure import INVOICE_ID, INVOICE_PROFILE, NOP
from bphtb_calculate_invoice import CalculateInvoice

def luas(n, jumlah_nol=0):
    f = '%%.%df' % jumlah_nol
    s = f % n
    return s.replace('.', '')
from bphtb_models import (
    #Invoice,
    Payment,
    Customer,
    Kecamatan,
    Kelurahan,
    #IsoPayment,
    #IsoReversal,
    )


class BphtbDbTransaction():
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
        
    def get_customer(self):
        q = BphtbDBSession.query(Customer).filter_by(id=self.calc.invoice.ppat_id)
        return q.first()

    def get_kecamatan(self):
        q = BphtbDBSession.query(Kecamatan).filter_by(
                kd_propinsi = self.calc.invoice.kd_propinsi,
                kd_dati2 = self.calc.invoice.kd_dati2,
                kd_kecamatan = self.calc.invoice.kd_kecamatan)
        return q.first()

    def get_kelurahan(self):
        q =  kel = BphtbDBSession.query(Kelurahan).filter_by(
                kd_propinsi = self.calc.invoice.kd_propinsi,
                kd_dati2 = self.calc.invoice.kd_dati2,
                kd_kecamatan = self.calc.invoice.kd_kecamatan,
                kd_kelurahan = self.calc.invoice.kd_kelurahan)
        return q.first()
        
    def get_pay_seq(self):
        q = BphtbDBSession.query(Payment).filter_by(sspd_id=self.calc.invoice.id).\
                           order_by('pembayaran_ke desc')
        pay = q.first()
        if pay:
            return pay.pembayaran_ke + 1
        return 1

        
    def get_invoice(self):
        if not self.invoice_id.set_raw(self.invoice_id_raw):
            return self.ack_invalid_number()
        self.invoice_profile = FixLength(INVOICE_PROFILE)
        self.calc = CalculateInvoice(self.invoice_id_raw)

        if self.calc.invoice:
        
            invoice = self.calc.invoice
            cust = self.get_customer()
            kec = self.get_kecamatan()
            kel = self.get_kelurahan()

            self.invoice_profile.from_dict({
                'npwpd': invoice.wp_npwp, 
                'nama' : invoice.wp_nama, 
                'alamat': invoice.wp_alamat, 
                'kode_pajak': 'BPHTB', 
                'nama_pajak': 'BEA PEROLEHAN HAK ATAS TANAH DAN BANGUNAN',
                'jth_tempo': invoice.tgl_jatuh_tempo and invoice.tgl_jatuh_tempo.strftime('%d%m%Y') or '00000000',
                'tagihan': self.calc.pokok,
                'denda': self.calc.denda, 
                'jumlah': self.calc.total,
                'jns_perolehan' : invoice.perolehan_id,
                'nilai_perolehan': invoice.npop,
                'notaris' : cust.nama,
                'rt_wp': invoice.wp_rt, 
                'rw_wp': invoice.wp_rw, 
                'kode_pos_wp': invoice.wp_kdpos.strip() and invoice.wp_kdpos.strip()  or '00000', 
                'kelurahan_wp': invoice.wp_kelurahan, 
                'kecamatan_wp': invoice.wp_kecamatan, 
                'kota_wp': invoice.wp_kota,
                'tahun_pajak': invoice.tahun,
                'no_ktp': invoice.wp_identitas,
                'luas_tnh': self.luas(invoice.bumi_luas),
                'luas_bng': self.luas(invoice.bng_luas),
                'alamat_op' : invoice.op_alamat,
                'kelurahan_op' : kel and kel.nm_kelurahan or None,
                'kecamatan_op' : kec and kec.nm_kecamatan or None,
                })
            self.calc.invoice_profile=self.invoice_profile
            #self.channel = self.get_channel()
        return self.calc

    def get_jml_akhiran_nol(self):
        return 'akhiran_nol_pada_luas' in self.conf and \
            self.conf['akhiran_nol_pada_luas'] or 0

    def luas(self, nilai):
        return luas(nilai, self.get_jml_akhiran_nol())

    def _set_invoice_profile(self):
        ok = self.set_invoice_profile()
        self.setBit(47, self.invoice_profile.get_raw())
        self.setBit(48, self.invoice_profile2.get_raw())
        self.setBit(61, self.calc.get_nop())
        return ok

    def set_ntp(self, ntp=''): # Nomor Transaksi Pemda
        self.setBit(57, ntp)

    def get_dates(self):
        return self.get_transaction_datetime(), \
               self.get_transmission_datetime(), \
               self.get_settlement_date()

    def save_inquiry(self):
        self.ack()


    ###########
    # Payment #
    ###########
    def is_payment_id_found(self, trx_id):
        raise OverridePlease

    def create_payment(self, *args, **kwargs):
        self.seq = kwargs['seq']
        self.bank_id = kwargs['bank_id']
        self.ntb = kwargs['ntb']
        pay, ke = self._create_payment(kwargs['tgl_bayar'])
        #DBSession.add(pay)
        #DBSession.flush() # get payment id
        return pay, ke 
        
    def _create_payment(self, tgl):
        cust = self.get_customer()
        pay_seq = self.get_pay_seq()
        inv = self.calc.invoice
        pay = Payment()
        pay.tanggal = tgl.date()
        pay.jam = tgl.time()
        pay.seq = self.seq
        pay.transno = self.ntb
        pay.bankid = self.bank_id
        #pay.cabang = self.get_value(107)[:4]
        #pay.users = self.get_value(107)[4:]
        pay.txs = self.calc.invoice_struct['kode']
        pay.sspd_id = inv.id
        pay.nop = self.calc.nop_struct.get_raw()
        pay.tahun = inv.tahun
        pay.kd_propinsi = inv.kd_propinsi
        pay.kd_dati2 = inv.kd_dati2
        pay.kd_kecamatan = inv.kd_kecamatan
        pay.kd_kelurahan = inv.kd_kelurahan
        pay.kd_blok = inv.kd_blok
        pay.no_urut = inv.no_urut
        pay.kd_jns_op = inv.kd_jns_op
        pay.thn_pajak_sppt = inv.thn_pajak_sppt
        pay.wp_nama = inv.wp_nama
        pay.wp_alamat = inv.wp_alamat
        pay.wp_blok_kav = inv.wp_blok_kav
        pay.wp_rt = inv.wp_rt
        pay.wp_rw = inv.wp_rw
        pay.wp_kelurahan = inv.wp_kelurahan
        pay.wp_kecamatan = inv.wp_kecamatan
        pay.wp_kota = inv.wp_kota
        pay.wp_provinsi = inv.wp_provinsi
        pay.wp_kdpos = inv.wp_kdpos
        pay.wp_identitas = inv.wp_identitas
        pay.wp_identitaskd = inv.wp_identitaskd
        pay.wp_npwp = inv.wp_npwp
        pay.notaris = cust.nama 
        pay.bumi_luas = inv.bumi_luas
        pay.bumi_njop = inv.bumi_njop
        pay.bng_luas = inv.bng_luas
        pay.bng_njop = inv.bng_njop
        pay.npop = inv.npop
        pay.bayar = self.calc.total
        pay.denda = self.calc.denda
        pay.bphtbjeniskd = inv.perolehan_id
        pay.no_tagihan = self.invoice_id_raw #get_invoice_id()
        pay.pembayaran_ke = pay_seq
        inv.status_pembayaran = 1
        
        BphtbDBSession.add(pay)
        BphtbDBSession.add(inv)
        return pay, pay_seq


    def get_real_value(self, value):
        if type(value) is not DictType:
            return value
        if self.from_iso.get_channel_id() in value:
            return value[self.channel_id]
        if 'default' in value:
            return value['default']
        return '00'

    def get_prefix_code(self):
        return ''

    ############
    # Reversal #
    ############
    def _reversal_response(self):
        transaction_datetime, transmission_datetime, settlement_date = \
            self.from_iso.get_dates()
        if not transaction_datetime or not transmission_datetime or \
           not settlement_date:
            return
        cls = self.get_reversal_cls()
        rev = cls(self.from_iso)
        if not rev.is_reversal_ready():
            return self.ack_invoice_open(self.from_iso.get_invoice_id())
        rev.set_unpaid()
        self.commit()

    def reversal_response(self):
        try:
            self._reversal_response()
        except:
            f = StringIO()
            traceback.print_exc(file=f)
            self.log_error(f.getvalue())
            f.close()
            self.ack_other('other error')

    def get_reversal_cls(self):
        raise OverridePlease

    ###################
    # Acknowledgement #
    ###################
    def ack_not_available(self):
        self.ack_not_available_2(self.invoice_id_raw)

    def ack_not_available_2(self, invoice_id):
        msg = ERR_NOT_AVAILABLE.format(invoice_id=invoice_id)
        self.ack(RC_NOT_AVAILABLE, msg)

    def ack_already_paid(self):
        ntp = self.calc.get_ntp()
        if ntp:
            self.set_ntp(ntp)
        msg = ERR_ALREADY_PAID.format(invoice_id=self.invoice_id_raw)
        self.ack(RC_ALREADY_PAID, msg)

    def ack_insufficient_fund(self, total_bayar):
        msg = ERR_INSUFFICIENT_FUND.format(invoice_id=self.invoice_id_raw,
                bayar=total_bayar,
                tagihan=self.calc.total)
        self.ack(RC_INSUFFICIENT_FUND, msg)

    def ack_payment_not_found(self):
        self.ack(RC_NOT_AVAILABLE, ERR_PAYMENT_NOT_FOUND)

    def ack_invoice_open(self, invoice_id):
        msg = ERR_INVOICE_OPEN.format(invoice_id=invoice_id)
        self.ack(RC_ALREADY_PAID, msg)

    def ack_other(self, msg):
        self.ack(RC_OTHER_ERROR, msg)

    def commit(self):
        BphtbDBSession.flush()
        BphtbDBSession.commit()
        #self.ack()

############
# Reversal #
############
class BphtbIsoReversal(object):
    def __init__(self, from_iso):
        self.from_iso = from_iso
        self.reversal_iso_request = ISO8583.getRawIso(from_iso).upper()
