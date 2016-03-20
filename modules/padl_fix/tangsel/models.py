import sys
sys.path[0:0] = ['/usr/share/opensipkd/modules']
from base_models import (
    Base,
    BaseModel,
    )
from tools import create_now
from sqlalchemy import (
    create_engine,
    Sequence,
    )
from sqlalchemy import (
    Column,
    String,
    BigInteger,
    Integer,
    Float,
    DateTime,
    Date,
    ForeignKey,
    )
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )
sys.path[0:0] = ['/etc/opensipkd']
from padl_fix_conf import (
    db_pool_size,
    db_max_overflow,
    )
 

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

PaymentSequence = Sequence('pad_sspd_id_seq')

class Payment(Base):
    __tablename__ = 'pad_sspd'
    __table_args__ = TABLE_ARGS

class Channel(Base, BaseModel):
    __tablename__ = 'pad_channel'
    nama = Column(String(20), nullable=False, unique=True)

class Bank(Base, BaseModel):
    __tablename__ = 'pad_tp' # Tempat Pembayaran
    singkatan = Column(String(16), nullable=False, unique=True)
    nama = Column(String(32), nullable=False, unique=True)

class IsoPayment(Base, BaseModel):
    __tablename__ = 'pad_payment'
    id = Column(BigInteger, primary_key=True)
    sspd_id = Column(BigInteger, nullable=False)
    tgl = Column(DateTime(timezone=True),
                 nullable=False,
                 default=create_now)
    iso_request = Column(String(1024), nullable=False) # Untuk reversal
    transmission = Column(DateTime(timezone=True), nullable=False)
    settlement = Column(Date, nullable=False)
    stan = Column(Integer, nullable=False)
    invoice_no = Column(String(32), nullable=False)
    ntb = Column(String(32), nullable=False)
    ntp = Column(String(32), nullable=False, unique=True)
    bank_id = Column(Integer, ForeignKey('pad_tp.id'), nullable=False)
    channel_id = Column(Integer, ForeignKey('pad_channel.id'), nullable=False)
    bank_ip = Column(String(15), nullable=False)

class IsoReversal(Base, BaseModel):
    __tablename__ = 'pad_reversal'
    id = Column(Integer, ForeignKey('pad_payment.id'), primary_key=True)
    tgl = Column(DateTime(timezone=True),
                 nullable=False,
                 default=create_now)
    iso_request = Column(String(1024), nullable=False)
