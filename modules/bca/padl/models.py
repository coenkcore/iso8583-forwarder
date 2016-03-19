import sys
sys.path[0:0] = ['/usr/share/opensipkd/modules']
from base_models import (
    Base,
    CommonModel,
    )


class Invoice(Base, CommonModel):
    __tablename__ = 'sppt'
    __table_args__ = dict(autoload=True)

class Pembayaran(Base, CommonModel):
    __tablename__ = 'pembayaran_sppt'
    __table_args__ = dict(autoload=True)

class Kelurahan(Base, CommonModel):
    __tablename__ = 'ref_kelurahan'
    __table_args__ = dict(autoload=True)

class Kecamatan(Base, CommonModel):
    __tablename__ = 'ref_kecamatan'
    __table_args__ = dict(autoload=True)

class Kabupaten(Base, CommonModel):
    __tablename__ = 'ref_dati2'
    __table_args__ = dict(autoload=True)

class Propinsi(Base, CommonModel):
    __tablename__ = 'ref_propinsi'
    __table_args__ = dict(autoload=True)
