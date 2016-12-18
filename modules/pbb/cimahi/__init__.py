from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )
from tools import FixLength
from sismiop.query import CalculateInvoice 
from common.pbb.models import Models
from common.pbb.query import (
    Payment,
    Reversal,
    )
from common.pbb.structure import (
    INVOICE_ID,
    INVOICE_PROFILE,
    )
from conf import (
    db_url,
    db_schema,
    db_pool_size,
    db_max_overflow,
    persen_denda,
    nip_rekam_byr_sppt,
    host,
    )


engine = create_engine(db_url, pool_size=db_pool_size,
                       max_overflow=db_max_overflow)
Base = declarative_base()
Base.metadata.bind = engine
session_factory = sessionmaker()
DBSession = scoped_session(session_factory)
DBSession.configure(bind=engine)
models = Models(Base, db_schema, None)
query = Payment(models, DBSession)


BANK_FIELDS = ('kd_kanwil', 'kd_kantor', 'kd_tp')
PREFIX_NTP_FIELDS = BANK_FIELDS[:-1]


class BaseResponse(object):
    def __init__(self, parent):
        self.parent = parent
        self.invoice_id = FixLength(INVOICE_ID)
        self.invoice_id_raw = parent.from_iso.get_invoice_id()
        self.invoice_id.set_raw(self.invoice_id_raw)

    def is_transaction_owner(self, pay):
        conf = host[self.parent.conf['name']]
        return pay.kd_kanwil == conf['kd_kanwil'] and \
            pay.kd_kantor == conf['kd_kantor'] and \
            pay.kd_tp == conf['kd_tp']

    def commit(self):
        DBSession.commit()
        self.parent.ack()


class InquiryResponse(BaseResponse):
    def __init__(self, parent):
        BaseResponse.__init__(self, parent)
        self.invoice_profile = FixLength(INVOICE_PROFILE)
        self.invoice_profile.from_dict({
            'Propinsi': self.invoice_id['Propinsi'],
            'Kabupaten': self.invoice_id['Kabupaten'],
            'Kecamatan': self.invoice_id['Kecamatan'],
            'Kelurahan': self.invoice_id['Kelurahan'],
            'Blok': self.invoice_id['Blok'],
            'Urut': self.invoice_id['Urut'],
            'Jenis': self.invoice_id['Jenis'],
            'Tahun Pajak': self.invoice_id['Tahun Pajak'],
            'Nama Kelurahan': nama_kelurahan(self.invoice_id),
            'Nama Kecamatan': nama_kecamatan(self.invoice_id),
            'Nama Propinsi': nama_propinsi(self.invoice_id)})
        try:
            int(self.invoice_id_raw)
        except ValueError:
            self.calc = None
            return
        self.calc = CalculateInvoice(models, DBSession, persen_denda,
            self.invoice_id['Propinsi'], self.invoice_id['Kabupaten'],
            self.invoice_id['Kecamatan'], self.invoice_id['Kelurahan'],
            self.invoice_id['Blok'], self.invoice_id['Urut'],
            self.invoice_id['Jenis'], self.invoice_id['Tahun Pajak'])

    def set_invoice_profile(self):
        inv = self.calc.invoice
        self.parent.set_amount(self.calc.total)
        self.invoice_profile.from_dict({
            'Nama': inv.nm_wp_sppt,
            'Luas Tanah': int(inv.luas_bumi_sppt),
            'Luas Bangunan': int(inv.luas_bng_sppt),
            'Lokasi': inv.jln_wp_sppt,
            'Jatuh Tempo': inv.tgl_jatuh_tempo_sppt.strftime('%Y%m%d'),
            'Tagihan': self.calc.tagihan,
            'Denda': self.calc.denda,
            'Total Bayar': self.calc.total})
        self.set_invoice_profile_to_parent()

    def set_invoice_profile_to_parent(self):
        self.parent.set_invoice_profile(self.invoice_profile.get_raw())

    def is_valid(self, is_need_invoice_profile=True):
        if not self.calc:
            return self.parent.ack_invalid_number()
        if not self.calc.invoice:
            is_need_invoice_profile and self.set_invoice_profile_to_parent()
            return self.parent.ack_not_available()
        is_need_invoice_profile and self.set_invoice_profile()
        if self.calc.paid:
            return self.ack_already_paid()
        if self.calc.total <= 0:
            return self.parent.ack_already_paid_2(self.calc.total)
        return True

    def ack_already_paid(self):
        pay = self.calc.invoice2payment()
        if pay and self.is_transaction_owner(pay):
            ntp = pay.id
        else:
            ntp = ''
        self.parent.set_ntp(ntp)
        return self.parent.ack_already_paid()

    def response(self):
        if not self.is_valid():
            return self.parent.set_amount(0)
        self.parent.set_amount(self.calc.total)
        query.create_inquiry(self.calc, self.parent.from_iso, persen_denda)
        self.commit()


def inquiry(parent):
    handler = InquiryResponse(parent)
    handler.response()


class PaymentResponse(InquiryResponse):
    def response(self):
        inv = self.calc.invoice
        if not inv:
            return self.parent.ack_not_available()
        if self.calc.total != self.parent.from_iso.get_amount():
            return self.parent.ack_insufficient_fund(self.calc.total)
        module_conf = host[self.parent.conf['name']]
        self.parent.conf.update(module_conf)
        if self.calc.paid:
            return self.ack_already_paid()
        if self.calc.total <= 0:
            return self.parent.ack_already_paid_2(self.calc.total)
        inq = query.invoice2inquiry(self.calc.invoice)
        if not inq:
            return self.parent.ack_inquiry_not_found()
        self.create_payment(inq)
        self.commit()

    def create_payment(self, inq):
        pay, urutan = self.sismiop_create_payment(inq)
        d = pay.to_dict()
        prefix_ntp = '' 
        for fieldname in PREFIX_NTP_FIELDS: 
            prefix_ntp += d[fieldname] or '00'
        ntp = query.create_ntp(prefix_ntp)
        iso_pay = models.Payment(id=ntp)
        iso_pay.inquiry_id = inq.id
        iso_pay.propinsi = inq.propinsi
        iso_pay.kabupaten = inq.kabupaten
        iso_pay.kecamatan = inq.kecamatan
        iso_pay.kelurahan = inq.kelurahan
        iso_pay.blok = inq.blok
        iso_pay.urut = inq.urut
        iso_pay.jenis = inq.jenis
        iso_pay.tahun = inq.tahun
        iso_pay.ke = urutan
        iso_pay.kd_kanwil_bank = pay.kd_kanwil
        iso_pay.kd_kppbb_bank = pay.kd_kantor
        iso_pay.kd_bank_tunggal = '00'
        iso_pay.kd_bank_persepsi = '00'
        iso_pay.kd_tp = pay.kd_tp
        iso_pay.channel = self.parent.from_iso.get_channel()
        iso_pay.ntb = self.parent.from_iso.get_ntb()
        iso_pay.iso_request = self.parent.from_iso.raw
        DBSession.add(iso_pay)
        DBSession.flush()
        self.parent.set_ntp(ntp)

    def sismiop_create_payment(self, inq):
        bank_fields = dict()
        for key in BANK_FIELDS:
            value = self.parent.get_bank_code(key)
            bank_fields[key] = value
        return self.calc.create_payment(self.calc.denda,
                self.parent.from_iso.get_transaction_date(), bank_fields,
                nip_rekam_byr_sppt)


def payment(parent):
    handler = PaymentResponse(parent)
    handler.response()


class ReversalResponse(BaseResponse):
    def __init__(self, parent):
        BaseResponse.__init__(self, parent)
        self.rev = Reversal(models, DBSession, self.invoice_id['Propinsi'],
            self.invoice_id['Kabupaten'], self.invoice_id['Kecamatan'],
            self.invoice_id['Kelurahan'], self.invoice_id['Blok'],
            self.invoice_id['Urut'], self.invoice_id['Jenis'],
            self.invoice_id['Tahun Pajak'])

    def response(self): #FIXME
        if not self.rev.invoice:
            return self.parent.ack_payment_not_found()
        if not self.rev.is_paid():
            return self.parent.ack_invoice_open()
        if not self.rev.payment:
            return self.parent.ack_payment_not_found()
        if not self.is_transaction_owner():
            return self.parent.ack_payment_owner()
        iso_pay = self.rev.get_iso_payment(self.invoice_id)
        if not iso_pay:
            return self.parent.ack_payment_not_found_2()
        self.rev.set_unpaid()
        self.commit()

    def is_transaction_owner(self):
        return BaseResponse.is_transaction_owner(self, self.rev.payment)


def reversal(parent):
    rev = ReversalResponse(parent)
    rev.response()

def nama_kelurahan(invoice_id):
    return query.cari_kelurahan(invoice_id['Propinsi'], invoice_id['Kabupaten'],
            invoice_id['Kecamatan'], invoice_id['Kelurahan'])

def nama_kecamatan(invoice_id):
    return query.cari_kecamatan(invoice_id['Propinsi'], invoice_id['Kabupaten'],
            invoice_id['Kecamatan'])

def nama_propinsi(invoice_id):
    return query.cari_propinsi(invoice_id['Propinsi'])
