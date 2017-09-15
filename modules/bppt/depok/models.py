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
    )


class OtherModels(object):
    def __init__(self, Base):
        class Invoice(Base, CommonModel):
            __tablename__ = 'data_pembayaran'
            id_pendaftaran = Column(String(20), primary_key=True)
            no_bayar = Column(String(32))
            no_sps = Column(String(32))
            tgl_sps = Column(Date)
            nama_izin = Column(String(128))
            nama_wp = Column(String(128))
            lokasi_izin = Column(String(128))
            nominal = Column(Integer)
            denda = Column(Integer)
            jumlah = Column(Integer)
            date_entry = Column(DateTime)

        self.Invoice = Invoice

        class Payment(Base, CommonModel):
            __tablename__ = 'data_ssrd'
            id_pendaftaran = Column(String(20), primary_key=True)
            no_bayar = Column(String(32))
            no_ssrd = Column(String(32))
            date_ssrd = Column(Date)
            no_sts = Column(String(32))
            date_sts = Column(Date)
            jumlah_bayar = Column(Integer)
            cara_bayar = Column(String(128))
            ref_bayar = Column(String(128))
            date_bayar = Column(DateTime)

        self.Payment = Payment


class Models(object):
    def __init__(self, Base):
        class IsoLog(Base, IsoModel):
            __tablename__ = 'iso_log'
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
