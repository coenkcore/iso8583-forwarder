from base_models import CommonModel
from tools import create_now
from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    DateTime,
    Date,
    ForeignKey,
    UniqueConstraint
    )


class Models(object):
    def __init__(self, Base, transaction_schema, area_schema):
        class Kecamatan(Base):
            __tablename__ = 'ref_kecamatan'
            __table_args__ = dict(autoload=True, schema=area_schema) 
        self.Kecamatan = Kecamatan

        class Kelurahan(Base):
            __tablename__ = 'ref_kelurahan'
            __table_args__ = dict(autoload=True, schema=area_schema) 
        self.Kelurahan = Kelurahan

        class Customer(Base):
            __tablename__ = 'bphtb_ppat'
            __table_args__ = dict(autoload=True, schema=transaction_schema)
        self.Customer = Customer

        class Invoice(Base):
            __tablename__ = 'bphtb_sspd'
            __table_args__ = dict(autoload=True, schema=transaction_schema)
        self.Invoice = Invoice

        class Payment(Base):
            __tablename__ = 'bphtb_bank'
            __table_args__ = dict(autoload=True, schema=transaction_schema)
        self.Payment = Payment

        class IsoPayment(Base, CommonModel):
            __tablename__ = 'bphtb_payment'
            __table_args__ = dict(schema=transaction_schema)
            id = Column(Integer, ForeignKey('bphtb.bphtb_bank.id'), primary_key=True)
            tgl = Column(DateTime(timezone=True),
                         nullable=False,
                         default=create_now)
            iso_request = Column(String(1024), nullable=False) # Untuk reversal
            transmission = Column(DateTime(timezone=True), nullable=False)
            settlement = Column(Date, nullable=False)
            stan = Column(Integer, nullable=False)
            invoice_id = Column(Integer,
                                ForeignKey('bphtb.bphtb_sspd.id'),
                                nullable=False)
            invoice_no = Column(String(32),nullable=False)
            ntb = Column(String(32), nullable=False)
            ntp = Column(String(32), nullable=False, unique=True)
            bank_id = Column(Integer) # sesuai ATM bersama
            channel_id = Column(Integer) # bit 18
            bank_ip = Column(String(15), nullable=False)
            UniqueConstraint('invoiceno', 'ntb', name='payment_uq')
        self.IsoPayment = IsoPayment

        class IsoReversal(Base, CommonModel):
            __tablename__ = 'bphtb_reversal'
            __table_args__ = dict(schema=transaction_schema)
            id = Column(Integer, ForeignKey('bphtb_payment.id'), primary_key=True)
            tgl = Column(DateTime(timezone=True),
                         nullable=False,
                         default=create_now)
            iso_request = Column(String(1024), nullable=False)
        self.IsoReversal = IsoReversal
