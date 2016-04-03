import sys
sys.path[0:0] = ['/usr/share/opensipkd/modules']
from base_models import (
    BaseModel,
    )
sys.path[0:0] = ['/usr/share/opensipkd-forwarder/modules/bca']
from bphtb import (
    BphtbBase,
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
TABLE_ARGS2 = dict(autoload=True, schema='public')

class Kecamatan(BphtbBase):
    __tablename__ = 'ref_kecamatan'
    __table_args__ = TABLE_ARGS2

class Kelurahan(BphtbBase):
    __tablename__ = 'ref_kelurahan'
    __table_args__ = TABLE_ARGS2

class Customer(BphtbBase):
    __tablename__ = 'bphtb_ppat'
    __table_args__ = TABLE_ARGS

class Invoice(BphtbBase):
    __tablename__ = 'bphtb_sspd'
    __table_args__ = TABLE_ARGS

class Pembayaran(BphtbBase):
    __tablename__ = 'bphtb_bank'
    __table_args__ = TABLE_ARGS