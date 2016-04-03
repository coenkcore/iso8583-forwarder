import sys
sys.path.insert(0, '/usr/share/opensipkd/modules/bca')
from base_models import (
    #Base,
    BaseModel,
    )
from padl import (
    PadlBase,
    #PadlDBSession
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
    )


TABLE_ARGS = {'autoload': True,
              'schema': 'pad'}

class Kecamatan(PadlBase):
    __tablename__ = 'tblkecamatan'
    #__tablename__ = 'pad_kecamatan'
    __table_args__ = TABLE_ARGS

class Kelurahan(PadlBase):
    __tablename__ = 'tblkelurahan'
    #__tablename__ = 'pad_kelurahan'
    __table_args__ = TABLE_ARGS

class Rekening(PadlBase):
    __tablename__ = 'tblrekening'
    #__tablename__ = 'pad_rekening'
    __table_args__ = TABLE_ARGS

class Pajak(PadlBase):
    __tablename__ = 'pad_pajak'
    #__tablename__ = 'pad_jenis_pajak'
    __table_args__ = TABLE_ARGS

class Usaha(PadlBase):
    __tablename__ = 'pad_usaha'
    __table_args__ = TABLE_ARGS

class Customer(PadlBase):
    __tablename__ = 'pad_customer'
    __table_args__ = TABLE_ARGS

class CustomerUsaha(PadlBase):
    __tablename__ = 'pad_customer_usaha'
    __table_args__ = TABLE_ARGS

class Invoice(PadlBase):
    __tablename__ = 'pad_spt'
    __table_args__ = TABLE_ARGS

class Pembayaran(PadlBase):
    __tablename__ = 'pad_sspd'
    __table_args__ = TABLE_ARGS

