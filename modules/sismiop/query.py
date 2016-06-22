from datetime import (
    datetime,
    date,
    )
from sqlalchemy import func
from tools import (
    hitung_denda,
    sppt2nop,
    )
 

class Query(object):
    def __init__(self, models, DBSession):
        self.models = models
        self.DBSession = DBSession

    def query_sppt(self, propinsi, kabupaten, kecamatan, kelurahan, blok, urut,
        jenis, tahun):
        return self.DBSession.query(self.models.Invoice).filter_by(
                kd_propinsi=propinsi, kd_dati2=kabupaten,
                kd_kecamatan=kecamatan, kd_kelurahan=kelurahan, kd_blok=blok,
                no_urut=urut, kd_jns_op=jenis, thn_pajak_sppt=tahun)

    def query_pembayaran(self, propinsi, kabupaten, kecamatan, kelurahan, blok, urut,
        jenis, tahun):
        return self.DBSession.query(self.models.Pembayaran).filter_by(
                kd_propinsi=propinsi, kd_dati2=kabupaten,
                kd_kecamatan=kecamatan, kd_kelurahan=kelurahan, kd_blok=blok,
                no_urut=urut, kd_jns_op=jenis, thn_pajak_sppt=tahun)

    def pay2bayar(self, pay):
        q = self.query_pembayaran(pay.propinsi, pay.kabupaten, pay.kecamatan,
                pay.kelurahan, pay.blok, pay.urut, pay.jenis, str(pay.tahun))
        q = q.filter_by(pembayaran_sppt_ke=pay.ke)
        return q.first()

    def pay2sppt(self, pay):
        q = self.query_sppt(pay.propinsi, pay.kabupaten, pay.kecamatan, pay.kelurahan,
                pay.blok, pay.urut, pay.jenis, str(pay.tahun))
        return q.first()

    def cari_kelurahan(self, propinsi, kabupaten, kecamatan, kelurahan):
        q = self.DBSession.query(self.models.Kelurahan).filter_by(kd_propinsi=propinsi,
                kd_dati2=kabupaten, kd_kecamatan=kecamatan,
                kd_kelurahan=kelurahan)
        r = q.first()
        return r and r.nm_kelurahan or ''

    def cari_kecamatan(self, propinsi, kabupaten, kecamatan):
        q = self.DBSession.query(self.models.Kecamatan).filter_by(kd_propinsi=propinsi,
                kd_dati2=kabupaten, kd_kecamatan=kecamatan)
        r = q.first()
        return r and r.nm_kecamatan or ''

    def cari_propinsi(self, propinsi):
        q = self.DBSession.query(self.models.Propinsi).filter_by(kd_propinsi=propinsi)
        r = q.first()
        return r and r.nm_propinsi or ''

    def invoice2inquiry(self, sppt):
        q = self.DBSession.query(self.models.Inquiry).filter_by(propinsi=sppt.kd_propinsi,
                kabupaten=sppt.kd_dati2, kecamatan=sppt.kd_kecamatan,
                kelurahan=sppt.kd_kelurahan, blok=sppt.kd_blok,
                urut=sppt.no_urut, jenis=sppt.kd_jns_op,
                tahun=sppt.thn_pajak_sppt)
        q = q.order_by(self.models.Inquiry.id.desc())
        return q.first()

    def invoice2payment(self, sppt):
        q = self.DBSession.query(self.models.Payment).filter_by(propinsi=sppt.kd_propinsi,
                kabupaten=sppt.kd_dati2, kecamatan=sppt.kd_kecamatan,
                kelurahan=sppt.kd_kelurahan, blok=sppt.kd_blok,
                urut=sppt.no_urut, jenis=sppt.kd_jns_op,
                tahun=sppt.thn_pajak_sppt)
        q = q.order_by(self.models.Payment.ke.desc())
        return q.first()

    def inq2bayar(self, inq):
        q = self.query_pembayaran(inq.propinsi, inq.kabupaten, inq.kecamatan,
                inq.kelurahan, inq.blok, inq.urut, inq.jenis, str(inq.tahun))
        q = q.order_by(self.models.Pembayaran.pembayaran_sppt_ke.desc())
        return q.first()

    def is_paid(self):
        return self.invoice.status_pembayaran_sppt == '1'


class CalculateInvoice(Query):
    def __init__(self, models, DBSession, persen_denda, propinsi, kabupaten,
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
        q = self.query_sppt(propinsi, kabupaten, kecamatan, kelurahan, blok, urut,
                jenis, tahun)
        self.invoice = q.first()
        if self.invoice:
            self.hitung()
            self.paid = self.is_paid()

    def hitung(self):
        q = self.DBSession.query(
                    func.sum(self.models.Pembayaran.jml_sppt_yg_dibayar).\
                         label('jml_sppt_yg_dibayar'),
                    func.sum(self.models.Pembayaran.denda_sppt).\
                         label('denda_sppt')).\
                    filter_by(kd_propinsi=self.invoice.kd_propinsi,
                              kd_dati2=self.invoice.kd_dati2,
                              kd_kecamatan=self.invoice.kd_kecamatan,
                              kd_kelurahan=self.invoice.kd_kelurahan,
                              kd_blok=self.invoice.kd_blok,
                              no_urut=self.invoice.no_urut,
                              kd_jns_op=self.invoice.kd_jns_op,
                              thn_pajak_sppt=self.invoice.thn_pajak_sppt)
        bayar = q.one()
        jml_bayar = bayar.jml_sppt_yg_dibayar or 0
        denda_lalu = bayar.denda_sppt or 0
        sisa = float(jml_bayar - denda_lalu)
        self.tagihan = float(self.invoice.pbb_yg_harus_dibayar_sppt - sisa)
        self.tagihan = int(round(self.tagihan))
        self.denda = self.hitung_denda()
        self.total = self.tagihan + self.denda

    def hitung_denda(self):
        self.kini = date.today()
        self.bln_tunggakan, denda = hitung_denda(self.tagihan,
            self.invoice.tgl_jatuh_tempo_sppt, self.persen_denda, self.kini)
        return int(round(denda))

    def set_paid(self):
        self.invoice.status_pembayaran_sppt = '1' # Lunas

    def create_payment(self, inq, tgl_bayar, bank_fields, nip_pencatat):
        bayar = self.inq2bayar(inq)
        if bayar:
            ke = bayar.pembayaran_sppt_ke + 1
        else:
            ke = 1
        bayar = self.models.Pembayaran()
        bayar.kd_propinsi = inq.propinsi
        bayar.kd_dati2 = inq.kabupaten
        bayar.kd_kecamatan = inq.kecamatan
        bayar.kd_kelurahan = inq.kelurahan
        bayar.kd_blok = inq.blok
        bayar.no_urut = inq.urut
        bayar.kd_jns_op = inq.jenis
        bayar.thn_pajak_sppt = inq.tahun
        bayar.pembayaran_sppt_ke = ke
        bayar.tgl_rekam_byr_sppt = datetime.now()
        bayar.tgl_pembayaran_sppt = tgl_bayar 
        bayar.jml_sppt_yg_dibayar = self.total
        bayar.denda_sppt = inq.denda
        bayar.nip_rekam_byr_sppt = nip_pencatat
        bayar.from_dict(bank_fields)
        self.set_paid()
        self.DBSession.add(self.invoice)
        self.DBSession.add(bayar)
        self.DBSession.flush()
        return bayar, ke

    # Override
    def invoice2payment(self):
        return Query.invoice2payment(self, self.invoice)


############
# Reversal #
############
class ReversalCommon(object):
    def set_unpaid(self):
        self.invoice.status_pembayaran_sppt = '0'
        self.bayar.jml_sppt_yg_dibayar = 0 
        self.bayar.denda_sppt = 0


class PaymentReversal(ReversalCommon, Query):
    def __init__(self, models, DBSession, pay):
        Query.__init__(self, models, DBSession)
        self.pay = pay
        self.bayar = self.pay2bayar(pay)
        if not self.bayar:
            return
        self.invoice = self.pay2sppt(pay)


class ReversalByQuery(ReversalCommon, Query):
    def __init__(self, models, DBSession, invoice_id):
        Query.__init__(self, models, DBSession)
        q = self.query_sppt(invoice_id['Propinsi'], invoice_id['Kabupaten'],
                invoice_id['Kecamatan'], invoice_id['Kelurahan'],
                invoice_id['Blok'], invoice_id['Urut'], invoice_id['Jenis'],
                invoice_id['Tahun Pajak'])
        self.invoice = q.first()
        if not self.invoice:
            return
        q = self.query_pembayaran(invoice_id['Propinsi'],
                invoice_id['Kabupaten'], invoice_id['Kecamatan'],
                invoice_id['Kelurahan'], invoice_id['Blok'], invoice_id['Urut'],
                invoice_id['Jenis'], invoice_id['Tahun Pajak'])
        q = q.order_by(Pembayaran.pembayaran_sppt_ke.desc())
        self.bayar = q.first()
