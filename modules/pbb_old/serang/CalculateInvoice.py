import sys
sys.path[0:0] = ['/usr/share/opensipkd/modules']
from base_models import DBSession
from datetime import (
    datetime,
    date,
    )
from sqlalchemy import func
from models import (
    Invoice,
    Pembayaran,
    )
sys.path[0:0] = ['/etc/opensipkd']
from pbb_conf import persen_denda


def query_sppt(propinsi, kabupaten, kecamatan, kelurahan, blok, urut,
        jenis, tahun):
    return DBSession.query(Invoice).filter_by(
                kd_propinsi=propinsi,
                kd_dati2=kabupaten,
                kd_kecamatan=kecamatan,
                kd_kelurahan=kelurahan,
                kd_blok=blok,
                no_urut=urut,
                kd_jns_op=jenis,
                thn_pajak_sppt=tahun)


class CalculateInvoice(object):
    def __init__(self, propinsi, kabupaten, kecamatan, kelurahan, blok, urut,
                 jenis, tahun):
        self.propinsi = propinsi
        self.kabupaten = kabupaten
        self.kecamatan = kecamatan
        self.kelurahan = kelurahan
        self.blok = blok
        self.urut = urut
        self.jenis = jenis
        self.tahun = tahun
        q = query_sppt(propinsi, kabupaten, kecamatan, kelurahan, blok, urut,
                jenis, tahun)
        self.invoice = q.first()
        if self.invoice:
            self.hitung()
            self.paid = self.is_paid()

    def hitung(self):
        bayar = DBSession.query(
                    func.sum(Pembayaran.jml_sppt_yg_dibayar).\
                         label('jml_sppt_yg_dibayar'),
                    func.sum(Pembayaran.denda_sppt).\
                         label('denda_sppt')).\
                    filter_by(kd_propinsi=self.invoice.kd_propinsi,
                              kd_dati2=self.invoice.kd_dati2,
                              kd_kecamatan=self.invoice.kd_kecamatan,
                              kd_kelurahan=self.invoice.kd_kelurahan,
                              kd_blok=self.invoice.kd_blok,
                              no_urut=self.invoice.no_urut,
                              kd_jns_op=self.invoice.kd_jns_op,
                              thn_pajak_sppt=self.invoice.thn_pajak_sppt).one()
        jml_bayar = bayar.jml_sppt_yg_dibayar or 0
        denda_lalu = bayar.denda_sppt or 0
        self.tagihan = self.invoice.pbb_yg_harus_dibayar_sppt - \
                        (jml_bayar - denda_lalu)
        self.tagihan = int(round(float(self.tagihan)))
        self.denda = self.hitung_denda()
        self.total = self.tagihan + self.denda

    def hitung_denda(self):
        self.bln_tunggakan = 0 
        jatuh_tempo = self.invoice.tgl_jatuh_tempo_sppt
        if type(jatuh_tempo) is not date:
            jatuh_tempo = jatuh_tempo.date()
        self.kini = kini = datetime.now()
        if jatuh_tempo >= kini.date():
            return 0
        x = (kini.year - jatuh_tempo.year) * 12
        y = kini.month - jatuh_tempo.month
        self.bln_tunggakan = x + y + 1
        if kini.day <= jatuh_tempo.day:
            self.bln_tunggakan -= 1
        if self.bln_tunggakan < 1:
            self.bln_tunggakan = 0
        if self.bln_tunggakan > 24:
            self.bln_tunggakan = 24
        denda = self.bln_tunggakan * persen_denda / 100 * self.tagihan
        return int(round(denda))

    def is_paid(self):
        return self.invoice.status_pembayaran_sppt == '1'
