from base_models import CommonModel
from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    DateTime,
    Date,
    ForeignKey,
    )
from sqlalchemy.ext.declarative import declarative_base
from config import bphtb as conf
db_schema = conf['db_schema']


Base = declarative_base()


class Invoice(Base, CommonModel):
    __tablename__ = 'tagihan_bphtb'
    __table_args__ = dict(schema=db_schema)
    id = Column(Integer, primary_key=True)
    no_tagihan = Column(String(10), nullable=False)
    no_dokumen = Column(String(15), nullable=False)
    user_entry = Column(Integer, nullable=False)
    tahun_pajak = Column(Integer)
    nama_wp = Column(String(150), nullable=False)
    npwp_wp = Column(String(100))
    ktp_wp = Column(String(50), nullable=False)
    alamat_wp = Column(String(255))
    kelurahan_wp = Column(String(100))
    rt_wp = Column(String(4))
    rw_wp = Column(String(4))
    kecamatan_wp = Column(String(100))
    kota_wp = Column(String(100))
    kode_pos_wp = Column(String(6))
    luas_bangunan_sppt = Column(Float)
    luas_tanah_sppt = Column(Float)
    njop_tanah_sppt = Column(Float)
    njop_bangunan_sppt = Column(Float)
    njop_sppt = Column(String(100))
    nilai_pasar = Column(Float)
    npop = Column(Float)
    njoptkp = Column(Float)
    npopkp = Column(Float)
    bphtb_hrs_bayar = Column(Float)
    status_pembayaran = Column(Integer)
    tgl_terbit = Column(DateTime)
    jml_cetak = Column(Integer)
    cuser = Column(Integer)
    cdate = Column(DateTime)
    muser = Column(Integer)
    mdate = Column(Date)
    nop_baru = Column(String(100))
    tgl_validasi = Column(DateTime)
    user_validasi = Column(Integer)
    luas_bangunan = Column(Float)
    luas_tanah = Column(Float)
    jns_perolehan_hak = Column(String(100))
    nama_notaris = Column(String(100))
    nama_wajib_pajak = Column(String(100))
    kelurahan_op = Column(String(100))
    kecamatan_op = Column(String(100))
    alamat_op = Column(String(100))
    jumlah_denda = Column(Float)
    tgl_bayar = Column(Date)
    id_sspd = Column(Integer, nullable=False)
    nop = Column(String(100))
             
 
class Payment(Base, CommonModel):
    __tablename__ = 'pembayaran_bphtb'
    __table_args__ = dict(schema=db_schema)
    id = Column(Integer, primary_key=True)
    id_tagihan = Column(Integer, ForeignKey(Invoice.id))
    jumlah_yg_dibayar= Column(Float)       
    tgl_pembayaran = Column(DateTime(timezone=False))
    tgl_rekam = Column(DateTime(timezone=False))
