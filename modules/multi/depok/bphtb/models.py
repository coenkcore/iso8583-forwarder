from base_models import CommonModel 
from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    Float,
    String,
    Date,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    Sequence,
    )


class Models(object):
    def __init__(self, Base):
        # Jenis Transaksi, pbb=1, bphtb=2, dst 
        class PajakSource(Base, CommonModel):
            __tablename__ = 'pajak_source'
            id  = Column(Integer, primary_key=True)
            nama = Column(String(20), nullable=False, unique=True)

        class Invoice(Base, CommonModel):
            __tablename__ = 'pajak_invoice'
            id  = Column(Integer, primary_key=True)
            source_id = Column(Integer, ForeignKey('pajak_source.id'), nullable=False)
            tahun = Column(Integer, nullable=False)
            no_tagihan = Column(String(30), nullable=False) # pemda invoice
            tgl = Column(DateTime, nullable=False)
            jatuh_tempo = Column(DateTime, nullable=False)
            jml_tagihan = Column(Float, nullable=False, default=0)
            status_bayar = Column(Integer, nullable=False, default=0) # 0, 1
            # informasi tambahan sesuai kebutuhan dimana akan ada beberapa perbedaan untuk setiap jenis pajak
            nop = Column(String(35)) # kompatibilitas semua pajak NOP/NOPD/NPWPD
            npop_omset = Column(Float, nullable=False, default=0) # NPOP/NJOP
            persen_pajak = Column(Float, nullable=False, default=0) # persen (/100) pajak
            kd_rekening = Column(String(15)) # kompatibilitas ke pajak lainnya
            nm_rekening = Column(String(50)) # kompatibilitas ke pajak lainnya
            nama_wp = Column(String(50))
            npwp_wp = Column(String(15))
            alamat_wp = Column(String(50))
            rt_wp = Column(String(3))
            rw_wp = Column(String(3))
            kelurahan_wp = Column(String(25))
            kecamatan_wp = Column(String(25))
            kota_wp = Column(String(25))
            kodepos_wp = Column(String(5))
            nama_op = Column(String(50)) # diisi nama wp apabila tidak ada. kompatibiltas ke pad lainnya
            alamat_op = Column(String(50))
            rt_op = Column(String(3))
            rw_op = Column(String(3))
            kelurahan_op = Column(String(25))
            kecamatan_op = Column(String(25))
            kota_op = Column(String(25))
            kodepos_op = Column(String(5))
            # informasi khusus bphtb
            luas_bumi = Column(Float, nullable=False, default=0)
            luas_bng = Column(Float, nullable=False, default=0)
            # npoptkp = Column(Float, nullable=False) # harga_tran
            kd_bphtb = Column(String(2), nullable=False, default='00') # kd_jphtb
            # faktor_pengurang  = Column(Float, nullable=False, default=0)
            nm_notaris = Column(String(40))
            jenis = Column(Integer, default=1) # 1: normal bayar, 2: kurang bayar
            # Catatan YM aa.gustiana 18-07-2013:
            # Column jenis akan digunakan untuk update bookppat (1) dan t_bank_kb (2)
            __table_args__ = (
                UniqueConstraint('source_id', 'tahun', 'no_tagihan'),
                )
        self.Invoice = Invoice
 

        # Jalur Transaksi
        class Channel(Base, CommonModel):
            __tablename__ = 'channel'
            id = Column(Integer, primary_key=True)
            nama = Column(String(20), nullable=False, unique=True)


        class Bank(Base, CommonModel):
            __tablename__ = 'bank'
            id = Column(Integer, primary_key=True)
            singkatan = Column(String(16), nullable=False, unique=True)
            nama = Column(String(30), nullable=False, unique=True)


        class Payment(Base, CommonModel):
            __tablename__ = 'pajak_payment'
            id  = Column(Integer, primary_key=True)
            source_id = Column(Integer, ForeignKey('pajak_source.id'), nullable=False)
            ntp = Column(String(30), nullable=False) # Nomor Transaksi Pemda
            ntb = Column(String(30), nullable=False) # Nomor Transaksi Bank
            channel_id = Column(Integer, ForeignKey('channel.id'), nullable=False)
            tahun = Column(Integer, nullable=False)
            # Untuk BPHTB Self Payment no_tagihan diisi oleh NTP saja
            no_tagihan = Column(String(30), nullable=False)
            pembayaran_ke = Column(Integer, nullable=False, default=1)
            # Pembayaran
            tgl_bayar = Column(DateTime, nullable=False)
            denda = Column(Float, nullable=False, default=0)
            jml_bayar = Column(Float, nullable=False, default=0)
            # Wajib pajak
            nama_wp = Column(String(50))
            npwp_wp = Column(String(15))
            alamat_wp = Column(String(50))
            rt_wp = Column(String(3))
            rw_wp = Column(String(3))
            kelurahan_wp = Column(String(25))
            kecamatan_wp = Column(String(25))
            kota_wp = Column(String(25))
            kodepos_wp = Column(String(5))
            # Objek pajak
            nama_op = Column(String(50)) # Diisi nama_wp apabila tidak ada
            alamat_op = Column(String(50))
            rt_op = Column(String(3))
            rw_op = Column(String(3))
            kelurahan_op = Column(String(25))
            kecamatan_op = Column(String(25))
            kota_op = Column(String(25))
            kodepos_op = Column(String(5))
            # Khusus PBB / BPHTB 
            luas_bumi = Column(Float, nullable=False, default=0)
            luas_bng = Column(Float, nullable=False, default=0)
            # Bank
            bank_id = Column(Integer, ForeignKey('bank.id'), nullable=False)
            nm_kcp_bank = Column(String(30))
            operators = Column(String(30))
            kode_bank = Column(String(3))
            kd_kanwil_bank = Column(String(2), nullable=False)
            kd_kppbb_bank = Column(String(2), nullable=False)
            kd_bank_tunggal = Column(String(2), nullable=False)
            kd_bank_persepsi = Column(String(2), nullable=False)
            kd_tp = Column(String(2), nullable=False)
            # Invoice ?
            invoice_id = Column(Integer, ForeignKey('pajak_invoice.id'))
            tgl_invoice = Column(DateTime)
            jatuh_tempo = Column(DateTime)
            jml_tagihan = Column(Float, nullable=False, default=0)
            # Informasi tambahan sesuai kebutuhan dimana akan ada beberapa perbedaan 
            # untuk setiap jenis pajak
            nop = Column(String(35)) # kompatibilitas semua pajak NOP/NOPD/NPWPD
            npop_omset = Column(Float, nullable=False, default=0) # NPOP/NJOP
            persen_pajak = Column(Float, nullable=False, default=0) # persen (/100) pajak
            kd_rekening = Column(String(15)) # kompatibilitas ke pajak lainnya
            nm_rekening = Column(String(50)) # kompatibilitas ke pajak lainnya
            # npoptkp = Column(Float, nullable=False) # harga_tran
            kd_bphtb = Column(String(2), nullable=False, default='00') # kd_jphtb
            # faktor_pengurang = Column(Float, nullable=False, default=0)
            nm_notaris = Column(String(40))
            __table_args__ = (
                UniqueConstraint('source_id', 'tahun', 'no_tagihan', 'pembayaran_ke'),
                UniqueConstraint('source_id', 'ntp'),
                )
        self.Payment = Payment
 

        ############
        # ISO 8583 #
        ############
        class IsoInquiry(Base, CommonModel):
            __tablename__ = 'iso_inquiry'
            id  = Column(Integer, primary_key=True)
            tgl = Column(DateTime, default=datetime.now, nullable=False)
            invoice_id = Column(Integer, ForeignKey('pajak_invoice.id'), nullable=False)
            transmission = Column(DateTime, nullable=False)
            stan = Column(Integer, nullable=False)
            settlement = Column(Date, nullable=False)
            bank_id = Column(Integer, ForeignKey('bank.id'), nullable=False) 
            channel_id = Column(Integer, ForeignKey('channel.id'), nullable=False) 
        self.IsoInquiry = IsoInquiry


        self.iso_payment_seq = Sequence('iso_payment_id_seq')

        class IsoPayment(Base, CommonModel):
            __tablename__ = 'iso_payment'
            id = Column(Integer, self.iso_payment_seq, primary_key=True) 
            tgl = Column(DateTime, default=datetime.now, nullable=False)
            iso_request = Column(String(1024), nullable=False) # Untuk reversal
            payment_id = Column(Integer, ForeignKey('pajak_payment.id'),
                            nullable=False)
            transmission = Column(DateTime, nullable=False)
            stan = Column(Integer, nullable=False)
            settlement = Column(Date, nullable=False)
            inquiry_id = Column(Integer, ForeignKey('iso_inquiry.id'))
        self.IsoPayment = IsoPayment


        class IsoReversal(Base, CommonModel):
            __tablename__ = 'iso_reversal'
            id  = Column(Integer, primary_key=True)
            payment_id = Column(Integer, ForeignKey('iso_payment.id'),
                            nullable=False, unique=True)
            tgl = Column(DateTime, default=datetime.now, nullable=False)
            iso_request = Column(String(1024), nullable=False)
        self.IsoReversal = IsoReversal
