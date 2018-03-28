from datetime import (
    datetime,
    date,
    )
from sqlalchemy import func
from .db_tools import (
    hitung_denda,
    sppt2nop,
    )
from tools import round_up


class Query(object):
    def __init__(self, models, DBSession):
        self.models = models
        self.DBSession = DBSession

    def query_invoice(
            self, propinsi, kabupaten, kecamatan, kelurahan, blok, urut, jenis,
            tahun):
        return self.DBSession.query(self.models.Invoice).filter_by(
                kd_propinsi=propinsi, kd_dati2=kabupaten,
                kd_kecamatan=kecamatan, kd_kelurahan=kelurahan, kd_blok=blok,
                no_urut=urut, kd_jns_op=jenis, thn_pajak_sppt=tahun)

    def query_payment(
            self, propinsi, kabupaten, kecamatan, kelurahan, blok, urut, jenis,
            tahun):
        return self.DBSession.query(self.models.Pembayaran).filter_by(
                kd_propinsi=propinsi, kd_dati2=kabupaten,
                kd_kecamatan=kecamatan, kd_kelurahan=kelurahan, kd_blok=blok,
                no_urut=urut, kd_jns_op=jenis, thn_pajak_sppt=tahun)

    def invoice2payment(self, inv):
        q = self.query_payment(
                inv.kd_propinsi, inv.kd_dati2, inv.kd_kecamatan,
                inv.kd_kelurahan, inv.kd_blok, inv.no_urut, inv.kd_jns_op,
                inv.thn_pajak_sppt)
        q = q.order_by(self.models.Pembayaran.pembayaran_sppt_ke.desc())
        return q.first()

    def cari_kelurahan(self, propinsi, kabupaten, kecamatan, kelurahan):
        q = self.DBSession.query(self.models.Kelurahan).filter_by(
                kd_propinsi=propinsi, kd_dati2=kabupaten,
                kd_kecamatan=kecamatan, kd_kelurahan=kelurahan)
        r = q.first()
        return r and r.nm_kelurahan or ''

    def cari_kecamatan(self, propinsi, kabupaten, kecamatan):
        q = self.DBSession.query(self.models.Kecamatan).filter_by(
                kd_propinsi=propinsi, kd_dati2=kabupaten,
                kd_kecamatan=kecamatan)
        r = q.first()
        return r and r.nm_kecamatan or ''

    def cari_propinsi(self, propinsi):
        q = self.DBSession.query(self.models.Propinsi).\
                filter_by(kd_propinsi=propinsi)
        r = q.first()
        return r and r.nm_propinsi or ''

    def is_paid(self):
        return self.invoice.status_pembayaran_sppt == '1'


class CalculateInvoice(Query):
    def __init__(
            self, models, DBSession, persen_denda, propinsi, kabupaten,
            kecamatan, kelurahan, blok, urut, jenis, tahun):
        Query.__init__(self, models, DBSession)
        self.persen_denda = persen_denda
        self.propinsi = propinsi
        self.kabupaten = kabupaten
        self.kecamatan = kecamatan
        self.kelurahan = kelurahan
        self.blok = blok
        self.urut = urut
        self.jenis = jenis
        self.tahun = tahun
        self.invoice = self.invoice_tahun(tahun)
        if self.invoice:
            self.hitung()
            self.paid = self.is_paid()

    def invoice_tahun(self, tahun):
        q = self.query_invoice(
                self.propinsi, self.kabupaten, self.kecamatan, self.kelurahan,
                self.blok, self.urut, self.jenis, tahun)
        return q.first()

    def hitung_invoice(self, invoice):
        q = self.DBSession.query(
                    func.sum(self.models.Pembayaran.jml_sppt_yg_dibayar).
                    label('jml_sppt_yg_dibayar'),
                    func.sum(self.models.Pembayaran.denda_sppt).
                    label('denda_sppt')).\
                    filter_by(kd_propinsi=invoice.kd_propinsi,
                              kd_dati2=invoice.kd_dati2,
                              kd_kecamatan=invoice.kd_kecamatan,
                              kd_kelurahan=invoice.kd_kelurahan,
                              kd_blok=invoice.kd_blok,
                              no_urut=invoice.no_urut,
                              kd_jns_op=invoice.kd_jns_op,
                              thn_pajak_sppt=invoice.thn_pajak_sppt)
        bayar = q.first()
        jml_bayar = bayar.jml_sppt_yg_dibayar or 0
        denda_lalu = bayar.denda_sppt or 0
        sisa = float(jml_bayar - denda_lalu)
        tagihan = round_up(invoice.pbb_yg_harus_dibayar_sppt - sisa)
        kini = date.today()
        bln_tunggakan, denda = hitung_denda(
            tagihan, invoice.tgl_jatuh_tempo_sppt, self.persen_denda, kini)
        denda = round_up(denda)
        return tagihan, denda, bln_tunggakan, kini

    def hitung(self):
        self.tagihan, self.denda, self.bln_tunggakan, self.kini = \
            self.hitung_invoice(self.invoice)
        self.total = self.tagihan + self.denda

    def set_paid(self):
        self.invoice.status_pembayaran_sppt = '1'  # Lunas

    def create_payment(self, denda, tgl_bayar, bank_fields, nip_pencatat):
        bayar = self.invoice2payment()
        if bayar:
            ke = bayar.pembayaran_sppt_ke + 1
        else:
            ke = 1
        bayar = self.models.Pembayaran()
        bayar.kd_propinsi = self.invoice.kd_propinsi
        bayar.kd_dati2 = self.invoice.kd_dati2
        bayar.kd_kecamatan = self.invoice.kd_kecamatan
        bayar.kd_kelurahan = self.invoice.kd_kelurahan
        bayar.kd_blok = self.invoice.kd_blok
        bayar.no_urut = self.invoice.no_urut
        bayar.kd_jns_op = self.invoice.kd_jns_op
        bayar.thn_pajak_sppt = self.invoice.thn_pajak_sppt
        bayar.pembayaran_sppt_ke = ke
        bayar.tgl_rekam_byr_sppt = datetime.now()
        bayar.tgl_pembayaran_sppt = tgl_bayar
        bayar.jml_sppt_yg_dibayar = self.total
        bayar.denda_sppt = denda
        bayar.nip_rekam_byr_sppt = nip_pencatat
        bayar.from_dict(bank_fields)
        self.set_paid()
        self.before_save(bayar)
        self.DBSession.add(self.invoice)
        self.DBSession.add(bayar)
        self.DBSession.flush()
        return bayar, ke

    def before_save(self, bayar):
        pass

    # Override
    def invoice2payment(self):
        return Query.invoice2payment(self, self.invoice)


############
# Reversal #
############
class Reversal(Query):
    def __init__(
            self, models, DBSession, propinsi, kabupaten, kecamatan, kelurahan,
            blok, urut, jenis, tahun):
        Query.__init__(self, models, DBSession)
        q = self.query_invoice(
                propinsi, kabupaten, kecamatan, kelurahan, blok, urut, jenis,
                tahun)
        self.invoice = q.first()
        if not self.invoice:
            return
        self.payment = self.invoice2payment()

    def invoice2payment(self):
        return Query.invoice2payment(self, self.invoice)

    def set_unpaid(self):
        self.invoice.status_pembayaran_sppt = '0'
        self.DBSession.add(self.invoice)
        if self.payment:
            self.payment.jml_sppt_yg_dibayar = 0
            self.payment.denda_sppt = 0
            self.DBSession.add(self.payment)
        self.DBSession.flush()
        return self.payment
