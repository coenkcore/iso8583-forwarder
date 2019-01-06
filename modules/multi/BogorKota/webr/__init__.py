import sys
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
)
from tools import FixLength
from multi.webr.structure import INVOICE_PROFILE
from .models import Models
from .query import (
    Query,
    CalculateInvoice,
    NTP,
    Reversal,
)
from .conf import (
    db_url,
    db_schema,
    db_pool_size,
    db_max_overflow,
    host,
    persen_denda,
    pesan1,
    pesan2,
)

engine = create_engine(db_url, pool_size=db_pool_size,
                       max_overflow=db_max_overflow)
Base = declarative_base()
Base.metadata.bind = engine
session_factory = sessionmaker()
DBSession = scoped_session(session_factory)
DBSession.configure(bind=engine)
models = Models(Base, db_schema)
query = Query(models, DBSession)

DEBUG = '--debug' in sys.argv


def print_debug(label, s):
    if DEBUG:
        print('*** DEBUG {l}: {s}'.format(l=label, s=s))


class BaseResponse(object):
    def __init__(self, parent):
        self.parent = parent
        self.invoice_id_raw = parent.from_iso.get_invoice_id()

    def is_transaction_owner(self, iso_pay):
        conf = host[self.parent.conf['name']]
        return iso_pay.bank_id == conf['id']

    def commit(self):
        DBSession.commit()
        self.parent.ack()


class InquiryResponse(BaseResponse):
    def __init__(self, parent):
        BaseResponse.__init__(self, parent)
        self.parent = parent
        self.calc = CalculateInvoice(
            models, DBSession, parent.from_iso.get_invoice_id(),
            persen_denda)
        module_conf = host[self.parent.conf['name']]
        self.parent.conf.update(module_conf)

    def init_invoice_profile(self):
        self.invoice_profile = FixLength(INVOICE_PROFILE)

    def set_invoice_profile(self):
        invoice = self.calc.invoice
        self.invoice_profile.from_dict({
            'Kode': invoice.kode,
            'Nama Penyetor': invoice.objek_nama,
            'Alamat 1': invoice.objek_alamat_1,
            'Alamat 2': invoice.objek_alamat_2,
            'Tagihan': self.calc.tagihan,
            'Denda': self.calc.denda,
            'Total': self.calc.total,
            'Kode Rekening': invoice.rekening_kode,
            'Nama Rekening': invoice.rekening_nama,
            'Kode SKPD': invoice.departemen_kode,
            'Nama SKPD': invoice.departemen_nama,
            'Additional 1': pesan1,
            'Additional 2': pesan2, })
        self.set_invoice_profile_to_parent()
        print_debug('Invoice Profile', self.invoice_profile.to_dict())

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
        self.init_invoice_profile()
        if not self.is_valid():
            return self.parent.set_amount(0)
        self.parent.set_amount(self.calc.total)
        self.parent.ack()

    def set_invoice_profile_(self, key, value):
        if value:
            self.invoice_profile.from_dict({key: value})

    def set_invoice_profile_to_parent(self):
        self.parent.set_invoice_profile(self.invoice_profile.get_raw())

    def ack_already_paid(self):
        pay = self.calc.get_payment()
        if pay and pay.bank_id == self.parent.conf['id']:
            ntp = pay.kode
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
def create_ntp(tgl):
    ntp = NTP(models, DBSession)
    return ntp.create(tgl)


def get_no_urut(tahun, departemen_id):
    q = DBSession.query(models.Payment).filter_by(
        tahun=tahun, departemen_id=departemen_id)
    q = q.order_by(models.Payment.no_urut.desc())
    row = q.first()
    if row:
        return row.no_urut + 1
    return 1


def get_pembayaran_ke(invoice_id):
    q = DBSession.query(models.Payment).filter_by(ar_invoice_id=invoice_id)
    q = q.order_by(models.Payment.pembayaran_ke.desc())
    row = q.first()
    if row:
        return row.pembayaran_ke + 1
    return 1


class PaymentResponse(InquiryResponse):
    def response(self):
        self.init_invoice_profile()
        if not self.is_valid():
            return
        self.create_payment()
        self.commit()

    # Override
    def is_valid(self):
        if not InquiryResponse.is_valid(self):
            return
        if self.calc.total != self.parent.from_iso.get_amount():
            return self.parent.ack_insufficient_fund(self.calc.total)
        return True

    def create_payment(self):
        inv = self.calc.invoice
        tgl_bayar = self.parent.from_iso.get_transaction_datetime()
        ntp = create_ntp(tgl_bayar.date())
        no_urut = get_no_urut(inv.tahun, inv.departemen_id)
        pembayaran_ke = get_pembayaran_ke(inv.id)
        pay = models.Payment()
        pay.kode = ntp
        pay.status = 1
        pay.created = pay.updated = pay.create_date = pay.update_date = \
            datetime.now()
        pay.bunga = self.calc.denda
        pay.tahun = inv.tahun
        pay.departemen_id = inv.departemen_id
        pay.no_urut = no_urut
        pay.ar_invoice_id = inv.id
        pay.pembayaran_ke = pembayaran_ke
        pay.bayar = self.calc.total
        pay.tgl_bayar = tgl_bayar
        pay.jatuh_tempo = inv.jatuh_tempo
        pay.ntb = self.parent.from_iso.get_ntb()
        pay.ntp = ntp
        pay.bank_id = self.parent.conf['id']
        pay.channel_id = self.parent.from_iso.get_channel()
        DBSession.add(pay)
        self.calc.set_paid()
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
        self.rev = Reversal(models, DBSession, self.invoice_id_raw)

    def response(self):
        if not self.rev.invoice:
            return self.parent.ack_payment_not_found()
        if not self.rev.is_paid():
            return self.parent.ack_invoice_open()
        if not self.rev.payment:
            return self.parent.ack_payment_not_found()
        if not self.is_transaction_owner(self.rev.payment):
            return self.parent.ack_payment_owner()
        self.rev.set_unpaid()
        self.commit()


def reversal(parent):
    rev = ReversalResponse(parent)
    rev.response()
