import sys
sys.path[0:0] = ['/usr/share/opensipkd/modules']
from base_models import (
    Base,
    CommonModel,
    )
from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    Float,
    String,
    DateTime,
    Date,
    Sequence,
    UniqueConstraint,
    ForeignKey,
    )
sys.path[0:0] = ['/etc/opensipkd']
from pbb_conf import db_url


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

# http://docs.sqlalchemy.org/en/rel_0_7/dialects/oracle.html
INQUIRY_SEQ = Sequence('inquiry_seq')

class Inquiry(Base, CommonModel):
    __tablename__ = 'inquiry'
    id = Column(Integer, INQUIRY_SEQ, primary_key=True)
    tgl = Column(DateTime, default=datetime.now, nullable=False)
    nop = Column(String(32), nullable=False)
    propinsi = Column(String(2), nullable=False)
    kabupaten = Column(String(2), nullable=False) 
    kecamatan = Column(String(3), nullable=False)
    kelurahan = Column(String(3), nullable=False)
    blok = Column(String(3), nullable=False)
    urut = Column(String(4), nullable=False)
    jenis = Column(String(1), nullable=False) 
    tahun = Column(Integer, nullable=False)
    tagihan = Column(Float, nullable=False)
    jatuh_tempo = Column(Date, nullable=False)
    bulan_tunggakan = Column(Integer, nullable=False)
    persen_denda = Column(Float, nullable=False)
    denda = Column(Float, nullable=False, default=0)
    transmission = Column(DateTime)
    stan = Column(Integer)
    settlement = Column(DateTime)
    pengirim = Column(String(16), nullable=False)

class Payment(Base, CommonModel):
    __tablename__ = 'payment'
    id = Column(String(32), primary_key=True)
    inquiry_id = Column(Integer, ForeignKey('inquiry.id'), nullable=False)
    propinsi = Column(String(2), nullable=False)
    kabupaten = Column(String(2), nullable=False) 
    kecamatan = Column(String(3), nullable=False)
    kelurahan = Column(String(3), nullable=False)
    blok = Column(String(3), nullable=False)
    urut = Column(String(4), nullable=False)
    jenis = Column(String(1), nullable=False) 
    tahun = Column(Integer, nullable=False)
    ke = Column(Integer, nullable=False)
    kd_kanwil_bank = Column(String(2), nullable=False)
    kd_kppbb_bank = Column(String(2), nullable=False)
    kd_bank_tunggal = Column(String(2), nullable=False)
    kd_bank_persepsi = Column(String(2), nullable=False)
    kd_tp = Column(String(2), nullable=False)
    channel = Column(String(4))
    ntb = Column(String(64))
    iso_request = Column(String(1024), nullable=False) # Untuk reversal
    # references pembayaran_sppt
    __table_args__ = (
        UniqueConstraint('propinsi', 'kabupaten', 'kecamatan',
                         'kelurahan', 'blok', 'urut', 'jenis',
                         'tahun', 'ke'),
        )

class Reversal(Base, CommonModel):
    __tablename__ = 'reversal'
    payment_id = Column(String(32), ForeignKey('payment.id'), primary_key=True)
    tgl = Column(DateTime, default=datetime.now, nullable=False)
    iso_request = Column(String(1024), nullable=False)
