import sys
from sqlalchemy import (
    Column,
    String,
    Integer,
    BigInteger,
    Float,
    DateTime,
    Date,
    ForeignKey,
    UniqueConstraint,
    create_engine,
    )
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )
sys.path[0:0] = ['/usr/share/opensipkd/modules']
from base_models import (
    Base,
    BaseModel,
    )
from tools import create_now
sys.path[0:0] = ['/etc/opensipkd']
from bphtb_fix_conf import (
    other_db_url,
    db_pool_size,
    db_max_overflow,
    )


OtherBase = declarative_base()
other_session_factory = sessionmaker()
OtherDBSession = scoped_session(other_session_factory)
other_engine = create_engine(other_db_url, pool_size=db_pool_size,
                 max_overflow=db_max_overflow)
OtherBase.metadata.bind = other_engine
OtherDBSession.configure(bind=other_engine)


TABLE_ARGS  = {'autoload': True}

class Invoice(OtherBase):
    __tablename__ = 'tbl_data_transaksi'
    __table_args__ = TABLE_ARGS

class Kecamatan(OtherBase):
    __tablename__ = 'mkecamatan'
    __table_args__ = TABLE_ARGS

class Kelurahan(OtherBase):
    __tablename__ = 'mkelurahan'
    __table_args__ = TABLE_ARGS

class Payment(OtherBase):
    __tablename__ = 'pembayaran_bphtb'
    __table_args__ = TABLE_ARGS

class Customer(OtherBase):
    __tablename__ = 'tbl_user'
    __table_args__ = TABLE_ARGS

class Pembeli(OtherBase):
    __tablename__ = 'tbl_pembeli'
    __table_args__ = TABLE_ARGS

class IsoPayment(Base, BaseModel):
    __tablename__ = 'bphtb_payment'
    id = Column(Integer, primary_key=True)
    tgl = Column(DateTime(timezone=True),
                 nullable=False,
                 default=create_now)
    iso_request = Column(String(1024), nullable=False) # Untuk reversal
    transmission = Column(DateTime(timezone=True), nullable=False)
    settlement = Column(Date, nullable=False)
    stan = Column(Integer, nullable=False)
    invoice_no = Column(String(32),nullable=False)
    pembayaran_ke = Column(Integer, nullable=False)
    ntb = Column(String(32), nullable=False)
    ntp = Column(String(32), nullable=False, unique=True)
    #bank_id = Column(String(11)) #, ForeignKey('bphtb_tp.id'), nullable=False)
    bank_id = Column(Integer, nullable=False) 
    #channel_id = Column(String(4)) #, #ForeignKey('bphtb_channel.id'), nullable=False)
    channel_id = Column(Integer, nullable=False) 
    bank_ip = Column(String(15), nullable=False)
    UniqueConstraint('invoiceno', 'ntb', name='payment_uq')

class IsoReversal(Base, BaseModel):
    __tablename__ = 'bphtb_reversal'
    id = Column(Integer, ForeignKey('bphtb_payment.id'), primary_key=True)
    tgl = Column(DateTime(timezone=True),
                 nullable=False,
                 default=create_now)
    iso_request = Column(String(1024), nullable=False)
