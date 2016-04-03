import sys
sys.path.insert(0, '/usr/share/opensipkd/modules/multi')
sys.path.insert(0, '/etc/opensipkd')
from base_models import (
    #Base,
    BaseModel,
    )
from webr import (
    WebrBase,
    WebrDBSession
)

from multi_conf import webr_db_schema
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
              'schema': webr_db_schema}

# class Kecamatan(WebrBase):
    # __tablename__ = 'tblkecamatan'
    # #__tablename__ = 'pad_kecamatan'
    # __table_args__ = TABLE_ARGS

# class Kelurahan(WebrBase):
    # __tablename__ = 'tblkelurahan'
    # #__tablename__ = 'pad_kelurahan'
    # __table_args__ = TABLE_ARGS

# class Rekening(WebrBase):
    # __tablename__ = 'tblrekening'
    # #__tablename__ = 'pad_rekening'
    # __table_args__ = TABLE_ARGS

# class Pajak(WebrBase):
    # __tablename__ = 'pad_pajak'
    # #__tablename__ = 'pad_jenis_pajak'
    # __table_args__ = TABLE_ARGS

# class Usaha(WebrBase):
    # __tablename__ = 'pad_usaha'
    # __table_args__ = TABLE_ARGS

# class Customer(WebrBase):
    # __tablename__ = 'pad_customer'
    # __table_args__ = TABLE_ARGS

# class CustomerUsaha(WebrBase):
    # __tablename__ = 'pad_customer_usaha'
    # __table_args__ = TABLE_ARGS
# class Unit(WebrBase):
    # __tablename__ = 'units'
    # __table_args__ = TABLE_ARGS

class Invoice(WebrBase):
    __tablename__ = 'arinvoices'
    __table_args__ = TABLE_ARGS

class Pembayaran(WebrBase):
    __tablename__ = 'arsspds'
    __table_args__ = TABLE_ARGS

