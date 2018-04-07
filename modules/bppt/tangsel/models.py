from base_models import (
    CommonModel,
    BaseModel,
    IsoModel,
    )
from tools import create_now
from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    DateTime,
    Date,
    Text,
    ForeignKey,
    BigInteger
    )


class OtherModels(object):
    def __init__(self, Base):
        class Perizinan(Base, CommonModel):
            __tablename__ = 'trperizinan'
            id = Column(Integer, primary_key=True) 
            n_perizinan = Column(String(128))
            initial = Column(String(128))
            
        class Pemohon(Base, CommonModel): #B
            __tablename__ = 'tmpemohon'
            id = Column(Integer, primary_key=True) 
            n_pemohon = Column(String(128)) 
            
        class Permohonan(Base, CommonModel): #B
            __tablename__ = 'tmpermohonan'
            id = Column(Integer, primary_key=True) 
            alamatizin = Column(String(128)) 
            trkelurahan_id = Column(Integer) 
            tmpemohon_id = Column(Integer, ForeignKey(Pemohon.id))
            trperizinan_id = Column(Integer, ForeignKey(Perizinan.id))

            
        class Invoice(Base, CommonModel):
            __tablename__ = 'tmretribusi'
            id = Column(Integer, primary_key=True) 
            kd_bayar = Column(String(32)) 
            no_skrd = Column(String(32)) 
            pendaftaran_id = Column(BigInteger)
            jumlah = Column(BigInteger)
            date_skrd = Column(DateTime(timezone=False))
            date_expire = Column(DateTime(timezone=False))
            c_verifikasi_bayar = Column(Integer)
            tgl_verifikasi_bayar = Column(DateTime(timezone=False))
            nominal = Column(BigInteger)
            denda = Column(BigInteger)
            jum_bayar = Column(BigInteger)
            ref_bayar = Column(String(128))
            is_bayar = Column(Integer)
            date_bayar = Column(DateTime(timezone=False))
            cara_bayar = Column(String(128))
            denda_masaberlaku = Column(Integer)
            tmpermohonan_id = Column(Integer, ForeignKey(Permohonan.id))
            #trperizinan_id = Column(Integer, ForeignKey(Perizinan.id))
            
        class Payment(Invoice):
            pass
        
        self.Invoice = Invoice
        self.Payment = Payment
        self.Perizinan = Perizinan
        self.Permohonan = Permohonan
        self.Pemohon = Pemohon


class Models(object):
    def __init__(self, Base):
        class IsoLog(Base, IsoModel):
            __tablename__ = 'iso_log'
            raw = Column(Text, nullable=False)
            request_id = Column(Integer, ForeignKey('iso_log.id'))
            bit002 = Column(Text)
            bit003 = Column(Text)
            bit004 = Column(Text)
            bit007 = Column(Text)
            bit011 = Column(Text)
            bit012 = Column(Text)
            bit013 = Column(Text)
            bit015 = Column(Text)
            bit018 = Column(Text)
            bit022 = Column(Text)
            bit032 = Column(Text)
            bit033 = Column(Text)
            bit035 = Column(Text)
            bit037 = Column(Text)
            bit038 = Column(Text)
            bit039 = Column(Text)
            bit041 = Column(Text)
            bit042 = Column(Text)
            bit043 = Column(Text)
            bit047 = Column(Text)
            bit048 = Column(Text)
            bit049 = Column(Text)
            bit059 = Column(Text)
            bit060 = Column(Text)
            bit061 = Column(Text)
            bit062 = Column(Text)
            bit063 = Column(Text)
            bit102 = Column(Text)
            bit107 = Column(Text)

        self.IsoLog = IsoLog


        class IsoPayment(Base, CommonModel):
            __tablename__ = 'iso_payment'
            id = Column(Integer, ForeignKey('iso_log.id'), primary_key=True)
            response_id = Column(Integer, ForeignKey('iso_log.id'), nullable=False)
            # data_pembayaran.id_pendaftaran
            id_pendaftaran = Column(String(20), nullable=False)
            # data_pembayaran.no_bayar
            no_bayar = Column(String(32), nullable=False)
            tgl = Column(DateTime(timezone=True), nullable=False)
            ntb = Column(String(32), nullable=False)
            ntp = Column(String(32), nullable=False, unique=True)
            bank_id = Column(Integer, nullable=False)
            channel_id = Column(Integer, nullable=False)

        self.IsoPayment = IsoPayment

        class IsoReversal(Base, CommonModel):
            __tablename__ = 'iso_reversal'
            id = Column(Integer, ForeignKey('iso_payment.id'), primary_key=True)
            request_id = Column(Integer, ForeignKey('iso_log.id'), nullable=False)
            response_id = Column(Integer, ForeignKey('iso_log.id'), nullable=False)
            # Salinan dari row tabel data_ssrd yang dihapus
            no_ssrd = Column(String(32))
            date_ssrd = Column(Date)
            no_sts = Column(String(32))
            date_sts = Column(Date)
            jumlah_bayar = Column(Integer)
            cara_bayar = Column(String(128))
            ref_bayar = Column(String(128))
            date_bayar = Column(DateTime)

        self.IsoReversal = IsoReversal


        # IMB 001
        # HO 002
        # PPTR 006
        class Izin(Base, BaseModel):
            __tablename__ = 'izin'
            nama = Column(String(255), nullable=False, unique=True)

        self.Izin = Izin
