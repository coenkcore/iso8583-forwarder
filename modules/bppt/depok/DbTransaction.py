import re
from datetime import datetime
from ISO8583.ISOErrors import BitNotSet
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )
from base_models import (
    Base,
    DBSession,
    )
from bppt.transaction import Transaction
from bppt.structure import TRANSACTION_BITS
from query import (
    CalculateInvoice,
    Query,
    NTP,
    Reversal,
    )
from models import (
    OtherModels,
    Models,
    )
from conf import (
    db_url,
    other_db_url,
    db_pool_size,
    db_max_overflow,
    host,
    )


engine = create_engine(
            db_url, pool_size=db_pool_size,
            max_overflow=db_max_overflow)
Base.metadata.bind = engine
DBSession.configure(bind=engine)
models = Models(Base)
query = Query(models, DBSession) 

other_engine = create_engine(
                other_db_url, pool_size=db_pool_size,
                max_overflow=db_max_overflow)
OtherBase = declarative_base()
OtherBase.metadata.bind = other_engine
session_factory = sessionmaker()
OtherDBSession = scoped_session(session_factory)
OtherDBSession.configure(bind=other_engine)
other_models = OtherModels(OtherBase)


def create_no_ssrd():
    q = OtherDBSession.query(other_models.Payment).order_by(
            other_models.Payment.no_ssrd.desc())
    pay = q.first()
    last_seq = 0 
    if pay:
        s_last_seq = pay.no_ssrd[6:]
        if s_last_seq:
            last_seq = int(s_last_seq)
    new_seq = last_seq + 1
    kini = datetime.now()
    periode = kini.strftime('%Y%m')
    if pay and pay.no_ssrd[:6] == periode:
        last_seq = int(pay.no_ssrd[6:])
        new_seq = last_seq + 1
    else:
        new_seq = 1
    s_new_seq = str(new_seq).zfill(6)
    n = periode + s_new_seq
    return n, kini

def create_ntp():
    ntp = NTP(models, DBSession)
    return ntp.create()

def real_invoice_id_raw(raw):
    return '-'.join([raw[:4], raw[4:6], raw[6:]])

def flush(db_session, row):
    db_session.add(row)
    db_session.flush()


class DbTransaction(Transaction):
    def get_invoice(self):
        invoice_id_raw = self.from_iso.get_invoice_id()
        if len(invoice_id_raw) != 11:
            return self.ack_invalid_number()
        self.invoice_id_raw = real_invoice_id_raw(invoice_id_raw)
        self.calc = CalculateInvoice(
                        other_models, OtherDBSession, self.invoice_id_raw)
        if not self.calc.invoice:
            return self.ack_not_available()
        self.set_invoice_profile()
        if self.calc.paid:
            return self.ack_already_paid()
        return self.calc.invoice

    # Override
    def set_invoice_profile(self):
        invoice = self.calc.invoice
        izin = query.get_izin_by_name(invoice.nama_izin)
        self.invoice_profile.from_dict({
            'No Bayar': re.sub('\D', '', invoice.no_bayar),
            'Kode Izin': izin.id,
            'Nama Izin': invoice.nama_izin, 
            'Jenis Layanan': '-',
            'No Resi': '-',
            'Pemohon': invoice.nama_wp,
            'Lokasi': invoice.lokasi_izin,
            'Tagihan': self.calc.tagihan,
            'Denda': self.calc.denda,
            'Total': self.calc.total,
            'Pesan': '',
            })
        Transaction.set_invoice_profile(self, self.invoice_profile.get_raw())

    def _inquiry_request_handler(self):
        if self.get_invoice():
            self.set_amount(self.calc.total)
            self.ack()
        else:
            self.set_amount(0)

    # Override
    def inquiry_request_handler(self):
        try:
            self.save_request_log()
            self._inquiry_request_handler()
            self.save_response_log()
            DBSession.commit()
        except:
            self.ack_unknown()

    ###########
    # Payment #
    ###########
    def _payment_request_handler(self):
        inv = self.get_invoice()
        if not inv:
            return
        if self.calc.total != self.get_amount():
            return self.ack_insufficient_fund()
        no_ssrd, kini = create_no_ssrd()
        pay = other_models.Payment()
        pay.id_pendaftaran = inv.id_pendaftaran
        pay.no_bayar = inv.no_bayar
        pay.no_ssrd = no_ssrd
        pay.date_ssrd = kini
        pay.date_bayar = self.from_iso.get_transaction_datetime() 
        pay.jumlah_bayar = self.calc.total
        pay.cara_bayar = self.from_iso.get_channel_id()
        pay.ref_bayar = self.from_iso.get_ntb()
        OtherDBSession.add(pay)
        OtherDBSession.flush()
        self.save_iso_payment(pay)
        self.commit()

    # Override
    def payment_request_handler(self):
        try:
            self.save_request_log()
            self._payment_request_handler()
        except:
            self.ack_unknown()

    def save_iso_payment(self, pay):
        ntp = create_ntp()
        self.set_ntp(ntp)
        self.ack()
        self.save_response_log()
        self.update_conf()
        iso_pay = models.IsoPayment(id=self.request_log.id)
        iso_pay.response_id = self.response_log.id
        iso_pay.id_pendaftaran = pay.id_pendaftaran
        iso_pay.no_bayar = pay.no_bayar
        iso_pay.ntp = ntp
        iso_pay.ntb = self.get_ntb()
        iso_pay.tgl = self.from_iso.get_transaction_datetime()
        iso_pay.bank_id = self.conf['id']
        iso_pay.channel_id = self.get_channel_id()
        flush(DBSession, iso_pay)

    ############
    # Reversal #
    ############
    def is_transaction_owner(self, iso_pay):
        self.update_conf()
        return iso_pay.bank_id == self.conf['id']

    def _reversal_request_handler(self):
        invoice_id_raw = self.from_iso.get_invoice_id()
        if len(invoice_id_raw) != 11:
            return self.ack_invalid_number()
        self.invoice_id_raw = real_invoice_id_raw(invoice_id_raw)
        rev = Reversal(other_models, OtherDBSession, self.invoice_id_raw)
        if not rev.payment:
            return self.ack_payment_not_found()
        if not rev.paid:
            return self.parent.ack_invoice_open()
        iso_pay = query.get_iso_payment(rev.payment)
        if not iso_pay:
            return self.ack_iso_payment_not_found()
        if not self.is_transaction_owner(iso_pay):
            return self.ack_payment_owner()
        if iso_pay.ntb != self.get_ntb():
            return self.ack_ntb()
        self.ack()
        self.save_response_log()
        iso_rev = models.IsoReversal(id=iso_pay.id)
        iso_rev.request_id = self.request_log.id
        iso_rev.response_id = self.response_log.id
        rev.set_unpaid(iso_rev)
        flush(DBSession, iso_rev)
        self.commit()

    def reversal_request_handler(self):
        try:
            self.save_request_log()
            self._reversal_request_handler()
        except:
            self.ack_unknown()
            
    #######
    # Log #
    #######
    def save_log(self, iso, request_log=None):
        row = models.IsoLog()
        row.forwarder = self.conf['name']
        row.ip = self.get_bank_ip()
        row.mti = iso.getMTI()
        row.is_request = True
        row.raw = iso.getRawIso()
        if request_log:
            row.request_id = request_log.id
        d = dict()
        for bit in TRANSACTION_BITS:
            try:
                val = iso.get_value(bit)
            except BitNotSet:
                continue
            field = 'bit{b}'.format(b=str(bit).zfill(3))
            d[field] = val
        row.from_dict(d)
        flush(DBSession, row)
        return row

    def save_request_log(self):
        self.request_log = self.save_log(self.from_iso)

    def save_response_log(self):
        self.response_log = self.save_log(self, self.request_log)

    ##########
    # Others #
    ##########
    def commit(self):
        DBSession.commit()
        OtherDBSession.commit()

    def update_conf(self):
        bank_name = self.conf['name']
        self.conf.update(host[bank_name])
