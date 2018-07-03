from datetime import datetime
from ISO8583.ISOErrors import BitNotSet
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import (
    ProgrammingError,
    OperationalError,
    )
from tools import round_up
from base_models import Base
from padl.transaction import Transaction
from padl.structure import (
    TRANSACTION_BITS,
    PAYMENT_CODE,
    )
from padl.models import Models
from .other_query import Query
from .conf import (
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
models = Models(Base)
session_factory = sessionmaker(bind=engine)

other_engine = create_engine(other_db_url)
other_session_factory = sessionmaker(bind=other_engine)

from .ReversalByQuery import ReversalByQuery


class DbTransaction(Transaction):
    def get_query(self):
        bank_id = str(self.from_iso.get_bank_id())
        q = Query(other_session_factory(), bank_id)
        q.log_info = self.log_info
        return q

    def get_invoice(self):
        try:
            q = self.get_query()
            inv = q.inquiry(self.from_iso.get_invoice_id())
        except ProgrammingError as msg:
            return self.ack_other(msg)
        except OperationalError as msg:
            return self.ack_other(msg)
        if 'Tagihan' in inv:
            return inv
        if 'hasil' in inv and inv.hasil == '0':
            return self.ack_not_available()
        self.ack_other('hasil query {} belum dipahami'.format(dict(inv)))

    # Override
    def set_invoice_profile(self, invoice):
        self.invoice_profile.from_dict({
            'NPWPD': invoice.NPWPD,
            'Nama': invoice.NamaWP,
            'Alamat 1': invoice.Alamat1,
            'Alamat 2': invoice.Alamat2,
            'Kode Rekening': invoice.KodeRekening.replace('.', ''),
            'Nama Rekening': invoice.Pajak,
            'Tagihan': round_up(invoice.Pokok),
            'Denda': round_up(invoice.Denda),
            'Total': round_up(invoice.Tagihan),
            'Masa 1': invoice.MasaAwal.strftime('%Y%m%d'),
            'Masa 2': invoice.MasaAkhir.strftime('%Y%m%d'),
            })
        Transaction.set_invoice_profile(self)

    def _inquiry_request_handler(self):
        if not self.is_allowed():
            return self.ack_not_allowed()
        invoice = self.get_invoice()
        if invoice:
            self.set_invoice_profile(invoice)
            self.set_amount(self.invoice_profile['Total'])
            if self.invoice_profile['Total'] > 0:
                return self.ack()
            return self.ack_already_paid()
        self.set_amount(0)

    # Override
    def inquiry_request_handler(self):
        try:
            self.save_request_log()
            self._inquiry_request_handler()
            self.save_response_log()
        except:
            self.ack_unknown()

    ###########
    # Payment #
    ###########
    def _payment_request_handler(self):
        if not self.is_allowed():
            return self.ack_not_allowed()
        invoice = self.get_invoice()
        if not invoice:
            return
        self.set_invoice_profile(invoice)
        if self.invoice_profile['Total'] != self.get_amount():
            return self.ack_insufficient_fund()
        q = self.get_query()
        try:
            pay = q.payment(self.from_iso.get_invoice_id())
        except ProgrammingError as msg:
            return self.ack_other(msg)
        except OperationalError as msg:
            return self.ack_other(msg)
        if pay.hasil == '0':
            return self.ack_already_paid_2()
        if pay.hasil == '2':
            return self.ack_other('Gagal membuat NTP')
        self.set_ntp(pay.hasil)
        self.ack()

    # Override
    def payment_request_handler(self):
        try:
            self.save_request_log()
            self._payment_request_handler()
            self.save_response_log()
        except:
            self.ack_unknown()

    ############
    # Reversal #
    ############
    def is_transaction_owner(self, bank_id):
        return bank_id == self.conf['id']

    def _reversal_request_handler(self):
        if not self.is_allowed():
            return self.ack_not_allowed()
        invoice_id = self.from_iso.get_invoice_id()
        rev = ReversalByQuery(invoice_id)
        rev.query.log_info = self.log_info
        if not rev.payment:
            return self.ack_payment_not_found()
        if not rev.is_paid():
            return self.ack_invoice_open()
        if not self.is_transaction_owner(int(rev.bank_id)):
            return self.ack_payment_owner()
        if self.from_iso.get_ntb() != rev.payment.bit048:
            return self.ack_ntb()
        result = rev.set_unpaid()
        if result.hasil == '1':
            return self.ack()
        if result.hasil == '2':
            return self.ack_payment_owner()
        if result.hasil == '0':
            s = 'Pembatalan gagal atau NTP {} tidak ditemukan'
            s = s.format(rev.payment.bit047)
        else:
            s = 'Nilai {} tidak dipahami'.format(result.hasil)
        self.ack_other(s)

    def reversal_request_handler(self):
        try:
            self.save_request_log()
            self._reversal_request_handler()
            self.save_response_log()
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
        self.DBSession.add(row)
        self.DBSession.flush()
        return row

    def save_request_log(self):
        self.DBSession = session_factory()
        self.request_log = self.save_log(self.from_iso)
        self.DBSession.commit()

    def save_response_log(self):
        self.response_log = self.save_log(self, self.request_log)
        self.DBSession.commit()

    ##########
    # Others #
    ##########
    def is_allowed(self):
        self.update_conf()
        bank_id = self.from_iso.get_bank_id()
        if 'id' in self.conf:
            return bank_id == self.conf['id']
        return bank_id in self.conf['ids']

    def update_conf(self):
        bank_name = self.conf['name']
        self.conf.update(host[bank_name])

    def ack_insufficient_fund(self):
        Transaction.ack_insufficient_fund(self, self.invoice_profile['Total'])

    def ack_already_paid(self):
        IsoLog = models.IsoLog
        invoice_id = self.from_iso.get_invoice_id()
        q = self.DBSession.query(IsoLog).filter_by(
                mti='0210', bit061=invoice_id, bit003=PAYMENT_CODE).\
                filter(IsoLog.bit047 != None).order_by(IsoLog.id.desc())
        pay = q.first()
        if pay:
            bank_id = int(pay.bit033)
            if self.is_transaction_owner(bank_id):
                self.set_ntp(pay.bit047)
                self.set_ntb(pay.bit048)
        Transaction.ack_already_paid(self)
