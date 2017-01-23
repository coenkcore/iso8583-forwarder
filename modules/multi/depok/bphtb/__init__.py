#from time import sleep
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )
from tools import (
    FixLength,
    TransactionID,
    )
from multi.bphtb.structure import INVOICE_PROFILE
from models import Models
from query import (
    Query,
    CalculateInvoice,
    NTP,
    Reversal,
    )
from conf import (
    db_url,
    db_pool_size,
    db_max_overflow,
    host,
    )


engine = create_engine(db_url, pool_size=db_pool_size,
                       max_overflow=db_max_overflow)
Base = declarative_base()
Base.metadata.bind = engine
session_factory = sessionmaker()
DBSession = scoped_session(session_factory)
DBSession.configure(bind=engine)
models = Models(Base)
query = Query(models, DBSession)


class BaseResponse(object):
    def __init__(self, parent):
        self.parent = parent
        self.invoice_id_raw = parent.from_iso.get_invoice_id()

    def is_allowed(self):
        bank_name = self.parent.conf['name']
        if bank_name not in host: 
            return self.parent.ack_not_allowed() 
        tp_conf = host[bank_name] 
        if 'kd_tp' not in tp_conf:
            bank_id = self.parent.from_iso.get_bank_id()
            if bank_id not in tp_conf:
                return self.parent.ack_not_allowed() 
            tp_conf = tp_conf[bank_id]
        self.parent.conf.update(tp_conf)
        return True

    def is_transaction_owner(self, iso_pay):
        pay = query.get_payment_from_iso(iso_pay)
        return pay.bank_id == self.parent.conf['id']

    def commit(self):
        DBSession.commit()
        self.parent.ack()



class Inquiry(BaseResponse):
    def __init__(self, parent):
        BaseResponse.__init__(self, parent)
        self.calc = CalculateInvoice(models, DBSession, self.invoice_id_raw)

    def init_invoice_profile(self):
        self.invoice_profile = FixLength(INVOICE_PROFILE)
        self.invoice_profile.from_dict({
            'kode pajak': 'BPHTB', 
            'nama pajak': 'BEA PEROLEHAN HAK ATAS TANAH DAN BANGUNAN',
            })

    def set_invoice_profile(self):
        invoice = self.calc.invoice
        self.invoice_profile.from_dict({
            'npwpd': invoice.npwp_wp,
            'nama' : invoice.nama_wp,
            'alamat': invoice.alamat_wp,
            'tagihan': self.calc.tagihan,
            'jumlah': self.calc.tagihan,
            'jenis perolehan' : invoice.kd_bphtb,
            'nilai perolehan': invoice.npop_omset,
            'rt wp': invoice.rt_wp, 
            'rw wp': invoice.rw_wp, 
            'kelurahan wp': invoice.kelurahan_wp,
            'kecamatan wp': invoice.kecamatan_wp,
            'kota wp': invoice.kota_wp,
            'tahun pajak': invoice.tahun,
            #'nik': invoice.wp_identitas,
            'luas tanah': invoice.luas_bumi,
            'luas bangunan': invoice.luas_bng,
            'alamat op' : invoice.alamat_op,
            })
        self.set_jatuh_tempo()
        self.set_kode_pos_wp()
        self.set_kecamatan_op()
        self.set_kelurahan_op()
        self.set_notaris()
        self.set_invoice_profile_to_parent()

    def is_valid(self, is_need_invoice_profile=True):
        if not self.calc.invoice:
            is_need_invoice_profile and self.set_invoice_profile_to_parent()
            if self.calc.invoice is False:
                return self.parent.ack_invalid_number()
            return self.parent.ack_not_available()
        is_need_invoice_profile and self.set_invoice_profile()
        if self.calc.paid:
            return self.ack_already_paid()
        if self.calc.tagihan <= 0:
            return self.parent.ack_already_paid_2(self.calc.tagihan)
        return True

    def response(self):
        if not self.is_allowed():
            return
        self.init_invoice_profile()
        if not self.is_valid():
            return self.parent.set_amount(0)
        self.parent.set_amount(self.calc.tagihan)
        self.save()

    def set_jatuh_tempo(self):
        if self.calc.invoice.jatuh_tempo:
            self.set_invoice_profile_('jatuh tempo',
                self.calc.invoice.jatuh_tempo.strftime('%d%m%Y'))

    def set_kode_pos_wp(self):
        kode_pos = self.calc.invoice.kodepos_wp.strip()
        self.set_invoice_profile_('kode pos wp', kode_pos)

    def set_kecamatan_op(self):
        if self.calc.invoice.kecamatan_op: 
            self.set_invoice_profile_('kecamatan op',
                self.calc.invoice.kecamatan_op) 

    def set_kelurahan_op(self):
        if self.calc.invoice.kelurahan_op: 
            self.set_invoice_profile_('kelurahan op',
                self.calc.invoice.kelurahan_op)

    def set_notaris(self):
        if self.calc.invoice.nm_notaris: 
            self.set_invoice_profile_('notaris', self.calc.invoice.nm_notaris)

    def set_invoice_profile_(self, key, value):
        if value:
            self.invoice_profile.from_dict({key: value})

    def set_invoice_profile_to_parent(self):
        self.parent.set_invoice_profile(self.invoice_profile.get_raw())

    def ack_already_paid(self):
        iso_pay = self.calc.get_iso_payment()
        ntp = ''
        if iso_pay:
            pay = query.get_payment_from_iso(iso_pay)
            if pay.bank_id == self.parent.conf['id']:
                ntp = pay.ntp
        self.parent.set_ntp(ntp)
        return self.parent.ack_already_paid()

    def save(self):
        inq = models.IsoInquiry()
        inq.tgl = datetime.now()
        inq.invoice_id = self.calc.invoice.id
        inq.bank_id = self.parent.conf['id']
        inq.channel_id = self.parent.from_iso.get_channel()
        inq.stan = self.parent.from_iso.get_stan()
        inq.transmission = self.parent.from_iso.get_transmission()
        inq.settlement = self.parent.from_iso.get_settlement()
        DBSession.add(inq)
        DBSession.flush()
        self.commit()


def inquiry(parent):
    inq = Inquiry(parent)
    inq.response()


###########
# Payment #
###########
def create_ntp():
    ntp = NTP(models, DBSession)
    return ntp.create()


class Payment(Inquiry):
    def response(self):
        if not self.is_valid():
            return
        ntp = create_ntp()
        pay = self.create_payment(ntp)
        self.create_iso_payment(pay)
        self.parent.set_ntp(ntp)
        self.commit()
        #detik = 120
        #self.parent.log_info('Tunggu {d} detik, BTN uji payment timeout.'.format(
        #    d=detik))
        #sleep(detik)

    # Override
    def is_valid(self):
        if not Inquiry.is_valid(self, False):
            return
        if self.calc.tagihan != self.parent.from_iso.get_amount():
            return self.parent.ack_insufficient_fund(self.calc.tagihan)
        return True

    def create_payment(self, ntp):
        inv = self.calc.invoice
        from_iso = self.parent.from_iso
        pay_id = models.iso_payment_seq.execute(engine)
        ke = self.calc.get_pay_seq()
        pay = models.Payment()
        pay.id = pay_id
        pay.ntp = ntp
        pay.invoice_id = inv.id
        pay.source_id = inv.source_id
        pay.tahun = inv.tahun
        pay.no_tagihan = inv.no_tagihan
        pay.pembayaran_ke = ke
        pay.jml_bayar = from_iso.get_amount()
        pay.tgl_bayar = from_iso.get_transaction_datetime() 
        pay.ntb = from_iso.get_ntb()
        pay.luas_bumi = inv.luas_bumi
        pay.luas_bng = inv.luas_bng
        pay.npop_omset = inv.npop_omset
        pay.kd_bphtb = inv.kd_bphtb
        pay.nm_notaris = inv.nm_notaris 
        self.set_payment_wp(pay)
        self.set_payment_op(pay)
        self.set_payment_bank(pay)
        self.set_payment_invoice(pay)
        DBSession.add(pay)
        self.calc.set_paid()
        DBSession.flush()
        return pay 

    def set_payment_invoice(self, pay):
        inv = self.calc.invoice
        pay.invoice_id = inv.id
        pay.tgl_invoice = inv.tgl
        pay.jatuh_tempo = inv.jatuh_tempo
        pay.jml_tagihan = inv.jml_tagihan
        pay.nop = inv.nop
        pay.npop_omset = inv.npop_omset
        pay.persen_pajak = inv.persen_pajak
        pay.kd_rekening = inv.kd_rekening
        pay.nm_rekening = inv.nm_rekening
        pay.kd_bphtb = inv.kd_bphtb
        pay.nm_notaris = inv.nm_notaris

    def set_payment_bank(self, pay):
        conf = self.parent.conf
        pay.bank_id = conf['id']
        pay.channel_id = self.parent.from_iso.get_channel()
        cabang = self.parent.get_cabang()
        pay.nm_kcp_bank = cabang['kode'] 
        pay.operators = cabang['user'] 
        pay.kode_bank = str(conf['id']).zfill(3)
        pay.kd_kanwil_bank = conf['kd_kanwil_bank']
        pay.kd_kppbb_bank = conf['kd_kppbb_bank']
        pay.kd_bank_tunggal = conf['kd_bank_tunggal']
        pay.kd_bank_persepsi = conf['kd_bank_persepsi']
        pay.kd_tp = conf['kd_tp']

    def set_payment_op(self, pay):
        inv = self.calc.invoice
        pay.nama_op = inv.nama_op
        pay.alamat_op = inv.alamat_op
        pay.rt_op = inv.rt_op
        pay.rw_op = inv.rw_op
        pay.kelurahan_op = inv.kelurahan_op
        pay.kecamatan_op = inv.kecamatan_op
        pay.kota_op = inv.kota_op
        pay.kodepos_op = inv.kodepos_op

    def set_payment_wp(self, pay):
        inv = self.calc.invoice
        pay.nama_wp = inv.nama_wp
        pay.npwp_wp = inv.npwp_wp
        pay.alamat_wp = inv.alamat_wp
        pay.rt_wp = inv.rt_wp
        pay.rw_wp = inv.rw_wp
        pay.kelurahan_wp = inv.kelurahan_wp
        pay.kecamatan_wp = inv.kecamatan_wp
        pay.kota_wp = inv.kota_wp
        pay.kodepos_wp = inv.kodepos_wp

    def create_iso_payment(self, pay):
        from_iso = self.parent.from_iso
        iso_pay = models.IsoPayment()
        iso_pay.id = iso_pay.payment_id = pay.id
        iso_pay.iso_request = from_iso.raw.upper()
        iso_pay.transmission = from_iso.get_transmission()
        iso_pay.settlement = from_iso.get_settlement()
        iso_pay.stan = from_iso.get_stan()
        DBSession.add(iso_pay)
        DBSession.flush()


def payment(parent):
    pay = Payment(parent)
    pay.response()


############
# Reversal #
############
class ReversalResponse(BaseResponse):
    def __init__(self, parent):
        BaseResponse.__init__(self, parent)
        self.rev = Reversal(models, DBSession, self.invoice_id_raw)

    def response(self):
        if not self.rev.invoice:
            return self.parent.ack_payment_not_found()
        if not self.rev.is_paid():
            return self.parent.ack_invoice_open()
        if not self.rev.payment:
            return self.parent.ack_payment_not_found()
        iso_pay = self.rev.get_iso_payment()
        if not iso_pay:
            return self.parent.ack_payment_not_found_2()
        if not self.is_transaction_owner(iso_pay):
            return self.parent.ack_payment_owner()
        self.rev.set_unpaid()
        self.commit()
        #detik = 120
        #self.parent.log_info('Tunggu {d} detik, BTN uji reversal timeout.'.format(
        #    d=detik))
        #sleep(detik)

def reversal(parent):
    rev = ReversalResponse(parent)
    rev.response()


