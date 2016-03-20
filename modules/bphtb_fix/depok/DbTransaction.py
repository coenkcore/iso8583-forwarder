from random import randrange
from datetime import datetime
from ISO8583.ISO8583 import ISO8583
import sys
sys.path[0:0] = ['/usr/share/opensipkd/modules']
from base_models import DBSession
from tools import FixLength
sys.path[0:0] = ['/etc/opensipkd']
from bphtb_fix_conf import host
sys.path[0:0] = ['/usr/share/opensipkd-forwarder/modules/bphtb_fix']
from bphtb_fix_db_transaction import (
    BaseDbTransaction,
    luas,
    )
from bphtb_fix_structure import NOP 
from models import (
    Invoice,
    Payment,
    IsoInquiry,
    IsoPayment,
    IsoReversal,
    Bank,
    iso_payment_seq,
    )
from PaymentReversal import IsoPaymentReversal
from CalculateInvoice import CalculateInvoice


def get_payment_id():
    return iso_payment_seq.execute(DBSession.bind)

def invoice2payment(invoice):
    q = DBSession.query(Payment).filter_by(invoice_id=invoice.id)
    return q.first()

class DbTransaction(BaseDbTransaction):
    def get_calc_cls(self): # inherited
        return CalculateInvoice

    def set_invoice_profile(self): # inherited
        inv = self.calc.invoice
        jml_akhiran_nol = self.get_jml_akhiran_nol()
        self.invoice_profile.from_dict({
            'Luas Tanah': luas(inv.luas_bumi, jml_akhiran_nol),
            'Luas Bangunan': luas(inv.luas_bng, jml_akhiran_nol),
            'NPOP': int(inv.npop_omset),
            'Jenis Perolehan Hak': inv.kd_bphtb,
            'Nama Notaris': inv.nm_notaris,
            'Nama Wajib Pajak': inv.nama_wp,
            'NPWP': inv.npwp_wp,
            'Alamat WP': inv.alamat_wp,
            'Alamat OP': inv.alamat_op,
            'Kota OP': inv.kota_op,
            'Kelurahan WP': inv.kelurahan_wp,
            'Kecamatan WP': inv.kecamatan_wp,
            'Jumlah Bayar': int(inv.jml_tagihan),
            'Jumlah Denda': 0})
        self.invoice_profile2.from_dict({
            'RT WP': inv.rt_wp,
            'RW WP': inv.rw_wp,
            'Kode Pos WP': inv.kodepos_wp,
            'Kelurahan OP': inv.kelurahan_op,
            'Kecamatan OP': inv.kecamatan_op,
            'Tahun Pajak': inv.tahun})
        self.setBit(47, self.invoice_profile.get_raw())
        self.setBit(48, self.invoice_profile2.get_raw())
        self.setBit(61, inv.nop or '')
        return True

    ###########
    # Inquiry #
    ###########
    def save_inquiry(self): # inherited
        transaction_date, transmission_date, settlement_date = self.get_dates()
        if not transaction_date or not transmission_date or not settlement_date:
            return
        inq = IsoInquiry()
        inq.tgl = datetime.now()
        inq.invoice_id = self.calc.invoice.id
        inq.bank_id = self.conf['bank_id'] 
        inq.channel_id = self.from_iso.get_channel_id()
        inq.stan = self.from_iso.get_stan()
        inq.transmission = transmission_date
        inq.settlement = settlement_date
        DBSession.add(inq)
        self.commit()

    ###########
    # Payment #
    ###########
    def is_payment_id_found(self, trx_id): # inherited
        q = DBSession.query(Payment).filter_by(source_id=2, ntp=trx_id)
        return q.first()

    def get_prefix_code(self): # inherited
        prefix = ''
        for fieldname in ['kd_kanwil_bank', 'kd_kppbb_bank', 'kd_bank_tunggal',
            'kd_bank_persepsi']:
            prefix += self.conf[fieldname]
        return prefix

    def create_payment(self): # inherited
        transaction_date, transmission_date, settlement_date = self.get_dates()
        if not transaction_date or not transmission_date or not settlement_date:
            return
        bayar = self.create_bayar()
        pay = IsoPayment()
        pay.id = pay.payment_id = bayar.id
        pay.iso_request = self.from_iso.getRawIso().upper()
        pay.transmission = transmission_date
        pay.settlement = settlement_date
        pay.stan = self.from_iso.get_stan()
        DBSession.flush() # Agar foreign key hadir dulu
        DBSession.add(pay)

    def create_bayar(self):
        inv = self.calc.invoice
        q = DBSession.query(Payment).filter_by(source_id=2,
                    tahun=inv.tahun, no_tagihan=inv.no_tagihan)
        q = q.order_by('pembayaran_ke DESC')
        bayar = q.first()
        if bayar:
            ke = bayar.pembayaran_ke + 1
        else:
            ke = 1
        ntp = self.create_payment_id()
        payment_id = get_payment_id()
        bayar = Payment()
        bayar.id = payment_id
        bayar.invoice_id = inv.id
        bayar.source_id = inv.source_id
        bayar.tahun = inv.tahun
        bayar.no_tagihan = inv.no_tagihan
        bayar.pembayaran_ke = ke
        bayar.jml_bayar = self.from_iso.get_amount()
        #bayar.tgl_bayar = datetime.now() 
        bayar.tgl_bayar = self.from_iso.get_transaction_datetime() 
        bayar.ntb = self.from_iso.get_ntb()
        bayar.luas_bumi = inv.luas_bumi
        bayar.luas_bng = inv.luas_bng
        bayar.npop_omset = inv.npop_omset
        bayar.kd_bphtb = inv.kd_bphtb
        bayar.nm_notaris = inv.nm_notaris 
        # Wajib Pajak
        bayar.nama_wp = inv.nama_wp
        bayar.npwp_wp = inv.npwp_wp
        bayar.alamat_wp = inv.alamat_wp
        bayar.rt_wp = inv.rt_wp
        bayar.rw_wp = inv.rw_wp
        bayar.kelurahan_wp = inv.kelurahan_wp
        bayar.kecamatan_wp = inv.kecamatan_wp
        bayar.kota_wp = inv.kota_wp
        bayar.kodepos_wp = inv.kodepos_wp
        # Objek Pajak
        bayar.nama_op = inv.nama_op
        bayar.alamat_op = inv.alamat_op
        bayar.rt_op = inv.rt_op
        bayar.rw_op = inv.rw_op
        bayar.kelurahan_op = inv.kelurahan_op
        bayar.kecamatan_op = inv.kecamatan_op
        bayar.kota_op = inv.kota_op
        bayar.kodepos_op = inv.kodepos_op
        # Bank
        bayar.bank_id = self.conf['bank_id']
        bayar.channel_id = self.from_iso.get_channel_id()
        bayar.nm_kcp_bank = '' #FIXME
        bayar.operators = '' #FIXME
        bayar.kode_bank = str(self.conf['bank_id']).zfill(3)
        for fieldname in ['kd_kanwil_bank', 'kd_kppbb_bank', 'kd_bank_tunggal',
                'kd_bank_persepsi', 'kd_tp']:
            value = self.conf[fieldname]
            value = self.get_real_value(value)
            bayar.from_dict({fieldname: value})
        # Invoice
        bayar.invoice_id = inv.id
        bayar.tgl_invoice = inv.tgl
        bayar.jatuh_tempo = inv.jatuh_tempo
        bayar.jml_tagihan = inv.jml_tagihan
        bayar.nop = inv.nop
        bayar.npop_omset = inv.npop_omset
        bayar.persen_pajak = inv.persen_pajak
        bayar.kd_rekening = inv.kd_rekening
        bayar.nm_rekening = inv.nm_rekening
        bayar.kd_bphtb = inv.kd_bphtb
        bayar.nm_notaris = inv.nm_notaris
        # Identitas transaksi
        bayar.ntp = ntp
        self.set_ntp(ntp)
        DBSession.add(bayar)
        self.calc.set_paid()
        return bayar

    ############
    # Reversal #
    ############
    def get_reversal_cls(self): # inherited
        return IsoPaymentReversal
