import sys
import os
from time import time
from datetime import datetime
sys.path.insert(0, '/usr/share/opensipkd/modules')
from base_models import DBSession
from tools import FixLength
#sys.path.insert(0, '/usr/share/opensipkd-forwarder/modules/bphtb')
from bphtb.structure import (
    PAYMENT_CODE,
    INVOICE_PROFILE,
    INVOICE_PROFILE2,
    )
from bphtb.transaction import Transaction
from bphtb.models import Payment


get_job_ready = [False]

class DbTransaction(Transaction):
    # Override
    def is_network_response(self):
        get_job_ready[0] = True
        return Transaction.is_network_response(self)

    # Override
    def is_payment(self):
        return

    # Override
    def is_transaction_response(self):
        ok = Transaction.is_transaction_response(self)
        if ok:
            return False
        return ok

    # Override
    def get_func_name(self):
        return self.is_echo_test_request() or self.is_payment() or \
               self.is_sign_on_request() or self.is_sign_off_request()

    def payment_response(self):
        pass

    def payment_request(self, invoice_id_raw):
        nop = invoice_id_raw[:-5]
        tahun = invoice_id_raw[-5:]
        print('NOP {nop} tahun {tahun}'.format(nop=nop, tahun=tahun))
        q = DBSession.query(Payment).filter_by(nop=nop, tahun=tahun).\
                order_by(Payment.id.desc())
        pay = q.first()
        invoice_profile = FixLength(INVOICE_PROFILE)
        invoice_profile['Luas Tanah'] = pay.bumi_luas 
        invoice_profile['Luas Bangunan'] = pay.bng_luas
        invoice_profile['NPOP'] = pay.npop
        invoice_profile['Jenis Perolehan Hak'] = pay.bphtbjeniskd
        invoice_profile['Nama Notaris'] = pay.notaris
        invoice_profile['Nama WP'] = pay.wp_nama
        #invoice_profile['NPWP'] = ''
        invoice_profile['Alamat WP'] = pay.wp_alamat
        invoice_profile2 = FixLength(INVOICE_PROFILE2)
        invoice_profile2['RT WP'] = pay.wp_rt
        invoice_profile2['RW WP'] = pay.wp_rw
        invoice_profile2['Kode Pos WP'] = pay.wp_kdpos
        invoice_profile2['Kelurahan WP'] = pay.wp_kelurahan
        invoice_profile2['Kecamatan WP'] = pay.wp_kecamatan
        #invoice_profile2['Nama Bank'] = ''
        #invoice_profile2['Nama KCP Bank'] = ''
        invoice_profile2['Nama Operator Bank'] = ''
        invoice_profile2['Tahun Pajak'] = tahun
        #invoice_profile2['Jenis Setoran'] = ''
        invoice_profile2['ID Operator Bank'] = ''
        invoice_profile2['Nomor Transaksi'] = pay.transno
        self.setMTI('0200')
        kini = datetime.now()
        self.setBit(2, kini.strftime('%Y%m%d%H%M%S')) 
        self.setBit(3, PAYMENT_CODE)
        self.setBit(4, 1000)
        self.setBit(7, kini.strftime('%m%d%H%M%S')) 
        self.setBit(11, kini.strftime('%H%M%S')) 
        self.setBit(12, kini.strftime('%H%M%S')) 
        self.setBit(13, kini.strftime('%m%d')) 
        self.setBit(15, kini.strftime('%m%d')) 
        self.setBit(18, '6010') 
        self.setBit(22, '021')
        self.setBit(32, '110')
        self.setBit(33, '00110')
        self.setBit(35, '')
        self.setBit(37, kini.strftime('%H%M%S')) 
        self.setBit(41, '000')
        self.setBit(42, '000000000000000')
        self.setBit(43, 'Nama Bank')
        self.setBit(47, invoice_profile.get_raw())
        self.setBit(48, invoice_profile2.get_raw())
        self.setBit(49, '390')
        self.setBit(59, 'PAY')
        self.setBit(61, nop)
        self.setBit(63, '214')
        self.setBit(102, '')
        self.setBit(107, '0000AAAA')



spool_file = '/tmp/bphtb-invoice.txt'

def get_job():
    if not get_job_ready[0]:
        return
    if not os.path.exists(spool_file):
        print('{f} tidak ada, abaikan.'.format(f=spool_file))
        return
    f = open(spool_file)
    invoice_id = f.read()
    f.close()
    os.remove(spool_file)
    iso = DbTransaction()
    iso.payment_request(invoice_id)
    return iso
