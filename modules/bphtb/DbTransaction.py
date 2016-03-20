import sys
from types import (
    StringType,
    UnicodeType,
    )
from datetime import datetime
sys.path.insert(0, '/usr/share/opensipkd/modules')
from base_models import DBSession
sys.path.insert(0, '/etc/opensipkd')
from bphtb_conf import is_need_sppt
if is_need_sppt:
    from models import Sppt
from transaction import Transaction
from models import (
    Payment,
    IsoPayment,
    )

def numerik(s):
    if type(s) in [StringType, UnicodeType]:
        s = s.strip()
    v = s or 0
    return float(v)

def bulat(s):
    return int(numerik(s))


class DbTransaction(Transaction):
    def get_invoice(self):
        nop = self.from_iso.get_nop()
        if not self.nop.set_raw(nop):
            return self.err_nop()
        profile = self.from_iso.get_profile()
        if not self.invoice_profile.set_raw(profile):
            return self.err_invoice_profile()
        profile2 = self.from_iso.get_profile2()
        if not self.invoice_profile2.set_raw(profile2):
            return self.err_invoice_profile()
        bank_profile = self.from_iso.get_bank_profile()
        if not self.bank_profile.set_raw(bank_profile):
            return self.err_bank_profile()
        if not is_need_sppt:
            return True
        q = DBSession.query(Sppt).filter_by(
                kd_propinsi=self.nop['Propinsi'],
                kd_dati2=self.nop['Kabupaten'],
                kd_kecamatan=self.nop['Kecamatan'],
                kd_kelurahan=self.nop['Kelurahan'],
                kd_blok=self.nop['Blok'],
                no_urut=self.nop['Urut'],
                jenis=self.nop['Jenis'],
                thn_pajak_sppt=self.invoice_profile2['Tahun Pajak'])
        row = q.first()
        if row:
            return row
        self.err_not_available(self.invoice_profile2['Tahun Pajak'])

    def payment_response(self):
        if not self.get_invoice():
            return
        pay = Payment()
        pay.seq = self.from_iso.get_seq()
        pay.tanggal = pay.jam = kini = datetime.now()
        pay.nop = self.from_iso.get_nop()
        pay.wp_nama = self.invoice_profile['Nama WP'] or ''
        pay.txs = 'NB' #FIXME
        pay.transno = self.invoice_profile2['Nomor Transaksi'] or ''
        pay.bankid = 1 #FIXME
        pay.bumi_luas = bulat(self.invoice_profile['Luas Tanah'])
        pay.bng_luas = bulat(self.invoice_profile['Luas Bangunan'])
        pay.wp_rt = self.invoice_profile2['RT WP']
        pay.wp_rw = self.invoice_profile2['RW WP']
        pay.wp_kelurahan = self.invoice_profile2['Kelurahan WP'] 
        pay.wp_kecamatan = self.invoice_profile2['Kecamatan WP'] 
        pay.wp_alamat = self.invoice_profile['Alamat WP'] 
        pay.wp_kdpos = self.invoice_profile2['Kode Pos WP'] 
        pay.npop = self.invoice_profile['NPOP'] 
        pay.bayar = self.from_iso.get_amount() 
        pay.cabang = self.bank_profile['Kode Cabang'] 
        pay.users = self.bank_profile['User ID'] 
        pay.notaris = self.invoice_profile['Nama Notaris']
        pay.bphtbjeniskd = self.invoice_profile['Jenis Perolehan Hak'] 
        pay.tahun = self.invoice_profile2['Tahun Pajak']
        DBSession.add(pay)
        if not self.flush():
            return
        iso_pay = IsoPayment()
        iso_pay.trx_id = pay.id
        iso_pay.from_iso(self.from_iso)
        DBSession.add(iso_pay)
        if self.flush():
            self.commit()

    def flush(self):
        try:
            DBSession.flush()
        except:
            return self.err_other(sys.exc_info()[1])
        return True

    def commit(self):
        DBSession.commit()
        self.ack()

    def reversal_response(self):
        iso_pay = IsoPayment.search_iso(self.from_iso)
        if not iso_pay:
            return self.err_payment_not_found()
        q = DBSession.query(Payment).filter_by(id=pay.trx_id)
        pay = q.first()
        q = DBSession.query(Reversal).filter_by(pay_trx_id=trx.id)
        reversal = q.first()
        if reversal:
            return self.err_already_canceled()
        reversal = Reversal()
        reversal.pay_trx_id = trx.id
        reversal.tgl = datetime.now()
        reversal.iso_request = self.from_iso.getRawIso()
        DBSession.add(reversal)
        if self.flush():
            self.commit()
