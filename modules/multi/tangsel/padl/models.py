from tools import create_now
from sqlalchemy import (
    Column,
    BigInteger,
    String,
    Integer,
    DateTime,
    Date,
    ForeignKey,
    )


class IsoModels(object):
    def __init__(self, Base):
        class IsoPayment(Base):
            __tablename__ = 'pad_payment'
            id = Column(BigInteger, primary_key=True, autoincrement=True)
            sspd_id = Column(BigInteger, primary_key=True)
            tgl = Column(DateTime(timezone=True),
                         nullable=False,
                         default=create_now)
            iso_request = Column(String(1024), nullable=False)
            transmission = Column(DateTime(timezone=True), nullable=False)
            settlement = Column(Date, nullable=False)
            stan = Column(Integer, nullable=False)
            invoice_no = Column(String(32), nullable=False)
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
