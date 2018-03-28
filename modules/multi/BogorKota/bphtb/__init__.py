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
from .conf import (
    db_url,
    transaction_schema,
    area_schema,
    iso_schema,
    db_pool_size,
    db_max_overflow,
    persen_denda,
    host,
    )


engine = create_engine(db_url, pool_size=db_pool_size,
                       max_overflow=db_max_overflow)
Base = declarative_base()
Base.metadata.bind = engine
session_factory = sessionmaker()
DBSession = scoped_session(session_factory)
DBSession.configure(bind=engine)
models = Models(Base, transaction_schema, area_schema, iso_schema)
query = Query(models, DBSession)


class BaseResponse(object):
    def __init__(self, parent):
        self.parent = parent

    def is_transaction_owner(self, iso_pay):
        conf = host[self.parent.conf['name']]
        return iso_pay.bank_id == conf['id']

    def is_allowed(self):
        conf = host[self.parent.conf['name']]
        if 'ids' in conf:
            if self.parent.get_bank_id() not in conf['ids']:
                return self.parent.ack_not_allowed()
        return True

    def commit(self):
        DBSession.commit()
        self.parent.ack()


class InquiryResponse(BaseResponse):
    def __init__(self, parent):
        BaseResponse.__init__(self, parent)
        cls = self.get_calc_cls()
        raw = parent.from_iso.get_invoice_id()
        self.calc = cls(models, DBSession, raw, persen_denda)
        module_conf = host[self.parent.conf['name']]
        self.parent.conf.update(module_conf)
        self.invoice_profile = FixLength(self.get_invoice_profile_structure())

    def get_calc_cls(self):
        return CalculateInvoice

    def get_invoice_profile_structure(self):
        return INVOICE_PROFILE

    def init_invoice_profile(self):
        self.invoice_profile.from_dict({
            'kode pajak': 'BPHTB',
            'nama pajak': 'BEA PEROLEHAN HAK ATAS TANAH DAN BANGUNAN',
            })

    def set_invoice_profile(self):
        invoice = self.calc.invoice
        self.invoice_profile.from_dict({
            'npwpd': invoice.wp_npwp,
            'nama': invoice.wp_nama,
            'alamat': invoice.wp_alamat,
            'tagihan': self.calc.tagihan,
            'denda': self.calc.denda,
            'jumlah': self.calc.total,
            'jenis perolehan': invoice.perolehan_id,
            'nilai perolehan': invoice.npop,
            'rt wp': invoice.wp_rt,
            'rw wp': invoice.wp_rw,
            'kelurahan wp': invoice.wp_kelurahan,
            'kecamatan wp': invoice.wp_kecamatan,
            'kota wp': invoice.wp_kota,
            'tahun pajak': invoice.tahun,
            'nik': invoice.wp_identitas,
            'luas tanah': invoice.bumi_luas,
            'luas bangunan': invoice.bng_luas,
            'alamat op': invoice.op_alamat,
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
        if self.calc.total <= 0:
            return self.parent.ack_already_paid_2(self.calc.total)
        return True

    def response(self):
        if not self.is_allowed():
            return
        self.init_invoice_profile()
        if not self.is_valid():
            return self.parent.set_amount(0)
        self.parent.set_amount(self.calc.total)
        self.parent.ack()

    def set_jatuh_tempo(self):
        if self.calc.invoice.tgl_jatuh_tempo:
            self.set_invoice_profile_(
                'jatuh tempo',
                self.calc.invoice.tgl_jatuh_tempo.strftime('%d%m%Y'))

    def set_kode_pos_wp(self):
        kode_pos = self.calc.invoice.wp_kdpos.strip()
        self.set_invoice_profile_('kode pos wp', kode_pos)

    def set_kecamatan_op(self):
        row = self.calc.get_kecamatan()
        if row:
            self.set_invoice_profile_('kecamatan op', row.nm_kecamatan)

    def set_kelurahan_op(self):
        row = self.calc.get_kelurahan()
        if row:
            self.set_invoice_profile_('kelurahan op', row.nm_kelurahan)

    def set_notaris(self):
        row = self.calc.get_customer()
        if row:
            self.set_invoice_profile_('notaris', row.nama)

    def set_invoice_profile_(self, key, value):
        if value:
            self.invoice_profile.from_dict({key: value})

    def set_invoice_profile_to_parent(self):
        self.parent.set_invoice_profile(self.invoice_profile.get_raw())

    def ack_already_paid(self):
        iso_pay = self.calc.get_iso_payment()
        if iso_pay and iso_pay.bank_id == self.parent.get_bank_id():
            ntp = iso_pay.ntp
        else:
            ntp = ''
        self.parent.set_ntp(ntp)
        return self.parent.ack_already_paid()


def inquiry(parent):
    inq = InquiryResponse(parent)
    inq.response()


###########
# Payment #
###########
def create_ntp():
    ntp = NTP(models, DBSession)
    return ntp.create()


class PaymentResponse(InquiryResponse):
    def response(self):
        if not self.is_allowed():
            return
        if not self.is_valid():
            return
        ntp = create_ntp()
        pay = self.create_payment()
        self.create_iso_payment(pay, ntp)
        self.parent.set_ntp(ntp)
        self.commit()

    # Override
    def is_valid(self):
        if not InquiryResponse.is_valid(self, False):
            return
        if self.calc.total != self.parent.from_iso.get_amount():
            return self.parent.ack_insufficient_fund(self.calc.total)
        return True

    def create_payment(self):
        cust = self.calc.get_customer()
        pay_seq = self.calc.get_pay_seq()
        inv = self.calc.invoice
        cabang = self.parent.get_cabang()
        pay = models.Payment()
        pay.tanggal = self.parent.get_transaction_date()
        pay.jam = self.parent.get_transaction_time()
        pay.seq = self.parent.get_sequence()
        pay.transno = self.parent.get_ntb()
        pay.cabang = cabang['kode']
        pay.users = cabang['user']
        pay.bankid = self.parent.get_bank_id()
        pay.txs = self.calc.invoice_id['Kode']
        pay.sspd_id = inv.id
        pay.tahun = inv.tahun
        pay.thn_pajak_sppt = inv.thn_pajak_sppt
        pay.notaris = cust.nama
        pay.bayar = self.calc.total
        pay.denda = self.calc.denda
        pay.bphtbjeniskd = inv.perolehan_id
        pay.no_tagihan = self.parent.from_iso.get_invoice_id()
        pay.pembayaran_ke = pay_seq
        self.set_payment_op(pay)
        self.set_payment_wp(pay)
        DBSession.add(pay)
        self.calc.set_paid()
        DBSession.flush()
        return pay

    def set_payment_op(self, pay):
        inv = self.calc.invoice
        pay.kd_propinsi = inv.kd_propinsi
        pay.kd_dati2 = inv.kd_dati2
        pay.kd_kecamatan = inv.kd_kecamatan
        pay.kd_kelurahan = inv.kd_kelurahan
        pay.kd_blok = inv.kd_blok
        pay.no_urut = inv.no_urut
        pay.kd_jns_op = inv.kd_jns_op
        pay.nop = self.calc.nop.get_raw()
        pay.bumi_luas = inv.bumi_luas
        pay.bumi_njop = inv.bumi_njop
        pay.bng_luas = inv.bng_luas
        pay.bng_njop = inv.bng_njop
        pay.npop = inv.npop

    def set_payment_wp(self, pay):
        inv = self.calc.invoice
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

    def create_iso_payment(self, pay, ntp):
        from_iso = self.parent.from_iso
        iso_pay = models.IsoPayment()
        iso_pay.id = pay.id
        iso_pay.invoice_id = pay.sspd_id
        iso_pay.invoice_no = from_iso.get_invoice_id()
        iso_pay.iso_request = from_iso.raw
        iso_pay.transmission = from_iso.get_transmission()
        iso_pay.settlement = from_iso.get_settlement()
        iso_pay.stan = from_iso.get_stan()
        iso_pay.ntb = from_iso.get_ntb()
        iso_pay.ntp = ntp
        iso_pay.bank_id = self.parent.get_bank_id()
        iso_pay.channel_id = from_iso.get_channel()
        iso_pay.bank_ip = self.parent.get_bank_ip()
        DBSession.add(iso_pay)
        DBSession.flush()


def payment(parent):
    pay = PaymentResponse(parent)
    pay.response()


############
# Reversal #
############
class ReversalResponse(BaseResponse):
    def __init__(self, parent):
        BaseResponse.__init__(self, parent)
        raw = parent.from_iso.get_invoice_id()
        self.rev = Reversal(models, DBSession, raw)

    def response(self):
        if not self.is_allowed():
            return
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


def reversal(parent):
    rev = ReversalResponse(parent)
    rev.response()
