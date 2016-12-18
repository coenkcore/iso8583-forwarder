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
from base_models import CommonModel
from sismiop.models import Models as SismiopModels



class Models(SismiopModels):
    def __init__(self, Base, db_schema, iso_db_schema=False):
        SismiopModels.__init__(self, Base, db_schema)
        if iso_db_schema is False:
            iso_db_schema = db_schema
        self.InquirySeq = Sequence('inquiry_seq', schema=iso_db_schema)

        class Inquiry(Base, CommonModel):
            __tablename__ = 'inquiry'
            __table_args__ = dict(schema=iso_db_schema)
            id = Column(Integer, self.InquirySeq, primary_key=True)
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
        self.Inquiry = Inquiry

        iso_db_schema_as_prefix = iso_db_schema and iso_db_schema + '.' or ''
        foreign_inquiry_id = iso_db_schema_as_prefix + 'inquiry.id'

        class Payment(Base, CommonModel):
            __tablename__ = 'payment'
            id = Column(String(32), primary_key=True)
            inquiry_id = Column(Integer, ForeignKey(foreign_inquiry_id),
                                nullable=False)
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
            __table_args__ = (
                UniqueConstraint('propinsi', 'kabupaten', 'kecamatan',
                                 'kelurahan', 'blok', 'urut', 'jenis',
                                 'tahun', 'ke'),
                dict(schema=iso_db_schema),
                )
        self.Payment = Payment

        class Reversal(Base, CommonModel):
            __tablename__ = 'reversal'
            __table_args__ = dict(schema=iso_db_schema)
            payment_id = Column(String(32), ForeignKey('payment.id'), primary_key=True)
            tgl = Column(DateTime, default=datetime.now, nullable=False)
            iso_request = Column(String(1024), nullable=False)
        self.Reversal = Reversal
