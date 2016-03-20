import sys
sys.path[0:0] = ['/usr/share/opensipkd/modules']
from base_models import (
    Base,
    BaseModel,
    )
from tools import create_now
from sqlalchemy import create_engine
from sqlalchemy import (
    Column,
    String,
    BigInteger,
    Integer,
    Float,
    DateTime,
    Date,
    ForeignKey,
    Sequence,
    )
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )
sys.path[0:0] = ['/etc/opensipkd']
from padl_fix_conf import other_db_url
 

TABLE_ARGS = {'autoload': True}

class Kecamatan(Base):
    __tablename__ = 'tblkecamatan'
    __table_args__ = TABLE_ARGS

class Kelurahan(Base):
    __tablename__ = 'tblkelurahan'
    __table_args__ = TABLE_ARGS

class Rekening(Base):
    __tablename__ = 'tblrekening'
    __table_args__ = TABLE_ARGS

class Pajak(Base):
    __tablename__ = 'pad_pajak'
    __table_args__ = TABLE_ARGS

class Usaha(Base):
    __tablename__ = 'pad_usaha'
    __table_args__ = TABLE_ARGS

class Customer(Base):
    __tablename__ = 'pad_customer'
    __table_args__ = TABLE_ARGS

class CustomerUsaha(Base):
    __tablename__ = 'pad_customer_usaha'
    __table_args__ = TABLE_ARGS

class Invoice(Base):
    __tablename__ = 'pad_spt'
    __table_args__ = TABLE_ARGS

class Payment(Base):
    __tablename__ = 'pad_sspd'
    __table_args__ = TABLE_ARGS

PAYMENT_SEQ = Sequence('pad_sspd_id_seq')

class Channel(Base, BaseModel):
    __tablename__ = 'pad_channel'
    nama = Column(String(20), nullable=False, unique=True)

class Bank(Base, BaseModel):
    __tablename__ = 'pad_tp' # Tempat Pembayaran
    singkatan = Column(String(16), nullable=False, unique=True)
    nama = Column(String(32), nullable=False, unique=True)

class IsoPayment(Base, BaseModel):
    __tablename__ = 'pad_payment'
    id = Column(Integer, primary_key=True) # references pad_sspd.id
    tgl = Column(DateTime(timezone=True),
                 nullable=False,
                 default=create_now)
    iso_request = Column(String(1024), nullable=False) # Untuk reversal
    transmission = Column(DateTime(timezone=True), nullable=False)
    settlement = Column(Date, nullable=False)
    stan = Column(Integer, nullable=False)
    invoice_id = Column(Integer, nullable=False) # references pad_spt.id
    ntb = Column(String(32), nullable=False)
    ntp = Column(String(32), nullable=False, unique=True)
    bank_id = Column(Integer, nullable=False) # references pad_tp.id
    channel_id = Column(Integer) # references pad_channel.id
    bank_ip = Column(String(15), nullable=False)

class IsoReversal(Base, BaseModel):
    __tablename__ = 'pad_reversal'
    id = Column(Integer, ForeignKey('pad_payment.id'), primary_key=True)
    tgl = Column(DateTime(timezone=True),
                 nullable=False,
                 default=create_now)
    iso_request = Column(String(1024), nullable=False)
