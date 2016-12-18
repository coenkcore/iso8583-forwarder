from sqlalchemy import create_engine
from tools import FixLength
from base_models import (
    Base,
    DBSession,
    )
from sismiop.query import Query
from common.pbb.models import Models
from common.pbb.structure import INVOICE_ID
from conf import db_url


engine = create_engine(db_url)
Base.metadata.bind = engine
DBSession.configure(bind=engine)
models = Models(Base, None, None)

class InquiryByQuery(Query):
    def __init__(self, invoice_id_raw):
        Query.__init__(self, models, DBSession)
        self.invoice_id = FixLength(INVOICE_ID)
        self.invoice_id.set_raw(invoice_id_raw)
        q = self.query_invoice(self.invoice_id['Propinsi'],
                self.invoice_id['Kabupaten'], self.invoice_id['Kecamatan'],
                self.invoice_id['Kelurahan'], self.invoice_id['Blok'],
                self.invoice_id['Urut'], self.invoice_id['Jenis'],
                self.invoice_id['Tahun Pajak'])
        self.invoice = q.first()
        self.ket = None
        if not self.invoice:
            return
        self.nama_wp = self.invoice.nm_wp_sppt
        self.payment = self.invoice2payment(self.invoice)
        if self.payment:
            self.total = self.payment.jml_sppt_yg_dibayar
            self.tgl_bayar = self.payment.tgl_rekam_byr_sppt
            self.ket = 'pembayaran ke {n}'.format(n=self.payment.pembayaran_sppt_ke)
            q = DBSession.query(models.TempatPembayaran).filter_by(
                kd_kanwil=self.payment.kd_kanwil_bank,
                kd_kppbb=self.payment.kd_kppbb_bank,
                kd_bank_tunggal=self.payment.kd_bank_tunggal,
                kd_bank_persepsi=self.payment.kd_bank_persepsi,
                kd_tp=self.payment.kd_tp)
            tp = q.first()
            self.tempat_pembayaran = dict()
            if tp:
                self.tempat_pembayaran['nama'] = tp.nm_tp
                alamat = tp.alamat_tp and tp.alamat_tp.strip()
                if alamat:
                    self.tempat_pembayaran['alamat'] = alamat
        self.h2h = self.invoice2iso_pay()

    def invoice2iso_pay(self):
        q = DBSession.query(models.Payment).filter_by(
                propinsi=self.invoice.kd_propinsi,
                kabupaten=self.invoice.kd_dati2,
                kecamatan=self.invoice.kd_kecamatan,
                kelurahan=self.invoice.kd_kelurahan,
                blok=self.invoice.kd_blok,
                urut=self.invoice.no_urut,
                jenis=self.invoice.kd_jns_op,
                tahun=self.invoice.thn_pajak_sppt).order_by(
                models.Payment.ke)
        r = []
        for iso_pay in q:
            q_inq = DBSession.query(models.Inquiry).filter_by(
                    id=iso_pay.inquiry_id)
            iso_inq = q_inq.first()
            total = iso_inq.tagihan + iso_inq.denda
            ket = 'Pembayaran ke {k}'.format(k=iso_pay.ke)
            d = dict(ket=ket, tgl=iso_inq.tgl, total=total)
            r.append(d)
        return r
