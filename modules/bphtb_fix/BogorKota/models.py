import sys
sys.path[0:0] = ['/usr/share/opensipkd/modules']
from base_models import (
    Base,
    BaseModel,
    )
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


TABLE_ARGS  = dict(autoload=True, schema='bphtb')
TABLE_ARGS2 = dict(autoload=True)


class Kecamatan(Base):
    __tablename__ = 'ref_kecamatan'
    __table_args__ = TABLE_ARGS2

class Kelurahan(Base):
    __tablename__ = 'ref_kelurahan'
    __table_args__ = TABLE_ARGS2

class Customer(Base):
    __tablename__ = 'bphtb_ppat'
    __table_args__ = TABLE_ARGS

class Invoice(Base):
    __tablename__ = 'bphtb_sspd'
    __table_args__ = TABLE_ARGS

class Payment(Base):
    __tablename__ = 'bphtb_bank'
    __table_args__ = TABLE_ARGS

class IsoPayment(Base, BaseModel):
    __tablename__ = 'bphtb_payment'
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
    bank_id = Column(Integer) #, ForeignKey('bphtb_tp.id'), nullable=False)
    channel_id = Column(Integer) #, #ForeignKey('bphtb_channel.id'), nullable=False)
    bank_ip = Column(String(15), nullable=False)
    UniqueConstraint('invoiceno', 'ntb', name='payment_uq')

class IsoReversal(Base, BaseModel):
    __tablename__ = 'bphtb_reversal'
    id = Column(Integer, ForeignKey('bphtb_payment.id'), primary_key=True)
    tgl = Column(DateTime(timezone=True),
                 nullable=False,
                 default=create_now)
    iso_request = Column(String(1024), nullable=False)
