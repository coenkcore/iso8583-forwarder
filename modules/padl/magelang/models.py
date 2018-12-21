from base_models import (
    Base,
    CommonModel,
    BaseModel,
    )
from tools import create_now
from sqlalchemy import (
    Column,
    String,
    BigInteger,
    Integer,
    Float,
    DateTime,
    Date,
    Text,
    Boolean,
    Time,
    ForeignKey,
    UniqueConstraint,
    )


class Kecamatan(Base):
    __tablename__ = 'tblkecamatan'
    id = Column(Integer, primary_key=True)
    kecamatankd = Column(String(2), nullable=False, unique=True)
    kecamatannm = Column(String(50))
    tmt = Column(DateTime)
    enabled = Column(Integer)
    create_date = Column(DateTime)
    create_uid = Column(Integer)
    write_date = Column(DateTime)
    write_uid = Column(Integer)
    __table_args__ = (
        dict(schema='pad'),)


class Kelurahan(Base):
    __tablename__ = 'tblkelurahan'
    id = Column(Integer, primary_key=True)
    kecamatan_id = Column(Integer, ForeignKey(Kecamatan.id), nullable=False)
    kelurahankd = Column(String(3), nullable=False)
    kelurahannm = Column(String(25))
    tmt = Column(DateTime)
    enabled = Column(Integer)
    create_date = Column(DateTime)
    create_uid = Column(Integer)
    write_date = Column(DateTime)
    write_uid = Column(Integer)
    __table_args__ = (
        UniqueConstraint('kecamatan_id', 'kelurahankd'),
        dict(schema='pad'))


class Rekening(Base, CommonModel):
    __tablename__ = 'tblrekening'
    id = Column(Integer, primary_key=True)
    rekeningkd = Column(String(15), nullable=False, unique=True)
    rekeningnm = Column(String(150))
    levelid = Column(Integer)
    issummary = Column(Integer, nullable=False)
    defsign = Column(Integer)
    isppkd = Column(Integer, nullable=False)
    tmt = Column(DateTime)
    enabled = Column(Integer)
    create_date = Column(DateTime)
    create_uid = Column(Integer)
    write_date = Column(DateTime)
    write_uid = Column(Integer)
    insidentil = Column(Integer)
    __table_args__ = (
        dict(schema='pad'),)


class Usaha(Base, CommonModel):
    __tablename__ = 'pad_usaha'
    id = Column(Integer, primary_key=True)
    usahanm = Column(String(50), nullable=False)
    so = Column(String(1))
    tmt = Column(DateTime)
    enabled = Column(Integer)
    create_date = Column(DateTime)
    create_uid = Column(Integer)
    write_date = Column(DateTime)
    write_uid = Column(Integer)
    __table_args__ = (
        dict(schema='pad'),)


class Pajak(Base, CommonModel):
    __tablename__ = 'pad_pajak'
    id = Column(Integer, primary_key=True)
    usaha_id = Column(Integer, ForeignKey(Usaha.id), nullable=False)
    pajaknm = Column(String(200))
    rekening_id = Column(Integer, ForeignKey(Rekening.id), nullable=False)
    rekeningkdsub = Column(String(5))
    rekdenda_id = Column(Integer)
    masapajak = Column(Integer, nullable=False)
    jatuhtempo = Column(Integer)
    multiple = Column(Integer)
    jalan_klas_id = Column(Integer)
    tmt = Column(DateTime)
    enabled = Column(Integer)
    create_date = Column(DateTime)
    create_uid = Column(Integer)
    write_date = Column(DateTime)
    write_uid = Column(Integer)
    jenis_reklame_id = Column(Integer)
    reklame_luas_min = Column(Integer)
    reklame_luas_max = Column(Integer)
    __table_args__ = (
        UniqueConstraint('rekening_id', 'rekeningkdsub'),
        dict(schema='pad'))


class Customer(Base, CommonModel):
    __tablename__ = 'pad_customer'
    id = Column(Integer, primary_key=True)
    parent = Column(Integer)
    npwpd = Column(String(17))
    rp = Column(String(1))
    pb = Column(Integer)
    formno = Column(Integer, nullable=False)
    reg_date = Column(DateTime)
    customernm = Column(String(50))
    kecamatan_id = Column(Integer, ForeignKey(Kecamatan.id))
    kelurahan_id = Column(Integer, ForeignKey(Kelurahan.id))
    kabupaten = Column(String(25))
    alamat = Column(String(255))
    kodepos = Column(String(5))
    telphone = Column(String(20))
    wpnama = Column(String(50))
    wpalamat = Column(String(255))
    wpkelurahan = Column(String(25))
    wpkecamatan = Column(String(25))
    wpkabupaten = Column(String(25))
    wptelp = Column(String(20))
    wpkodepos = Column(String(5))
    pnama = Column(String(50))
    palamat = Column(String(255))
    pkelurahan = Column(String(25))
    pkecamatan = Column(String(25))
    pkabupaten = Column(String(25))
    ptelp = Column(String(20))
    pkodepos = Column(String(5))
    ijin1 = Column(String(100))
    ijin1no = Column(String(100))
    ijin1tgl = Column(DateTime)
    ijin1tglakhir = Column(DateTime)
    ijin2 = Column(String(100))
    ijin2no = Column(String(100))
    ijin2tgl = Column(DateTime)
    ijin2tglakhir = Column(DateTime)
    ijin3 = Column(String(100))
    ijin3no = Column(String(100))
    ijin3tgl = Column(DateTime)
    ijin3tglakhir = Column(DateTime)
    ijin4 = Column(String(100))
    ijin4no = Column(String(100))
    ijin4tgl = Column(DateTime)
    ijin4tglakhir = Column(DateTime)
    kukuhno = Column(String(30))
    kukuhnip = Column(Integer)
    kukuhtgl = Column(DateTime)
    kukuh_jabat_id = Column(Integer)
    kukuhprinted = Column(Integer)
    enabled = Column(Integer)
    create_date = Column(DateTime)
    create_uid = Column(Integer)
    write_date = Column(DateTime)
    write_uid = Column(Integer)
    tmt = Column(DateTime)
    customer_status_id = Column(Integer)
    kembalitgl = Column(DateTime)
    kembalioleh = Column(String(30))
    kartuprinted = Column(Integer)
    kembalinip = Column(Integer)
    penerimanm = Column(String(50))
    penerimaalamat = Column(String(50))
    penerimatgl = Column(DateTime)
    catatnip = Column(Integer)
    kirimtgl = Column(DateTime)
    batastgl = Column(DateTime)
    petugas_jabat_id = Column(Integer)
    pencatat_jabat_id = Column(Integer)
    kd_restojmlmeja = Column(Integer)
    kd_restojmlkursi = Column(Integer)
    kd_restojmltamu = Column(Integer)
    kd_filmkursi = Column(Integer)
    kd_filmpertunjukan = Column(Integer)
    kd_filmtarif = Column(Float)
    kd_bilyarmeja = Column(Integer)
    kd_bilyartarif = Column(Float)
    kd_bilyarkegiatan = Column(Integer)
    kd_diskopengunjung = Column(Integer)
    kd_diskotarif = Column(Float)
    kd_waletvolume = Column(Integer)
    __table_args__ = (
        UniqueConstraint('rp', 'pb', 'formno', 'kecamatan_id', 'kelurahan_id'),
        dict(schema='pad'))


class CustomerUsaha(Base, CommonModel):
    __tablename__ = 'pad_customer_usaha'
    id = Column(Integer, primary_key=True)
    konterid = Column(Integer, nullable=False)
    reg_date = Column(DateTime)
    customer_id = Column(Integer, ForeignKey(Customer.id), nullable=False)
    usaha_id = Column(Integer, ForeignKey(Usaha.id), nullable=False)
    so = Column(String(1))
    kecamatan_id = Column(Integer, ForeignKey(Kecamatan.id))
    kelurahan_id = Column(Integer, ForeignKey(Kelurahan.id))
    notes = Column(String(50))
    enabled = Column(Integer)
    create_date = Column(DateTime)
    create_uid = Column(Integer)
    write_date = Column(DateTime)
    write_uid = Column(Integer)
    customer_status_id = Column(Integer)
    aktifnotes = Column(String(200))
    tmt = Column(DateTime)
    air_zona_id = Column(Integer)
    air_manfaat_id = Column(Integer)
    def_pajak_id = Column(Integer)
    opnm = Column(String(100))
    opalamat = Column(String(100))
    latitude = Column(Float)
    longitude = Column(Float)
    npwpd_old = Column(String(50))
    petugas_jabat_id = Column(Integer)
    __table_args__ = (
        UniqueConstraint('konterid', 'customer_id', 'usaha_id'),
        dict(schema='pad'))


class SptType(Base, CommonModel):
    __tablename__ = 'pad_spt_type'
    id = Column(Integer, primary_key=True)
    typenm = Column(String(20), nullable=False)
    tmt = Column(DateTime)
    enabled = Column(Integer)
    create_date = Column(DateTime)
    create_uid = Column(Integer)
    write_date = Column(DateTime)
    write_uid = Column(Integer)
    __table_args__ = (
        dict(schema='pad'),)


class Invoice(Base, CommonModel):
    __tablename__ = 'pad_spt'
    id = Column(Integer, primary_key=True)
    tahun = Column(Integer, nullable=False)
    sptno = Column(Integer, nullable=False)
    customer_id = Column(Integer, ForeignKey(Customer.id), nullable=False)
    customer_usaha_id = Column(
        Integer, ForeignKey(CustomerUsaha.id), nullable=False)
    rekening_id = Column(Integer, ForeignKey(Rekening.id))
    pajak_id = Column(Integer, ForeignKey(Pajak.id), nullable=False)
    type_id = Column(Integer, ForeignKey(SptType.id))
    so = Column(String(1), nullable=False)
    masadari = Column(DateTime, nullable=False)
    masasd = Column(DateTime, nullable=False)
    jatuhtempotgl = Column(DateTime)
    r_bayarid = Column(Integer)
    minomset = Column(Float)
    dasar = Column(Float, nullable=False)
    tarif = Column(Float, nullable=False)
    denda = Column(Float)
    bunga = Column(Float, nullable=False)
    setoran = Column(Float)
    kenaikan = Column(Float, nullable=False)
    kompensasi = Column(Float)
    lain2 = Column(Float, nullable=False)
    pajak_terhutang = Column(Integer, nullable=False)
    air_manfaat_id = Column(Integer)
    air_zona_id = Column(Integer)
    meteran_awal = Column(Integer)
    meteran_akhir = Column(Integer)
    volume = Column(Integer)
    satuan = Column(Text)
    r_panjang = Column(Float)
    r_lebar = Column(Float)
    r_muka = Column(Float)
    r_banyak = Column(Float)
    r_luas = Column(Float)
    r_tarifid = Column(Integer)
    r_kontrak = Column(Float)
    r_lama = Column(Integer)
    r_jalan_id = Column(Integer)
    r_jalanklas_id = Column(Integer)
    r_lokasi = Column(String(250))
    r_judul = Column(String(200))
    r_kelurahan_id = Column(Integer)
    r_lokasi_id = Column(Integer)
    r_calculated = Column(Float)
    r_nsr = Column(Float)
    r_nsrno = Column(String(30))
    r_nsrtgl = Column(DateTime)
    r_nsl_kecamatan_id = Column(Integer)
    r_nsl_type_id = Column(Integer)
    r_nsl_nilai = Column(Float)
    notes = Column(String(255))
    unit_id = Column(Integer)
    enabled = Column(Integer)
    create_date = Column(DateTime)
    create_uid = Column(Integer)
    write_date = Column(DateTime)
    write_uid = Column(Integer)
    terimanip = Column(String(50))
    terimatgl = Column(DateTime, nullable=False)
    kirimtgl = Column(DateTime)
    isprint_dc = Column(Boolean)
    r_nsr_id = Column(Integer)
    r_lokasi_pasang_id = Column(Integer)
    r_lokasi_pasang_val = Column(Float)
    r_jalanklas_val = Column(Float)
    r_sudut_pandang_id = Column(Integer)
    r_sudut_pandang_val = Column(Float)
    r_tinggi = Column(Float)
    r_njop = Column(Float)
    r_status = Column(String(20))
    r_njop_ketinggian = Column(Float)
    status_pembayaran = Column(Integer, nullable=False)
    rek_no_paneng = Column(String(50))
    sptno_lengkap = Column(String(20))
    sptno_lama = Column(Integer)
    r_nama = Column(String(100))
    r_alamat = Column(String(255))
    kd_restojmlmeja = Column(Integer)
    kd_restojmlkursi = Column(Integer)
    kd_restojmltamu = Column(Integer)
    kd_filmkursi = Column(Integer)
    kd_filmpertunjukan = Column(Integer)
    kd_filmtarif = Column(Float)
    kd_bilyarmeja = Column(Integer)
    kd_bilyartarif = Column(Float)
    kd_bilyarkegiatan = Column(Integer)
    kd_diskopengunjung = Column(Integer)
    kd_diskotarif = Column(Float)
    kd_waletvolume = Column(Integer)
    kd_park_roda2_luas = Column(Integer)
    kd_park_roda2_jumlah = Column(Integer)
    kd_park_roda2_tarif1 = Column(Integer)
    kd_park_roda2_tarif2 = Column(Integer)
    kd_park_roda2_tarif3 = Column(Integer)
    kd_park_roda4_luas = Column(Integer)
    kd_park_roda4_jumlah = Column(Integer)
    kd_park_roda4_tarif1 = Column(Integer)
    kd_park_roda4_tarif2 = Column(Integer)
    kd_park_roda4_tarif3 = Column(Integer)
    kd_park_rodax_luas = Column(Integer)
    kd_park_rodax_jumlah = Column(Integer)
    kd_park_rodax_tarif1 = Column(Integer)
    kd_park_rodax_tarif2 = Column(Integer)
    kd_park_rodax_tarif3 = Column(Integer)
    file_attachment = Column(Integer)
    dt_hot_pembukuan = Column(Integer)
    dt_hot_kas_register = Column(Integer)
    dt_res_kas_register = Column(Integer)
    dt_res_pembukuan = Column(Integer)
    dt_hib_kas_register = Column(Integer)
    dt_hib_pembukuan = Column(Integer)
    dt_hib_meja_mesin = Column(Integer)
    dt_hib_kamar = Column(Integer)
    dt_hib_karcis_bebas = Column(Integer)
    dt_hib_karcis_mesin = Column(Integer)
    dt_hib_pertunjukan_hari_biasa = Column(Integer)
    dt_hib_pertunjukan_hari_libur = Column(Integer)
    dt_hib_pengunjung_hari_biasa = Column(Integer)
    dt_hib_pengunjung_hari_libur = Column(Integer)
    dt_par_kas_register = Column(Integer)
    dt_par_pembukuan = Column(Integer)
    r_iprno = Column(String(30))
    r_iprtgl = Column(DateTime)
    r_iprid = Column(Integer)
    r_kecamatan_id = Column(Integer)
    m_tonase = Column(Float)
    m_njop = Column(Float)
    r_njop_lain = Column(Float)
    m_tonase_sdh_byr = Column(Float)
    m_karcis_sdh_byr = Column(Float)
    m_dasar_sdh_byr = Column(Float)
    multiple = Column(Integer)
    abt_tarif = Column(Float)
    abt_calculated = Column(Float)
    nama_lainnya = Column(String(250))
    __table_args__ = (
        UniqueConstraint('tahun', 'sptno', 'customer_usaha_id', 'masadari'),
        UniqueConstraint('tahun', 'sptno'),
        dict(schema='pad'))


class Payment(Base, CommonModel):
    __tablename__ = 'pad_sspd'
    id = Column(Integer, primary_key=True)
    tahun = Column(Integer, nullable=False)
    sspdno = Column(Integer, nullable=False)
    sspdtgl = Column(DateTime, nullable=False)
    spt_id = Column(Integer, ForeignKey(Invoice.id), nullable=False)
    bunga = Column(Float)
    bulan_telat = Column(Integer)
    hitung_bunga = Column(Integer)
    printed = Column(Integer)
    enabled = Column(Integer)
    create_date = Column(DateTime)
    create_uid = Column(Integer)
    write_date = Column(DateTime)
    write_uid = Column(Integer)
    sspdjam = Column(Time)
    tp_id = Column(Integer)
    is_validated = Column(Integer)
    keterangan = Column(String(255))
    denda = Column(Integer)
    jml_bayar = Column(Integer)
    is_valid = Column(Integer)
    cancel_jml_bayar = Column(Integer)
    cancel_bunga = Column(Integer)
    cancel_denda = Column(Integer)
    cancel_date = Column(DateTime)
    cancel_uid = Column(Integer)
    __table_args__ = (
        UniqueConstraint('tahun', 'sspdno'),
        dict(schema='pad'))


class Channel(Base, BaseModel):
    __tablename__ = 'pad_channel'
    nama = Column(String(20), nullable=False, unique=True)


class Bank(Base, BaseModel):
    __tablename__ = 'pad_tp'  # Tempat Pembayaran
    singkatan = Column(String(16), nullable=False, unique=True)
    nama = Column(String(32), nullable=False, unique=True)


class IsoPayment(Base, BaseModel):
    __tablename__ = 'pad_payment'
    id = Column(BigInteger, primary_key=True)
    sspd_id = Column(BigInteger, nullable=False)
    tgl = Column(DateTime(timezone=True), nullable=False, default=create_now)
    iso_request = Column(String(1024), nullable=False) # Untuk reversal
    transmission = Column(DateTime(timezone=True), nullable=False)
    settlement = Column(Date, nullable=False)
    stan = Column(Integer, nullable=False)
    invoice_no = Column(String(32), nullable=False)
    invoice_id = Column(BigInteger, nullable=False)
    ntb = Column(String(64), nullable=False)
    ntp = Column(String(32), nullable=False, unique=True)
    bank_id = Column(Integer, ForeignKey(Bank.id), nullable=False)
    channel_id = Column(Integer, ForeignKey(Channel.id), nullable=False)
    bank_ip = Column(String(15), nullable=False)


class IsoReversal(Base, BaseModel):
    __tablename__ = 'pad_reversal'
    id = Column(Integer, ForeignKey(Payment.id), primary_key=True)
    tgl = Column(DateTime(timezone=True), nullable=False, default=create_now)
