import sys
from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    BigInteger,
    String,
    Date,
    Time,
    DateTime,
    UniqueConstraint,
    ForeignKey,
    )
sys.path.insert(0, '/usr/share/opensipkd/modules')
from base_models import (
    Base,
    CommonModel,
    )
sys.path.insert(0, '/etc/opensipkd')
from bphtb_conf import is_need_sppt
from structure import TRANSACTION_BITS


if is_need_sppt:
    class Sppt(Base):
        __tablename__ = 'sppt'
        __table_args__ = dict(autoload=True)


class Payment(Base):
    __tablename__ = 'bphtb_bank'
    id = Column(BigInteger, primary_key=True)
    tanggal = Column(Date, nullable=False)
    jam = Column(Time, nullable=False)
    seq = Column(Integer, nullable=False)
    transno = Column(String(20), nullable=False)
    cabang = Column(String(5))
    users = Column(String(5))
    bankid = Column(Integer, nullable=False)
    txs = Column(String(5), nullable=False)
    sspd_id = Column(Integer)
    nop = Column(String(50), nullable=False)
    tahun = Column(Integer)
    kd_propinsi = Column(String(2))
    kd_dati2 = Column(String(2))
    kd_kecamatan = Column(String(2))
    kd_kelurahan = Column(String(2))
    kd_blok = Column(String(3))
    no_urut = Column(String(4))
    kd_jns_op = Column(String(1))
    thn_pajak_sppt = Column(String(4))
    wp_nama = Column(String(50), nullable=False)
    wp_alamat = Column(String(100))
    wp_blok_kav = Column(String(100))
    wp_rt = Column(String(3))
    wp_rw = Column(String(3))
    wp_kelurahan = Column(String(30))
    wp_kecamatan = Column(String(30))
    wp_kota = Column(String(30))
    wp_provinsi = Column(String(50))
    wp_kdpos = Column(String(5))
    wp_identitas = Column(String(50))
    wp_identitaskd = Column(String(50))
    wp_npwp = Column(String(50))
    notaris = Column(String(50))
    bumi_luas = Column(Integer)
    bumi_njop = Column(Integer)
    bng_luas = Column(Integer)
    bng_njop = Column(Integer)
    npop = Column(BigInteger)
    bayar = Column(BigInteger) 
    denda = Column(Integer)
    bphtbjeniskd = Column(Integer)
    __table_args__ = (
        (UniqueConstraint('tanggal', 'jam', 'seq', 'transno')),
        dict(schema='bphtb'),
        )


class IsoPayment(Base, CommonModel):
    __tablename__ = 'bphtb_payment'
    __table_args__ = dict(schema='bphtb')
    #trx_id = Column(BigInteger, ForeignKey('Transaction'), primary_key=True)
    trx_id = Column(BigInteger, primary_key=True)
    iso_request = Column(String(1024), nullable=False) # Tadinya untuk reversal
    bit2 = Column(String(32)) # ['PAN', 'Primary Account Number', 'LL', 2+19, 'n'],
    bit3 = Column(String(8)) # ['Processing', 'Processing Code', 'N', 6, 'n'], # '341019'
    bit4 = Column(String(16)) # ['Amount', 'Amount Transaction', 'N', 12, 'n'],
    bit7 = Column(String(16)) # ['Transmission', 'Transmission Datetime', 'N', 10, 'n'],
    bit11 = Column(String(8)) # ['STAN', 'System Trace Audit Number', 'N', 6, 'n'],
    bit12 = Column(String(8)) # ['Time', 'Time Local Transaction', 'N', 6, 'n'],
    bit13 = Column(String(4)) # ['Date', 'Date Local Transaction', 'N', 4, 'n'],
    bit15 = Column(String(4)) # ['Settlement', 'Settlement Date', 'N', 4, 'n'],
    bit18 = Column(String(4)) # ['Merchant', 'Merchant Type', 'N', 4, 'n'],
    bit22 = Column(String(4)) # ['POS', 'POS Entry Mode Code', 'N', 3, 'n'], # '021'
    bit32 = Column(String(16)) # ['Acquiring', 'Acquiring Institution Code', 'LL', 2+11, 'n'], # '110'
    bit33 = Column(String(16)) # ['Forwarding', 'Forwarding Institution ID Code', 'LL', 2+11, 'n'], # '00110'
    bit35 = Column(String(64)) # ['Track', 'Track 2 Data', 'LL', 2+37, 'n'],
    bit37 = Column(String(16)) # ['Sequence', 'Sequence Number', 'N', 12, 'n'],
    bit41 = Column(String(8)) # ['Terminal', 'Terminal Identification Number', 'N', 8, 'ans'],
    bit42 = Column(String(16)) # ['User', 'Terminal Name / User Identification', 'N', 15, 'ans'],
    bit43 = Column(String(64)) # ['Card', 'Card Acceptor Name / Location', 'ANS', 40, 'ans'],
    bit47 = Column(String(256)) # ['Invoice Profile', 'Nomor Transaksi Pemda', 'LLL', 3+177, 'ans'], # Payment
    bit48 = Column(String(256)) # ['Invoice Profile 2', 'Nomor Transaksi Bank', 'LLL', 3+163, 'ans'], # Payment
    bit49 = Column(String(4)) # ['Currency', 'Transaction Currency Code', 'N', 3, 'n'],
    bit61 = Column(String(32)) # ['Invoice', 'Invoice ID', 'LLL', 3+22, 'ans'], # 1-18 NOP, 19-22 Tahun Pajak
    bit63 = Column(String(8)) # ['Additional', 'Additional Data', 'LLL', 3+3, 'ans'], # '214'
    bit102 = Column(String(32)) # ['Source', 'Source Account Number', 'LL', 2+20, 'ans'],
    bit107 = Column(String(16)) # ['Cabang', 'Kode Cabang, User ID', 'LLL', 3+8, 'ans'], # 1-4 Kode Cabang, 5-8 User ID

    def from_iso(self, iso):
        self.iso_request = iso.getRawIso()
        d = {}
        for bit in TRANSACTION_BITS:
            if bit in [39, 70, 102]:
                continue
            fieldname = 'bit%d' % bit
            value = iso.getBit(bit)
            d[fieldname] = value
        self.from_dict(d)

    @staticmethod
    def search_iso(iso):
        d = {}
        for bit in TRANSACTION_BITS:
            if bit in [7, 39, 70, 102]:
                continue
            fieldname = 'bit%d' % bit
            d[fieldname] = iso.getBit(bit)
        q = DBSession.query(IsoPayment).filter_by(**d).\
                order_by(IsoPayment.trx_id.desc())
        return q.first()


class Reversal(Base):
    __tablename__ = 'bphtb_reversal'
    __table_args__ = dict(schema='bphtb')
    pay_trx_id = Column(Integer, primary_key=True)
    tgl = Column(DateTime, default=datetime.now, nullable=False)
