from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ISO8583.ISO8583 import ISO8583
from ISO8583.ISOErrors import BitNotSet
from tools import TransactionID
from common.bphtb.structure import (
    TRANSACTION_BITS,
    PAYMENT_CODE,
    )
from config import db_url
from .models import Iso


engine = create_engine(db_url)
session_factory = sessionmaker(bind=engine)


class NTP(TransactionID):
    def __init__(self, DBSession):
        self.DBSession = DBSession

    # Override
    def is_found(self, ntp):
        q = self.DBSession.query(Iso).filter_by(bit_057=ntp)
        return q.first()


class Query:
    def __init__(self):
        self.DBSession = session_factory() 


class Log(Query):
    def __init__(self, forwarder, bank_ip):
        Query.__init__(self)
        self.forwarder = forwarder
        self.bank_ip = bank_ip

    def save(self, iso, is_send, request_log=None, payment_id=None):
        row = Iso()
        row.forwarder = self.forwarder 
        row.ip = self.bank_ip
        row.mti = iso.getMTI()
        row.raw = ISO8583.getRawIso(iso)
        row.is_send = is_send
        if request_log:
            row.request_id = request_log.id
        row.payment_id = payment_id
        d = dict()
        for bit in TRANSACTION_BITS:
            try:
                val = iso.get_value(bit)
            except BitNotSet:
                continue
            field = 'bit_{}'.format(str(bit).zfill(3))
            d[field] = val
        row.from_dict(d)
        self.DBSession.add(row)
        self.DBSession.flush()
        self.DBSession.commit()
        return row

    def save_request(self, iso):
        self.request_log = self.save(iso, False)

    def save_response(self, iso, payment_id=None):
        self.response_log = self.save(iso, True, self.request_log, payment_id)

    def save_payment_response(self, iso, payment_id):
        ntp_generator = NTP(self.DBSession)
        ntp = ntp_generator.create()
        iso.set_ntp(ntp)
        self.save_response(iso, payment_id)


class Reversal(Query):
    def __init__(self, invoice_id, amount, ntb):
        Query.__init__(self)
        s_amount = str(amount).zfill(12)
        q = self.DBSession.query(Iso).filter_by(
                mti='0210', bit_003=PAYMENT_CODE, bit_004=s_amount,
                bit_058=ntb, bit_062=invoice_id)
        q = q.order_by(Iso.id.desc())
        self.payment = q.first()
