import sys
from ISO8583.ISO8583 import ISO8583
sys.path.insert(0, '/usr/share/opensipkd/modules')
from base_models import DBSession
from tools import FixLength
sys.path.insert(0, '/usr/share/opensipkd-forwarder/modules/bphtb_fix')
from bphtb_fix_db_transaction import BaseDbTransaction
from models import (
    Invoice,
    Payment,
    Customer,
    Kecamatan,
    Kelurahan,
    IsoPayment,
    IsoReversal,
    )
from PaymentReversal import (
    IsoPaymentReversal,
    get_last_payment,
    )
from CalculateInvoice import CalculateInvoice


class DbTransaction(BaseDbTransaction):
    def get_calc_cls(self): # inherited
        return CalculateInvoice
 
    def get_customer(self):
        q = DBSession.query(Customer).filter_by(id=self.calc.invoice.ppat_id)
        return q.first()

    def get_kecamatan(self):
        q = DBSession.query(Kecamatan).filter_by(
                kd_propinsi = self.calc.invoice.kd_propinsi,
                kd_dati2 = self.calc.invoice.kd_dati2,
                kd_kecamatan = self.calc.invoice.kd_kecamatan)
        return q.first()

    def get_kelurahan(self):
        q =  kel = DBSession.query(Kelurahan).filter_by(
                kd_propinsi = self.calc.invoice.kd_propinsi,
                kd_dati2 = self.calc.invoice.kd_dati2,
                kd_kecamatan = self.calc.invoice.kd_kecamatan,
                kd_kelurahan = self.calc.invoice.kd_kelurahan)
        return q.first()

    def set_invoice_profile(self): # inherited
        invoice = self.calc.invoice
        cust = self.get_customer()
        kec = self.get_kecamatan()
        kel = self.get_kelurahan()
        self.invoice_profile.from_dict({
            'Luas Tanah'          : self.luas(invoice.bumi_luas),
            'Luas Bangunan'       : self.luas(invoice.bng_luas),
            'NPOP'                : invoice.npop,
            'Jenis Perolehan Hak' : invoice.perolehan_id,
            'Nama Notaris'        : cust.nama,
            'Nama Wajib Pajak'    : invoice.wp_nama, 
            'NPWP'                : invoice.wp_npwp, 
            'Alamat WP'           : invoice.wp_alamat, 
            'Alamat OP'           : invoice.op_alamat,
            'Kota OP'             : invoice.wp_kota,
            'Kelurahan WP'        : invoice.wp_kelurahan, 
            'Kecamatan WP'        : invoice.wp_kecamatan, 
            'Jumlah Bayar'        : self.calc.tagihan,
            'Jumlah Denda'        : self.calc.denda, 
            })
        self.invoice_profile2.from_dict({
            'RT WP'        : invoice.wp_rt, 
            'RW WP'        : invoice.wp_rw, 
            'Kode Pos WP'  : invoice.wp_kdpos, 
            'Kelurahan OP' : kel and kel.nm_kelurahan or None,
            'Kecamatan OP' : kec and kec.nm_kecamatan or None,
            'Tahun Pajak'  : invoice.tahun,
            })
        return True

    ###########
    # Payment #
    ###########
    def is_payment_id_found(self, trx_id): # inherited 
        q = DBSession.query(IsoPayment).filter_by(ntp=trx_id)
        return q.first()

    def get_pay_seq(self):
        q = DBSession.query(Payment).filter_by(sspd_id=self.calc.invoice.id)
        pay = q.first()
        if pay:
            return pay.pembayaran_ke + 1
        return 1

    def create_payment(self): # inherited
        transaction_datetime, transmission_datetime, settlement_date = \
            self.from_iso.get_dates()
        if not transaction_datetime or not transmission_datetime or \
            not settlement_date:
            return
        ntp = self.create_payment_id()
        pay = self._create_payment(transaction_datetime)
        DBSession.add(pay)
        DBSession.flush() # get payment id
        iso_pay = self._create_iso_payment(pay, ntp)
        iso_pay.ntp = ntp
        iso_pay.bank_id = self.conf['id'] 
        iso_pay.channel_id = self.get_channel_id()
        iso_pay.bank_ip = self.get_bank_ip()
        DBSession.add(iso_pay)
        return iso_pay.ntp

    def _create_payment(self, tgl):
        cust = self.get_customer()
        pay_seq = self.get_pay_seq()
        inv = self.calc.invoice
        pay = Payment()
        pay.tanggal = tgl.date()
        pay.jam = tgl.time()
        pay.seq = self.get_value(37)
        pay.transno = self.get_ntb()
        pay.cabang = self.get_value(107)[:4]
        pay.users = self.get_value(107)[4:]
        pay.bankid = self.conf['id']
        pay.txs = self.calc.invoice_struct['Kode']
        pay.sspd_id = self.calc.invoice.id
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
        pay.no_tagihan = self.get_invoice_id()
        pay.pembayaran_ke = pay_seq
        return pay

    def _create_iso_payment(self, pay, ntp):
        iso_pay = IsoPayment()
        iso_pay.id = pay.id
        iso_pay.invoice_id = pay.sspd_id
        iso_pay.invoice_no = self.calc.invoice_id
        iso_pay.iso_request = ISO8583.getRawIso(self.from_iso).upper()
        iso_pay.transmission = self.from_iso.get_transmission_datetime()
        iso_pay.settlement = self.from_iso.get_settlement_date()
        iso_pay.stan = self.from_iso.get_stan()
        iso_pay.ntb = self.from_iso.get_ntb()
        iso_pay.ntp = ntp
        iso_pay.bank_id = self.conf['id'] 
        iso_pay.channel_id = self.get_channel_id()
        iso_pay.bank_ip = self.get_bank_ip()
        return iso_pay

    ############
    # Reversal #
    ############
    def get_reversal_cls(self): # inherited
        return IsoPaymentReversal
