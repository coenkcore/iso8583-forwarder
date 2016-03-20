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
    BigInteger,
    )
from tools import FixLength
    
class MyFixLength(FixLength):
    def get(self, name):
        return self.fields[name]['value'] or None

# http://docs.sqlalchemy.org/en/rel_0_7/dialects/oracle.html
INQUIRY_SEQ = Sequence('inquiry_seq')

# class Inquiry(Base, CommonModel):
    # __tablename__ = 'inquiry'
    # id = Column(Integer, INQUIRY_SEQ, primary_key=True)
    # tgl = Column(DateTime, default=datetime.now, nullable=False)
    # nop = Column(String(32), nullable=False)
    # propinsi = Column(String(2), nullable=False)
    # kabupaten = Column(String(2), nullable=False) 
    # kecamatan = Column(String(3), nullable=False)
    # kelurahan = Column(String(3), nullable=False)
    # blok = Column(String(3), nullable=False)
    # urut = Column(String(4), nullable=False)
    # jenis = Column(String(1), nullable=False) 
    # tahun = Column(Integer, nullable=False)
    # tagihan = Column(Float, nullable=False)
    # jatuh_tempo = Column(Date, nullable=False)
    # bulan_tunggakan = Column(Integer, nullable=False)
    # persen_denda = Column(Float, nullable=False)
    # denda = Column(Float, nullable=False, default=0)
    # transmission = Column(DateTime)
    # stan = Column(Integer)
    # settlement = Column(DateTime)
    # pengirim = Column(String(16), nullable=False)

class Payment(Base, CommonModel):
    __tablename__ = 'payment'
    id = Column(String(32), primary_key=True)
    #inquiry_id = Column(Integer, ForeignKey('inquiry.id'), nullable=False)
    invoice_id = Column(String(32), nullable=False)
    ke = Column(Integer, nullable=False)
    ntb = Column(String(64))
    ntp = Column(String(64))
    bank_id = Column(String(64))
    forwarder_id = Column(String(64))
    tgl = Column(DateTime, default=datetime.now, nullable=False)
    amount = Column(BigInteger, default=0, nullable=False)
    denda = Column(BigInteger, default=0, nullable=False)
    bank_id = Column(String(64))
    channel = Column(String(4))
    status = Column(Integer, default=0, nullable=False)
    __table_args__ = (
        UniqueConstraint('invoice_id', 'ke'),
        )

class Reversal(Base, CommonModel):
    __tablename__ = 'reversal'
    payment_id = Column(String(32), ForeignKey('payment.id'), primary_key=True)
    tgl = Column(DateTime, default=datetime.now, nullable=False)
    #iso_request = Column(String(1024), nullable=False)
