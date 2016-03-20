import sys
sys.path.insert(0, '/usr/share/opensipkd/modules')
from base_models import (
    CommonModel,
    )
sys.path.insert(0, '/usr/share/opensipkd-forwarder/modules')
from pbb import (
    PbbBase,
    )
    
sys.path.insert(0, '/etc/opensipkd')
from bca_conf import pbb_db_schema


class Invoice(PbbBase, CommonModel):
    __tablename__ = 'sppt'
    __table_args__ = dict(schema=pbb_db_schema, autoload=True)

class Pembayaran(PbbBase, CommonModel):
    __tablename__ = 'pembayaran_sppt'
    __table_args__ = dict(schema=pbb_db_schema, autoload=True)

class Kelurahan(PbbBase, CommonModel):
    __tablename__ = 'ref_kelurahan'
    __table_args__ = dict(schema=pbb_db_schema, autoload=True)

class Kecamatan(PbbBase, CommonModel):
    __tablename__ = 'ref_kecamatan'
    __table_args__ = dict(schema=pbb_db_schema, autoload=True)

class Kabupaten(PbbBase, CommonModel):
    __tablename__ = 'ref_dati2'
    __table_args__ = dict(schema=pbb_db_schema, autoload=True)

class Propinsi(PbbBase, CommonModel):
    __tablename__ = 'ref_propinsi'
    __table_args__ = dict(schema=pbb_db_schema, autoload=True)
