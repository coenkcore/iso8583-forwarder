import sys
sys.path[0:0] = ['/usr/share/opensipkd/modules']
from base_models import (
    Base,
    BaseModel,
    CommonModel,
    )
from tools import create_now
from sqlalchemy import (
    create_engine,
    Sequence,
    )
from sqlalchemy import (
    Column,
    String,
    Integer,
    SmallInteger,
    BigInteger,
    Float,
    DateTime,
    Date,
    ForeignKey,
    Boolean,
        
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
 

#TABLE_ARGS = dict(autoload=True, schema='pad')
TABLE_ARGS = dict(autoload=True)
class Rekening(Base, CommonModel):
    __tablename__ = 'ref_rek_6'
    kd_rek_1        = Column(SmallInteger, primary_key=True)
    kd_rek_2        = Column(SmallInteger, primary_key=True)
    kd_rek_3        = Column(SmallInteger, primary_key=True)
    kd_rek_4        = Column(SmallInteger, primary_key=True)
    kd_rek_5        = Column(SmallInteger, primary_key=True)
    kd_rek_6        = Column(SmallInteger, primary_key=True)
    nm_rek_6        = Column(String(255))
    no_peraturan    = Column(String(25))
    tgl_peraturan   = Column(DateTime)
    nm_pendapatan   = Column(String(255))
    tarif           = Column(Float)

class Customer(Base, CommonModel):
    __tablename__ = 'ta_wajib_pajak'
    npwp_gab       = Column(String(25), primary_key=True)
    jn_wajib_pajak = Column(Integer, primary_key=True)
    no_pokok_wp    = Column(String(25))
    jn_wpb         = Column(Integer)
    no_daftar      = Column(String(25))
    nama_wp        = Column(String(50))
    tgl_aktif      = Column(DateTime)
    keterangan     = Column(String(150))
    status         = Column(Boolean)
    
class CustomerUsaha(Base, CommonModel):
    __tablename__ = 'ta_wajib_pajak_usaha'
    no_pokok_wp       = Column(String(25), primary_key=True)
    jn_wajib_pajak    = Column(SmallInteger, primary_key=True)
    jn_usaha_wp       = Column(SmallInteger, primary_key=True)
    kd_usaha          = Column(SmallInteger, primary_key=True)
    nm_usaha          = Column(String(100))
    klasifikasi_usaha = Column(String(100))
    alamat_usaha      = Column(String(255))
    nm_izin           = Column(String(50))
    no_izin           = Column(String(50))
    tgl_izin          = Column(DateTime)

class InvoiceSpt(Base, CommonModel):
    __tablename__ = 'ta_kartu_pajak_pungut'
    tahun           = Column(SmallInteger, primary_key=True) 
    no_spt          = Column(String(25) , primary_key=True)
    tgl_spt         = Column(DateTime )
    no_pokok_wp     = Column(String(25) )
    jn_wajib_pajak  = Column(SmallInteger )
    jn_usaha_wp     = Column(SmallInteger )
    kd_usaha        = Column(SmallInteger )
    jn_pajak        = Column(SmallInteger )
    jn_pemungutan   = Column(SmallInteger )
    jn_penetapan    = Column(SmallInteger )
    masa1           = Column(DateTime)
    masa2           = Column(DateTime)
    kd_urusan       = Column(SmallInteger)
    kd_bidang       = Column(SmallInteger)
    kd_unit         = Column(SmallInteger)
    kd_sub          = Column(SmallInteger)
    kd_nilai        = Column(SmallInteger)
    nm_penerima     = Column(String(50))
    nip_penerima    = Column(String(21))
    jbt_penerima    = Column(String(100))
    tgl_terima      = Column(DateTime)
    keterangan      = Column(String(255))
    
class InvoiceSkp(Base, CommonModel):
    __tablename__ = 'ta_skpd'
    tahun             = Column(SmallInteger, primary_key=True)
    no_ketetapan      = Column(String(25), primary_key=True)
    no_nota           = Column(String(25))
    jns_surat         = Column(SmallInteger)
    kd_urusan         = Column(SmallInteger)
    kd_bidang         = Column(SmallInteger)
    kd_unit           = Column(SmallInteger)
    kd_sub            = Column(SmallInteger)
    kd_bank           = Column(SmallInteger)
    no_pokok_wp       = Column(String(25))
    jn_wajib_pajak    = Column(SmallInteger)
    jn_usaha_wp       = Column(SmallInteger)
    kd_usaha          = Column(SmallInteger)
    jn_pajak          = Column(SmallInteger)
    jn_pemungutan     = Column(SmallInteger)
    masa1             = Column(DateTime)
    masa2             = Column(DateTime)
    tgl_jatuh_tempo   = Column(DateTime)
    tgl_penetapan     = Column(DateTime)
    nm_penandatangan  = Column(String(50))
    nip_penandatangan = Column(String(21))
    jbt_penandatangan = Column(String(75))
    kd_edit           = Column(SmallInteger)
    keterangan        = Column(String(500))     

class InvoiceSkpDet(Base, CommonModel):
    __tablename__ = 'ta_skpd_rinc'
    tahun           = Column(SmallInteger, primary_key=True)
    no_ketetapan    = Column(String(25), primary_key=True)
    no_id           = Column(SmallInteger, primary_key=True)
    kd_rek_1        = Column(SmallInteger)
    kd_rek_2        = Column(SmallInteger)
    kd_rek_3        = Column(SmallInteger)
    kd_rek_4        = Column(SmallInteger)
    kd_rek_5        = Column(SmallInteger)
    kd_rek_6        = Column(SmallInteger)
    bunga           = Column(Float)
    kenaikan        = Column(Float)
    denda           = Column(Float)
    dasar_pengenaan = Column(Float)
    pajak_terhutang = Column(Float)
    nilai_setoran   = Column(Float)
    kompensasi      = Column(Float)
    dll             = Column(Float)
    jumlah          = Column(Float)
   
class Payment(Base, CommonModel):
    __tablename__ = 'ta_sspd'
    tahun           = Column(SmallInteger, primary_key=True, autoincrement=False ) 
    no_sspd         = Column(String(25), primary_key=True)
    tgl_sspd        = Column(DateTime)
    no_ketetapan    = Column(String(25))
    kd_urusan       = Column(SmallInteger)
    kd_bidang       = Column(SmallInteger)
    kd_unit         = Column(SmallInteger)
    kd_sub          = Column(SmallInteger)
    kd_setoran      = Column(SmallInteger)
    jn_setoran      = Column(SmallInteger)
    jn_dokumen      = Column(SmallInteger)
    no_bku          = Column(Integer)
    no_pokok_wp     = Column(String(25))
    jn_wajib_pajak  = Column(SmallInteger)
    jn_usaha_wp     = Column(SmallInteger)
    kd_usaha        = Column(SmallInteger)
    jn_pajak        = Column(SmallInteger)
    jn_pemungutan   = Column(SmallInteger)
    masa1           = Column(DateTime)
    masa2           = Column(DateTime)
    kd_bank         = Column(SmallInteger)
    nm_penerima     = Column(String(25))
    nip_penerima    = Column(String(21))
    jbt_penerima    = Column(String(50))
    nm_penyetor     = Column(String(50))
    alamat_penyetor = Column(String(255))
    keterangan      = Column(String(150))

    
class PaymentDet(Base, CommonModel):
    __tablename__ = 'ta_sspd_rinc'
    tahun       = Column(SmallInteger, primary_key=True, autoincrement=False ) 
    no_sspd     = Column(String(25), primary_key=True)
    no_id       = Column(SmallInteger )
    kd_rek_1    = Column(SmallInteger )
    kd_rek_2    = Column(SmallInteger )
    kd_rek_3    = Column(SmallInteger )
    kd_rek_4    = Column(SmallInteger )
    kd_rek_5    = Column(SmallInteger )
    kd_rek_6    = Column(SmallInteger )
    nilai       = Column(Float)
    keterangan  = Column(String(150))


class Hotel(Base, CommonModel):
    __tablename__ = 'ta_kartu_pajak_hotel' #01
    tahun           = Column(SmallInteger, primary_key=True) 
    no_spt          = Column(String(25) , primary_key=True)
    kd_rek_1        = Column(SmallInteger , primary_key=True)
    kd_rek_2        = Column(SmallInteger , primary_key=True)
    kd_rek_3        = Column(SmallInteger , primary_key=True)
    kd_rek_4        = Column(SmallInteger , primary_key=True)
    kd_rek_5        = Column(SmallInteger , primary_key=True)
    kd_rek_6        = Column(SmallInteger , primary_key=True)
    dasarpengenaan  = Column(Float)
    pajakterhutang  = Column(Float)
    tarifpajak      = Column(Float)
    kas             = Column(Boolean)
    pembukuan       = Column(Boolean)

class Restoran(Base, CommonModel):
    __tablename__ = 'ta_kartu_pajak_restoran' #01
    tahun           = Column(SmallInteger, primary_key=True) 
    no_spt          = Column(String(25) , primary_key=True)
    kd_rek_1        = Column(SmallInteger , primary_key=True)
    kd_rek_2        = Column(SmallInteger , primary_key=True)
    kd_rek_3        = Column(SmallInteger , primary_key=True)
    kd_rek_4        = Column(SmallInteger , primary_key=True)
    kd_rek_5        = Column(SmallInteger , primary_key=True)
    kd_rek_6        = Column(SmallInteger , primary_key=True)
    dasarpengenaan  = Column(Float)
    pajakterhutang  = Column(Float)
    tarifpajak      = Column(Float)
    kas             = Column(Boolean)
    pembukuan       = Column(Boolean)

class Hiburan(Base, CommonModel):
    __tablename__ = 'ta_kartu_pajak_hiburan' #01
    tahun           = Column(SmallInteger, primary_key=True) 
    no_spt          = Column(String(25) , primary_key=True)
    kd_rek_1        = Column(SmallInteger , primary_key=True)
    kd_rek_2        = Column(SmallInteger , primary_key=True)
    kd_rek_3        = Column(SmallInteger , primary_key=True)
    kd_rek_4        = Column(SmallInteger , primary_key=True)
    kd_rek_5        = Column(SmallInteger , primary_key=True)
    kd_rek_6        = Column(SmallInteger , primary_key=True)
    dasarpengenaan  = Column(Float)
    pajakterhutang  = Column(Float)
    tarifpajak      = Column(Float)
    kas             = Column(Boolean)
    pembukuan       = Column(Boolean)    

class Galian(Base, CommonModel):
    __tablename__ = 'ta_kartu_pajak_galian' #01
    tahun           = Column(SmallInteger, primary_key=True) 
    no_spt          = Column(String(25) , primary_key=True)
    kd_rek_1        = Column(SmallInteger , primary_key=True)
    kd_rek_2        = Column(SmallInteger , primary_key=True)
    kd_rek_3        = Column(SmallInteger , primary_key=True)
    kd_rek_4        = Column(SmallInteger , primary_key=True)
    kd_rek_5        = Column(SmallInteger , primary_key=True)
    kd_rek_6        = Column(SmallInteger , primary_key=True)
    dasarpengenaan  = Column(Float)
    pajakterhutang  = Column(Float)
    tarifpajak      = Column(Float)
    kas             = Column(Boolean)
    pembukuan       = Column(Boolean)
class Parkir(Base, CommonModel):
    __tablename__ = 'ta_kartu_pajak_parkir' #01
    tahun           = Column(SmallInteger, primary_key=True) 
    no_spt          = Column(String(25) , primary_key=True)
    kd_rek_1        = Column(SmallInteger , primary_key=True)
    kd_rek_2        = Column(SmallInteger , primary_key=True)
    kd_rek_3        = Column(SmallInteger , primary_key=True)
    kd_rek_4        = Column(SmallInteger , primary_key=True)
    kd_rek_5        = Column(SmallInteger , primary_key=True)
    kd_rek_6        = Column(SmallInteger , primary_key=True)
    dasarpengenaan  = Column(Float)
    pajakterhutang  = Column(Float)
    tarifpajak      = Column(Float)
    kas             = Column(Boolean)
    pembukuan       = Column(Boolean)
    
class PJalan(Base, CommonModel):
    __tablename__ = 'ta_kartu_pajak_pjalan' #01
    tahun           = Column(SmallInteger, primary_key=True) 
    no_spt          = Column(String(25) , primary_key=True)
    kd_rek_1        = Column(SmallInteger , primary_key=True)
    kd_rek_2        = Column(SmallInteger , primary_key=True)
    kd_rek_3        = Column(SmallInteger , primary_key=True)
    kd_rek_4        = Column(SmallInteger , primary_key=True)
    kd_rek_5        = Column(SmallInteger , primary_key=True)
    kd_rek_6        = Column(SmallInteger , primary_key=True)
    dasarpengenaan  = Column(Float)
    pajakterhutang  = Column(Float)
    tarifpajak      = Column(Float)
    kas             = Column(Boolean)
    pembukuan       = Column(Boolean)

class Walet(Base, CommonModel):
    __tablename__ = 'ta_kartu_pajak_walet' #01
    tahun           = Column(SmallInteger, primary_key=True) 
    no_spt          = Column(String(25) , primary_key=True)
    kd_rek_1        = Column(SmallInteger , primary_key=True)
    kd_rek_2        = Column(SmallInteger , primary_key=True)
    kd_rek_3        = Column(SmallInteger , primary_key=True)
    kd_rek_4        = Column(SmallInteger , primary_key=True)
    kd_rek_5        = Column(SmallInteger , primary_key=True)
    kd_rek_6        = Column(SmallInteger , primary_key=True)
    dasarpengenaan  = Column(Float)
    pajakterhutang  = Column(Float)
    tarifpajak      = Column(Float)
    kas             = Column(Boolean)
    pembukuan       = Column(Boolean)
    
"""
class HotelDet(Base):
    __tablename__ = 'ta_kartu_pajak_hotel_rinc'
    __table_args__ = TABLE_ARGS
    
class InvoiceSkp(Base):
    __tablename__ = 'ta_skpd'
    __table_args__ = TABLE_ARGS

class InvoiceSkpDet(Base):
    __tablename__ = 'ta_skpd_rinc'
    __table_args__ = TABLE_ARGS

    

class Restoran(Base):
    __tablename__ = 'ta_kartu_pajak_restoran' #02
    __table_args__ = TABLE_ARGS

class Hiburan(Base):
    __tablename__ = 'ta_kartu_pajak_hiburan' #03
    __table_args__ = TABLE_ARGS
    
class HiburanDet(Base):
    __tablename__ = 'ta_kartu_pajak_hiburan_rinc' 
    __table_args__ = TABLE_ARGS
    
class Reklame(Base):
    __tablename__ = 'ta_kartu_pajak_reklame_1' #04
    __table_args__ = TABLE_ARGS
    
class PPJ(Base):
    __tablename__ = 'ta_kartu_pajak_pjalan' #05
    __table_args__ = TABLE_ARGS
    
class PPJDet(Base):
    __tablename__ = 'ta_kartu_pajak_pjalan_rinc'
    __table_args__ = TABLE_ARGS

class Galian(Base):
    __tablename__ = 'ta_kartu_pajak_galian' #06
    __table_args__ = TABLE_ARGS
    
class Parkir(Base):
    __tablename__ = 'ta_kartu_pajak_parkir' #07
    __table_args__ = TABLE_ARGS
    
class Air(Base):
    __tablename__ = 'ta_kartu_pajak_air' #08
    __table_args__ = TABLE_ARGS
    
    
class Walet(Base):
    __tablename__ = 'ta_kartu_pajak_walet' #09
    __table_args__ = TABLE_ARGS
    
"""
    
#PaymentSequence = Sequence('pad_sspd_id_seq')
"""class Channel(Base, BaseModel):
    __tablename__ = 'pad_channel'
    nama = Column(String(20), nullable=False, unique=True)
"""

#class Bank(Base, BaseModel):
#    __tablename__ = 'ref_bank' # Tempat Pembayaran
#    __table_args__ = TABLE_ARGS
    
    #singkatan = Column(String(16), nullable=False, unique=True)
    #nama = Column(String(32), nullable=False, unique=True)

"""PaymentSequence = Sequence('pad_payment_id_seq')

class IsoPayment(Base, BaseModel):
    __tablename__ = 'pad_payment'
    __table_args__ = TABLE_ARGS
    id = Column(Integer, primary_key=True)
    invoice_id = Column(Integer, ForeignKey('pad_invoice.id'), nullable=False)
    tgl = Column(DateTime(timezone=True),
                 nullable=False,
                 default=create_now)
    tagihan = Column(Float, nullable=False)
    denda = Column(Float, nullable=False)
    total_bayar = Column(Float, nullable=False)
    iso_request = Column(String(1024), nullable=False) # Untuk reversal
    transmission = Column(DateTime(timezone=True), nullable=False)
    settlement = Column(Date, nullable=False)
    stan = Column(Integer, nullable=False)
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
"""