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
        class Perizinan(Base):
            __tablename__ = 'trperizinan'
            id = Column(Integer, primary_key=True)
            n_perizinan = Column(String(255))
            initial = Column(String(35))
            c_tarif = Column(Integer)
            is_open = Column(Integer)
            v_hari = Column(Integer)
            v_berlaku_tahun = Column(Integer)
            v_perizinan = Column(Integer)
            c_foto = Column(Integer)
            c_keputusan = Column(Integer)
            kode_ijin = Column(String(11))
            id_bidang = Column(Integer)
            no_rek = Column(String(32))
            no_rek_denda = Column(String(32))
            keterangan = Column(Text)
            is_peruntukan = Column(Integer)
            id_kelompok_ijin = Column(Integer)
            draft_sk = Column(String(100), nullable=False)
            draft_sertifikat = Column(String(100), nullable=False)
            aktif = Column(String(1))

        class Pemohon(Base):
            __tablename__ = 'tmpemohon'
            id = Column(Integer, primary_key=True)
            no_referensi = Column(String(50), primary_key=True)
            n_pemohon = Column(String(255))
            telp_pemohon = Column(String(50))
            a_pemohon = Column(Text)
            a_pemohon_luar = Column(Text)
            i_user = Column(String(50))
            d_entry = Column(DateTime)
            npwrd = Column(String(32))
            trkelurahan_id = Column(Integer)
            email = Column(String(50))

        class Permohonan(Base):
            __tablename__ = 'tmpermohonan'
            id = Column(Integer, primary_key=True)
            tmpemohon_id = Column(Integer, ForeignKey(Pemohon.id))
            pendaftaran_id = Column(String(23))
            trstspermohonan_id = Column(Integer)
            trperijinan_id = Column(Integer)
            trperuntukan_id = Column(Integer)
            d_ambil_izin = Column(Date, primary_key=True)
            d_izin_dicabut = Column(Date)
            i_urut = Column(Integer)
            a_izin = Column(Text)
            c_paralel = Column(Integer)
            c_tinjauan = Column(Integer)
            c_izin_selesai = Column(Integer)
            c_izin_dicabut = Column(Integer, primary_key=True)
            id_lama = Column(Integer)
            d_perubahan = Column(Date)
            d_perpanjangan = Column(Date)
            d_daftarulang = Column(Date)
            i_entry = Column(String(50))
            d_entry = Column(DateTime)
            c_status_bayar = Column(Integer)
            keterangan = Column(String(255))
            trperizinan_id = Column(Integer, ForeignKey(Perizinan.id))
            trjenispermohonan_id = Column(Integer)
            trkelurahan_id = Column(String(20))
            alamatizin = Column(Text)
            tmregister_id = Column(Integer)
            c_click = Column(Integer)
            d_verifikasi = Column(Date)
            nm_verifikasi = Column(String(50))
            d_persetujuan = Column(Date)
            d_survey = Column(Date)
            d_bap = Column(Date)
            d_keputusan = Column(Date)
            d_kabid = Column(Date)
            d_sekban = Column(Date)
            d_kaban = Column(Date)
            d_skrd = Column(Date)
            d_cetaksk = Column(Date)
            d_arsip = Column(Date)
            d_tolak = Column(Date)
            c_verifikasi_berkas = Column(Integer)
            c_bap = Column(Integer)
            c_persetujuan = Column(Integer)
            c_keputusan = Column(Integer)
            c_kabid = Column(Integer)
            c_sekban = Column(Integer)
            c_kaban = Column(Integer)
            c_skrd = Column(Integer)
            c_cetaksk = Column(Integer)
            c_not_like = Column(Integer)
            c_tolak = Column(Integer)
            c_arsip = Column(Integer)
            i_user_tolak = Column(String(100))
            alasan_tolak = Column(Text)
            c_sk1 = Column(Integer)
            c_sk2 = Column(Integer)
            file_sk1 = Column(String(200))
            file_sk2 = Column(String(200))
            no_skbaru = Column(String(50))
            tgl_penetapan = Column(Date)
            no_sklama = Column(String(50))
            tgl_msberkalu_sk = Column(Date)
            tgl_msberlaku_sk_lama = Column(Date)
            d_pengesahan = Column(Date)
            ip_client = Column(String(30))
            token = Column(String(50))
            kode_izin = Column(String(10))
            latitude = Column(String(30), nullable=False)
            longitude = Column(String(30), nullable=False)
            c_pending = Column(Integer, nullable=False)
            catatan_mutasi = Column(String(200), nullable=False)
            c_bapenda = Column(Integer, nullable=False)
            pbb_nop = Column(String(18))
            pbb_nama_wp = Column(String(100))
            pbb_alamat_wp = Column(String(200))
            pbb_alamat_op = Column(String(200))
            pbb_luas_bumi = Column(Float)
            pbb_luas_bng = Column(Float)
            tgl_msberkalu_sk_manual = Column(String(255))
            isiemail = Column(Text)
            ditolak_dt = Column(String(255))
            ttd = Column(Integer)
            daftar_dari = Column(String(50))
            s_bap = Column(String(1))

        class Invoice(Base, CommonModel):
            __tablename__ = 'tmretribusi'
            id = Column(Integer, primary_key=True)
            tmpermohonan_id = Column(Integer, ForeignKey(Permohonan.id))
            pendaftaran_id = Column(String(22))
            nominal = Column(Float)
            denda_masaberlaku = Column(Float)
            denda = Column(Float)
            jumlah = Column(Float)
            no_skrd = Column(String(32))
            date_skrd = Column(Date)
            no_ssrd = Column(String(32))
            date_ssrd = Column(Date)
            jum_bayar = Column(Float)
            is_bayar = Column(Integer)
            cara_bayar = Column(String(32))
            ref_bayar = Column(String(32))
            date_bayar = Column(Date)
            date_expire = Column(Date)
            user_entry = Column(String(32))
            date_entry = Column(DateTime)
            ip_addres = Column(String(50))
            i_urut = Column(Integer)
            i_urut_ssrd = Column(Integer)
            i_urut_ho = Column(Integer)
            i_urut_ssrd_ho = Column(Integer)
            no_bku = Column(String(32))
            file_buktibayar = Column(String(200))
            npwd = Column(String(100))
            kode_bayar = Column(String(14))
            pembayaran_melalui = Column(String(8))
            status_pembayaran = Column(String(11))
            kurang_bayar = Column(Float)
            tgl_kurangbayar = Column(Date)
            time_bayar = Column(DateTime)

        self.Invoice = Invoice
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
            id = Column(
                Integer, ForeignKey(IsoLog.id), primary_key=True)
            response_id = Column(
                Integer, ForeignKey(IsoLog.id), nullable=False)
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
            id = Column(
                Integer, ForeignKey(IsoPayment.id), primary_key=True)
            request_id = Column(
                Integer, ForeignKey(IsoLog.id), nullable=False)
            response_id = Column(
                Integer, ForeignKey(IsoLog.id), nullable=False)
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

        class Channel(Base, BaseModel):
            __tablename__ = 'channel'
            nama = Column(String(8), nullable=False, unique=True)

        self.Channel = Channel
