import sys
from sqlalchemy.sql import func
sys.path[0:0] = ['/usr/share/opensipkd/modules']
from base_models import DBSession
from tools import FixLength
sys.path[0:0] = ['/etc/opensipkd']
from bphtb_fix_conf import nip_pencatat
sys.path[0:0] = ['/usr/share/opensipkd-forwarder/modules/bphtb_fix']
from bphtb_fix_db_transaction import (
    BaseDbTransaction,
    luas,
    )
from bphtb_fix_structure import NOP
from models import (
    OtherDBSession,
    Invoice,
    Payment,
    Customer,
    Pembeli,
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

    def set_invoice_profile(self): # inherited
        invoice = self.calc.invoice
        nop = FixLength(NOP)
        nop.set_raw(invoice.nop)
        cust = OtherDBSession.query(Customer).filter_by(
                register_id=invoice.reg_ppat).first()
        kec = OtherDBSession.query(Kecamatan).filter_by(
                skodekecamatan=nop['Kecamatan']).first()
        kel = OtherDBSession.query(Kelurahan).filter_by(
                nkecamatan=kec.nkecamatan,
                skodekelurahan=nop['Kelurahan']).first()
        wp = OtherDBSession.query(Pembeli).filter_by(
                kd_bphtb=invoice.kd_booking).first()
        if not wp:
            return self.ack_wp()
        self.invoice_profile.from_dict({
            'Luas Tanah'             : self.luas(int(invoice.luas_tanah)),
            'Luas Bangunan'          : self.luas(int(invoice.luas_bng)),
            'NPOP'                   : invoice.npop,
            'Jenis Perolehan Hak'    : invoice.jns_perolehan,
            'Nama Notaris'           : cust.fullname,
            'Nama Wajib Pajak'       : wp.nm_pembeli,
            'NPWP'                   : wp.npwp_pembeli,
            'Alamat WP'              : wp.alamat_pembeli,
            'Alamat OP'              : invoice.alamat_op,
            'Kota OP'                : invoice.kota_op,
            'Kelurahan WP'           : wp.kelurahan_pembeli,
            'Kecamatan WP'           : wp.kecamatan_pembeli,
            'Jumlah Bayar'           : self.calc.tagihan,
            'Jumlah Denda'           : 0, 
            })
        self.invoice_profile2.from_dict({
            'RT WP'                  : wp.rt_pembeli,
            'RW WP'                  : wp.rw_pembeli,
            'Kode Pos WP'            : wp.kodepos_pembeli,
            'Kelurahan OP'           : kel and kel.skelurahan or '',
            'Kecamatan OP'           : kec and kec.skecamatan or '',
            'Tahun Pajak'            : invoice.tgl_rekam.strftime('%Y'),
            })
        return True

    ###########
    # Payment #
    ###########
    def is_payment_id_found(self, trx_id): # inherited 
        q = DBSession.query(IsoPayment).filter_by(ntp=trx_id)
        return q.first()

    def create_payment(self): # inherited
        transaction_datetime, transmission_datetime, settlement_date = \
            self.from_iso.get_dates()
        if not transaction_datetime or not transmission_datetime or \
            not settlement_date:
            return
        pay = self.create_bayar(transaction_datetime)
        iso_pay = IsoPayment()
        iso_pay.invoice_no = self.invoice_id_raw
        iso_pay.pembayaran_ke = pay.pembayaran_bphtb_ke 
        iso_pay.iso_request = self.from_iso.getRawIso().upper()
        iso_pay.transaction = transaction_datetime
        iso_pay.transmission = transmission_datetime
        iso_pay.settlement = settlement_date
        iso_pay.stan = self.from_iso.get_stan()
        iso_pay.ntb = self.from_iso.get_ntb()
        iso_pay.ntp = pay.ntpd
        iso_pay.bank_id = self.conf['bank_id']
        iso_pay.channel_id = self.from_iso.get_channel_id()
        iso_pay.bank_ip = self.conf['ip']
        DBSession.add(iso_pay)
        self.set_ntp(pay.ntpd)

    def create_bayar(self, transaction_datetime):
        inv = self.calc.invoice
        pay = get_last_payment(inv.kd_booking)
        if pay:
            pembayaran_ke = int(pay.pembayaran_bphtb_ke) + 1
        else:
            pembayaran_ke = 1
        pay_id = OtherDBSession.query(func.max(Payment.id)).scalar()
        if pay_id:
            pay_id += 1
        else:
            pay_id = 1
        ntp = self.create_payment_id()
        pay = Payment()
        pay.id = pay_id
        pay.nop = inv.nop
        pay.kd_booking = inv.kd_booking
        pay.ntpd = ntp
        pay.pembayaran_bphtb_ke = pembayaran_ke
        pay.bphtb_dibayar = self.calc.total
        pay.tgl_pembayaran_bphtb = transaction_datetime 
        pay.nip_rekam_byr = nip_pencatat
        pay.reversal = 0
        OtherDBSession.add(pay)
        self.calc.set_paid()
        return pay 

    ############
    # Reversal #
    ############
    def get_reversal_cls(self): # inherited
        return IsoPaymentReversal

    def commit(self): # inherited
        OtherDBSession.commit()
        BaseDbTransaction.commit(self)

    ###################
    # Acknowledgement #
    ###################
    def ack_wp(self):
        msg = 'Profil wajib pajak untuk kode booking {n} tidak ada.'.format(
                n=self.calc.invoice.kd_booking)
        self.ack_other(msg)
