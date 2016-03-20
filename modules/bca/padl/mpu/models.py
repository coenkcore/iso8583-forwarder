import sys
from datetime import (
    date,
    timedelta,
    )
from sqlalchemy import (
    Column,
    String,
    Text,
    Integer,
    Float,
    DateTime,
    Date,
    ForeignKey,
    UniqueConstraint,
    func,
    and_,
    )
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )
sys.path.insert(0, '/usr/share/opensipkd/modules')
from base_models import (
    Base,
    BaseModel,
    CommonModel,
    DBSession,
    )
from tools import create_now


class InvoiceView(Base, CommonModel):
    __tablename__ = 'view_h2h'
    spt_id = Column(Integer, primary_key=True)
    kode_bayar = Column(Integer)
    spt_nomor = Column(Integer)
    spt_periode = Column(Integer)
    nama_wajibpajak = Column(String(100))
    alamat_wajibpajak = Column(String(150))
    kecamatan_wajibpajak = Column(String(30))
    kelurahan_wajibpajak = Column(String(30))
    kabkot_wajibpajak = Column(String(30))
    npwpd = Column(Text)
    wp_wr_id = Column(Integer)
    spt_jenis_pajakretribusi = Column(Integer)
    spt_periode_jual1 = Column(Date)
    spt_periode_jual2 = Column(Date)
    spt_status = Column(Integer)
    jenis_ketetapan = Column(String(50))
    dasar_pengenaan = Column(Float)
    jumlah_pajak = Column(Float)
    kode_rekening = Column(Text)
    nama_rekening = Column(String(200))
    korek_id = Column(Integer)
    jatuh_tempo = Column(Date)
    is_bayar = Column(Text)


class Payment(Base, CommonModel):
    __tablename__ = 'setoran_pajak_retribusi'
    setorpajret_id = Column(Integer, primary_key=True)
    setorpajret_id_penetapan = Column(Integer) # Invoice.spt_id
    setorpajret_no_bukti = Column(Integer, nullable=False)
    setorpajret_tgl_bayar = Column(Date, nullable=False)
    setorpajret_jlh_bayar = Column(Float, nullable=False)
    setorpajret_via_bayar = Column(Integer, nullable=False)
    setorpajret_jenis_ketetapan = Column(Integer)
    setorpajret_jlh_denda = Column(Float)
    setorpajret_time = Column(DateTime)
    setorpajret_timestart = Column(DateTime)
    setorpajret_sms = Column(Integer)

    @staticmethod
    def get_last_no_bukti(tgl_bayar):
        tahun = tgl_bayar.year
        q = DBSession.query(func.max(Payment.setorpajret_no_bukti)).filter(and_(
             Payment.setorpajret_tgl_bayar > date(tahun-1, 12, 31),
             Payment.setorpajret_tgl_bayar < date(tahun+1, 1, 1)))
        row = q.first()
        return row[0]

    @staticmethod
    def create(invoice, tgl_bayar, tagihan_pokok):
        last_no_bukti = Payment.get_last_no_bukti(tgl_bayar)
        row = Payment()
        row.setorpajret_no_bukti = last_no_bukti + 1
        row.setorpajret_id_penetapan = invoice.spt_id
        row.setorpajret_tgl_bayar = tgl_bayar.date() 
        row.setorpajret_jlh_bayar = tagihan_pokok 
        row.setorpajret_via_bayar = 2 # tanda bahwa ini lewat bank
        row.setorpajret_jenis_ketetapan = invoice.spt_status
        row.setorpajret_time = tgl_bayar
        return row

    @staticmethod
    def create_denda(pay, inv_denda):
        last_no_bukti = Payment.get_last_no_bukti(pay.setorpajret_tgl_bayar)
        row = Payment()
        row.setorpajret_no_bukti = last_no_bukti + 1
        row.setorpajret_id_penetapan = inv_denda.netapajrek_id
        row.setorpajret_tgl_bayar = pay.setorpajret_tgl_bayar
        row.setorpajret_jlh_bayar = inv_denda.netapajrek_besaran 
        row.setorpajret_via_bayar = pay.setorpajret_via_bayar
        row.setorpajret_jenis_ketetapan = pay.setorpajret_jenis_ketetapan
        row.setorpajret_time = pay.setorpajret_time
        return row
 

# Untuk view_h2h.spt_status = 8
class PaymentDetail(Base, CommonModel):
    __tablename__ = 'setoran_pajak_retribusi_self_detail'
    sprsd_id = Column(Integer, primary_key=True)
    sprsd_id_setor = Column(Integer, nullable=False)
    sprsd_idwpwr = Column(Integer, nullable=False)
    sprsd_kode_rek = Column(Integer, nullable=False)
    sprsd_omzet = Column(Float, nullable=False)
    sprsd_periode_jual1 = Column(Date, nullable=False)
    sprsd_periode_jual2 = Column(Date, nullable=False)
    sprsd_thn = Column(Integer, nullable=False)
    sprsd_id_spt = Column(Integer)

    @staticmethod
    def create(pay, inv, rek_id):
        row = PaymentDetail()
        row.sprsd_id_setor = pay.setorpajret_id
        row.sprsd_idwpwr = inv.wp_wr_id
        row.sprsd_kode_rek = rek_id
        row.sprsd_omzet = inv.dasar_pengenaan
        row.sprsd_periode_jual1 = inv.spt_periode_jual1
        row.sprsd_periode_jual2 = inv.spt_periode_jual2
        row.sprsd_thn = inv.spt_periode
        row.sprsd_id_spt = inv.spt_id
        return row


JENIS_PAJAK = {
    1: 244, # 4.1.4.07.01 Pendapatan Denda Pajak Hotel
    2: 245, # 4.1.4.07.02 Pendapatan Denda Pajak Restoran
    3: 246, # 4.1.4.07.03 Pendapatan Denda Pajak Hiburan
    4: 247, # 4.1.4.07.04 Pendapatan Denda Pajak Reklame
    5: 248, # 4.1.4.07.05 Pendapatan Denda Pajak Penerangan Jalan
    6: 249, # 4.1.4.07.06 Pendapatan Denda Pajak Mineral Bukan Logam dan Batuan
    7: 250, # 4.1.4.07.07 Pendapatan Denda Pajak Parkir
    8: 251, # 4.1.4.07.08 Pendapatan Denda Pajak Air Tanah
    }

JATUH_TEMPO_DENDA = timedelta(30)

class Invoice(Base, CommonModel):
    __tablename__ = 'penetapan_pajak_retribusi'
    netapajrek_id = Column(Integer, primary_key=True)
    netapajrek_id_spt = Column(Integer)
    netapajrek_tgl = Column(Date, nullable=False)
    netapajrek_wkt_proses = Column(DateTime, nullable=False)
    netapajrek_tgl_jatuh_tempo = Column(Date)
    netapajrek_kohir = Column(Integer)
    netapajrek_jenis_ketetapan = Column(Integer)
    netapajrek_setoran_sebelumnya = Column(Integer)
    netapajrek_besaran = Column(Float)
    netapajrek_kode_rek = Column(Integer)
    netapajrek_id_lhp = Column(Integer)
    netapajrek_keterangan = Column(String(200))
    netapajrek_time = Column(DateTime)
    id_surat_teguran_sptpd = Column(Integer)
    __table_args__ = (
        UniqueConstraint('netapajrek_jenis_ketetapan',
            'netapajrek_setoran_sebelumnya'),
        )

    @staticmethod
    def get_last_kohir(tahun):
        q = DBSession.query(func.max(Invoice.netapajrek_kohir)).\
                filter(Invoice.netapajrek_tgl > date(tahun-1, 12, 31),
                       Invoice.netapajrek_tgl < date(tahun+1, 1, 1),
                       Invoice.netapajrek_jenis_ketetapan == 3)
        row = q.first()
        return row[0]

    @staticmethod
    def create_denda(invoice, pay):
        if invoice.spt_status == 8:
            id_spt = invoice.spt_id
        else:
            q = DBSession.query(Invoice).filter_by(
                    netapajrek_id=invoice.spt_id,
                    netapajrek_jenis_ketetapan=invoice.spt_status)
            spt = q.first()
            id_spt = spt.netapajrek_id_spt
        kohir = Invoice.get_last_kohir(pay.setorpajret_tgl_bayar.year) \
                + 1
        row = Invoice()
        row.netapajrek_id_spt = id_spt
        row.netapajrek_kohir = kohir
        row.netapajrek_jenis_ketetapan = 3
        row.netapajrek_setoran_sebelumnya = pay.setorpajret_id
        row.netapajrek_tgl = pay.setorpajret_tgl_bayar
        row.netapajrek_tgl_jatuh_tempo = row.netapajrek_tgl + JATUH_TEMPO_DENDA
        row.netapajrek_wkt_proses = pay.setorpajret_time
        row.netapajrek_kode_rek = JENIS_PAJAK[invoice.spt_jenis_pajakretribusi]
        row.netapajrek_id_lhp = 0
        row.id_surat_teguran_sptpd = 0
        return row


class IsoPayment(Base, BaseModel):
    __tablename__ = 'pad_payment'
    tgl = Column(DateTime(timezone=True),
                 nullable=False,
                 default=create_now)
    iso_request = Column(String(1024), nullable=False)
    transaction_time = Column(DateTime(timezone=True), nullable=False)
    spt_id = Column(Integer, nullable=False) # Invoice.spt_id
    tahun_bayar = Column(Integer, nullable=False)
    # Payment.setorpajret_no_bukti
    nomor_bukti = Column(Integer, nullable=False)
    tagihan = Column(Float, nullable=False)
    denda = Column(Float, nullable=False)
    total_bayar = Column(Float, nullable=False)
    ntb = Column(String(32), nullable=False)
    # ntp = str(tahun_bayar) + str(nomor_bukti).zfill(6)
    ntp = Column(String(32), nullable=False, unique=True)
    bank_id = Column(Integer, nullable=False) 
    channel_id = Column(Integer, nullable=False)
    bank_ip = Column(String(15), nullable=False)


class IsoReversal(Base, BaseModel):
    __tablename__ = 'pad_reversal'
    id = Column(Integer, ForeignKey('pad_payment.id'), primary_key=True)
    tgl = Column(DateTime(timezone=True),
                 nullable=False,
                 default=create_now)
    iso_request = Column(String(1024), nullable=False)
