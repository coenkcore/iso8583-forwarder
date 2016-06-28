from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )
from tools import FixLength
from sismiop.query import CalculateInvoice 
from common.pbb.models import Models
from common.pbb.query import Query
from common.pbb.structure import (
    INVOICE_ID,
    INVOICE_PROFILE,
    )
from conf import (
    db_url,
    db_schema,
    iso_db_schema,
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
models = Models(Base, db_schema, iso_db_schema)
query = Query(models, DBSession)


BANK_FIELDS = ('kd_kanwil', 'kd_kantor', 'kd_tp')
PREFIX_NTP_FIELDS = BANK_FIELDS[:-1]


class Inquiry(object):
    def __init__(self, parent):
        self.parent = parent
        self.invoice_id = invoice_id = FixLength(INVOICE_ID)
        self.invoice_profile = FixLength(INVOICE_PROFILE)
        self.invoice_id.set_raw(parent.from_iso.get_invoice_id())
        self.invoice_profile.from_dict({
            'Propinsi': invoice_id['Propinsi'],
            'Kabupaten': invoice_id['Kabupaten'],
            'Kecamatan': invoice_id['Kecamatan'],
            'Kelurahan': invoice_id['Kelurahan'],
            'Blok': invoice_id['Blok'],
            'Urut': invoice_id['Urut'],
            'Jenis': invoice_id['Jenis'],
            'Tahun Pajak': invoice_id['Tahun Pajak'],
            'Nama Kelurahan': nama_kelurahan(invoice_id),
            'Nama Kecamatan': nama_kecamatan(invoice_id),
            'Nama Propinsi': nama_propinsi(invoice_id)})
        self.calc = CalculateInvoice(models, DBSession, persen_denda,
            invoice_id['Propinsi'], invoice_id['Kabupaten'],
            invoice_id['Kecamatan'], invoice_id['Kelurahan'],
            invoice_id['Blok'], invoice_id['Urut'], invoice_id['Jenis'],
            invoice_id['Tahun Pajak'])

    def set_invoice_profile(self):
        inv = self.calc.invoice
        self.parent.set_amount(self.calc.total)
        self.invoice_profile.from_dict({
            'Nama': inv.nm_wp_sppt,
            'Luas Tanah': int(inv.luas_bumi_sppt),
            'Luas Bangunan': int(inv.luas_bng_sppt),
            'Lokasi': inv.jln_wp_sppt})
        self.set_invoice_profile_to_parent()

    def set_invoice_profile_to_parent(self):
        self.parent.set_invoice_profile(self.invoice_profile.get_raw())

    def is_valid(self, is_need_invoice_profile=True):
        if not self.calc.invoice:
            is_need_invoice_profile and self.set_invoice_profile_to_parent()
            return self.parent.ack_not_available()
        is_need_invoice_profile and self.set_invoice_profile()
        if self.calc.paid:
            return self.ack_already_paid()
        if self.calc.total <= 0:
            return self.parent.ack_already_paid_2()
        return True

    def ack_already_paid(self):
        module_conf = host[self.parent.conf['name']]
        self.parent.conf.update(module_conf)
        pay = self.calc.invoice2payment()
        if pay and pay.kd_kanwil_bank == self.parent.conf['kd_kanwil'] and \
            pay.kd_kppbb_bank == self.parent.conf['kd_kantor'] and \
            pay.kd_tp == self.parent.conf['kd_tp']:
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

    def commit(self):
        DBSession.commit()
        self.parent.ack()


class Payment(Inquiry):
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
            return self.parent.ack_already_paid_2()
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
        return self.calc.create_payment(inq,
                self.parent.from_iso.get_transaction_date(), bank_fields,
                nip_rekam_byr_sppt)


def inquiry(parent):
    inq = Inquiry(parent)
    inq.response()

def payment(parent):
    pay = Payment(parent)
    pay.response()

def nama_kelurahan(invoice_id):
    return query.cari_kelurahan(invoice_id['Propinsi'], invoice_id['Kabupaten'],
            invoice_id['Kecamatan'], invoice_id['Kelurahan'])

def nama_kecamatan(invoice_id):
    return query.cari_kecamatan(invoice_id['Propinsi'], invoice_id['Kabupaten'],
            invoice_id['Kecamatan'])

def nama_propinsi(invoice_id):
    return query.cari_propinsi(invoice_id['Propinsi'])
