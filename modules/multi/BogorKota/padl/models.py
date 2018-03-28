from tools import create_now
from sqlalchemy import (
    Column,
    String,
    Integer,
    DateTime,
    Date,
    ForeignKey,
    )


class Models(object):
    def __init__(self, Base, db_schema):
        class Kecamatan(Base):
            __tablename__ = 'tblkecamatan'
            __table_args__ = dict(autoload=True, schema=db_schema)
        self.Kecamatan = Kecamatan

        class Kelurahan(Base):
            __tablename__ = 'tblkelurahan'
            __table_args__ = dict(autoload=True, schema=db_schema)
        self.Kelurahan = Kelurahan

        class Rekening(Base):
            __tablename__ = 'tblrekening'
            __table_args__ = dict(autoload=True, schema=db_schema)
        self.Rekening = Rekening

        class Pajak(Base):
            __tablename__ = 'pad_pajak'
            __table_args__ = dict(autoload=True, schema=db_schema)

        self.Pajak = Pajak

        class Usaha(Base):
            __tablename__ = 'pad_usaha'
            __table_args__ = dict(autoload=True, schema=db_schema)

        self.Usaha = Usaha

        class Customer(Base):
            __tablename__ = 'pad_customer'
            __table_args__ = dict(autoload=True, schema=db_schema)

        self.Customer = Customer

        class CustomerUsaha(Base):
            __tablename__ = 'pad_customer_usaha'
            __table_args__ = dict(autoload=True, schema=db_schema)

        self.CustomerUsaha = CustomerUsaha

        class Invoice(Base):
            __tablename__ = 'pad_spt'
            __table_args__ = dict(autoload=True, schema=db_schema)

        self.Invoice = Invoice

        class Payment(Base):
            __tablename__ = 'pad_sspd'
            __table_args__ = dict(autoload=True, schema=db_schema)

        self.Payment = Payment

        class Channel(Base):
            __tablename__ = 'pad_channel'
            id = Column(Integer, primary_key=True)
            nama = Column(String(20), nullable=False, unique=True)

        self.Channel = Channel

        class Bank(Base):
            __tablename__ = 'pad_tp'  # Tempat Pembayaran
            id = Column(Integer, primary_key=True)
            singkatan = Column(String(16), nullable=False, unique=True)
            nama = Column(String(32), nullable=False, unique=True)

        self.Bank = Bank


class IsoModels(object):
    def __init__(self, Base):
        class IsoPayment(Base):
            __tablename__ = 'pad_payment'
            id = Column(
                    Integer, ForeignKey('pad.pad_sspd.id'), primary_key=True)
            tgl = Column(DateTime(timezone=True),
                         nullable=False,
                         default=create_now)
            iso_request = Column(String(1024), nullable=False)
            transmission = Column(DateTime(timezone=True), nullable=False)
            settlement = Column(Date, nullable=False)
            stan = Column(Integer, nullable=False)
            invoice_id = Column(Integer,
                                ForeignKey('pad.pad_spt.id'),
                                nullable=False)
            ntb = Column(String(32), nullable=False)
            ntp = Column(String(32), nullable=False, unique=True)
            bank_id = Column(Integer, ForeignKey('pad_tp.id'), nullable=False)
            channel_id = Column(
                    Integer, ForeignKey('pad_channel.id'), nullable=False)
            bank_ip = Column(String(15), nullable=False)

        self.IsoPayment = IsoPayment

        class IsoReversal(Base):
            __tablename__ = 'pad_reversal'
            id = Column(
                    Integer, ForeignKey('pad_payment.id'), primary_key=True)
            tgl = Column(DateTime(timezone=True),
                         nullable=False,
                         default=create_now)
            iso_request = Column(String(1024), nullable=False)

        self.IsoReversal = IsoReversal
