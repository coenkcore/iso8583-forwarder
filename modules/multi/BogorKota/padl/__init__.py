from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )
from tools import FixLength
from multi.bphtb.structure import INVOICE_PROFILE
from .models import Models
from .query import (
    CalculateInvoice,
    NTP,
    Reversal,
    )
from .conf import (
    db_url,
    db_schema,
    db_pool_size,
    db_max_overflow,
    persen_denda,
    host,
    load_iso_models,
    )


engine = create_engine(db_url, pool_size=db_pool_size,
                       max_overflow=db_max_overflow)
Base = declarative_base()
Base.metadata.bind = engine
session_factory = sessionmaker()
DBSession = scoped_session(session_factory)
DBSession.configure(bind=engine)
models = Models(Base, db_schema)
if load_iso_models:
    iso_models = IsoModels(Base)
else:
    iso_models = None


class BaseResponse(object):
    def __init__(self, parent):
        self.parent = parent
        self.invoice_id_raw = parent.from_iso.get_invoice_id()
        self.models = self.get_models()
        self.iso_models = self.get_iso_models()

    def get_models(self):
        return models

    def get_iso_models(self):
        return iso_models

    def is_transaction_owner(self, iso_pay):
        conf = host[self.parent.conf['name']]
        if 'id' in conf:
            return iso_pay.bank_id == conf['id']
        return iso_pay.bank_id in conf['ids']

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
        self.parent = parent
        cls = self.get_calc_cls()
        invoice_id_raw = parent.from_iso.get_invoice_id()
        self.calc = cls(self.models, DBSession, invoice_id_raw, persen_denda)
        module_conf = host[self.parent.conf['name']]
        self.parent.conf.update(module_conf)

    def get_calc_cls(self):
        return CalculateInvoice

    def init_invoice_profile(self):
        self.invoice_profile = FixLength(INVOICE_PROFILE)
        self.invoice_profile.from_dict({
            'kode pajak': 'PADL',
            'nama pajak': 'PENDAPATAN ASLI DAERAH LAINNYA',
            })

    def set_invoice_profile(self):
        invoice = self.calc.invoice
        op = self.calc.get_op()
        kel = self.calc.get_kelurahan(op.kelurahan_id)
        kec = self.calc.get_kecamatan(kel.kecamatan_id)
        wp = self.calc.get_wp(op)
        nama = self.get_nama_wp(op, wp)
        self.invoice_profile.from_dict({
            'npwpd': wp.npwpd,
            'nama': nama,
            'alamat': wp.alamat,
            'tagihan': self.calc.tagihan,
            'denda': self.calc.denda,
            'jumlah': self.calc.total,
            'alamat op': op.opalamat,
            'kelurahan op': kel.kelurahannm,
            'kecamatan op': kec.kecamatannm,
            'kode pos wp': wp.wpkodepos,
            })
        self.set_jatuh_tempo()
        self.set_invoice_profile_to_parent()

    def get_nama_wp(self, op, wp):
        nama_ = []
        if op.opnm:
            nama_.append(op.opnm)
        nama = self.calc.invoice.r_nama or wp.customernm
        if nama:
            nama_.append(nama)
        return ','.join(nama_)

    def is_valid(self, is_need_invoice_profile=True):
        if not self.calc.invoice:
            is_need_invoice_profile and self.set_invoice_profile_to_parent()
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
        if self.calc.invoice.jatuhtempotgl:
            self.set_invoice_profile_(
                'jatuh tempo',
                self.calc.invoice.jatuhtempotgl.strftime('%d%m%Y'))

    def set_invoice_profile_(self, key, value):
        if value:
            self.invoice_profile.from_dict({key: value})

    def set_invoice_profile_to_parent(self):
        self.parent.set_invoice_profile(self.invoice_profile.get_raw())

    def ack_already_paid(self):
        iso_pay = self.calc.get_iso_payment()
        if iso_pay and iso_pay.bank_id == self.parent.conf['id']:
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

class PaymentResponse(InquiryResponse):
    def response(self):
        if not self.is_allowed():
            return
        if not self.is_valid():
            return
        self.create_payment()
        self.commit()

    # Override
    def is_valid(self):
        if not InquiryResponse.is_valid(self, False):
            return
        if self.calc.total != self.parent.from_iso.get_amount():
            return self.parent.ack_insufficient_fund(self.calc.total)
        return True

    def create_payment(self):
        sspdno = self.calc.get_pay_seq()
        pay = self.models.Payment()
        pay.tahun = self.calc.invoice.tahun
        pay.spt_id = self.calc.invoice.id
        pay.sspdno = sspdno
        pay.denda = pay.bunga = self.calc.denda
        pay.jml_bayar = self.calc.total
        pay.create_date = pay.write_date = datetime.now()
        pay.sspdtgl = self.parent.from_iso.get_transaction_datetime()
        pay.printed = 1
        self.before_save(pay)
        DBSession.add(pay)
        self.calc.set_paid()
        DBSession.flush()
        self.create_iso_payment(pay)

    def before_save(self, pay):
        pass

    def create_ntp(self):
        ntp = NTP(self.iso_models, DBSession)
        return ntp.create()

    def create_iso_payment(self, pay):
        from_iso = self.parent.from_iso
        ntp = self.create_ntp()
        iso_pay = self.iso_models.IsoPayment()
        iso_pay.id = pay.id
        iso_pay.invoice_id = pay.spt_id
        iso_pay.iso_request = from_iso.raw
        iso_pay.transmission = from_iso.get_transmission()
        iso_pay.settlement = from_iso.get_settlement()
        iso_pay.stan = from_iso.get_stan()
        iso_pay.ntb = from_iso.get_ntb()
        iso_pay.ntp = ntp
        iso_pay.bank_id = self.parent.conf['id']
        iso_pay.channel_id = from_iso.get_channel()
        iso_pay.bank_ip = self.parent.get_bank_ip()
        DBSession.add(iso_pay)
        DBSession.flush()
        self.parent.set_ntp(ntp)


def payment(parent):
    pay = PaymentResponse(parent)
    pay.response()


############
# Reversal #
############
class ReversalResponse(BaseResponse):
    def __init__(self, parent):
        BaseResponse.__init__(self, parent)
        self.rev = Reversal(
                self.models, self.iso_models, DBSession, self.invoice_id_raw)

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
