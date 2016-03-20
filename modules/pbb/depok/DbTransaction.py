import sys
from datetime import datetime
sys.path[0:0] = ['/usr/share/opensipkd/modules']
from base_models import DBSession
sys.path[0:0] = ['/etc/opensipkd']
from pbb_conf import (
    persen_denda,
    nip_rekam_byr_sppt,
    )
sys.path[0:0] = ['/usr/share/opensipkd-forwarder/modules/pbb']
from pbb_db_transaction import (
    BaseDbTransaction,
    inquiry_id,
    )
from pbb_models import (
    Inquiry,
    Payment,
    Reversal,
    )
from models import (
    Invoice,
    Pembayaran,
    Kelurahan,
    Kecamatan,
    Kabupaten,
    Propinsi,
    )
from CalculateInvoice import (
    CalculateInvoice,
    query_sppt,
    )
from PaymentReversal import PaymentReversal
from DbTools import query_pembayaran


def cari_kelurahan(propinsi, kabupaten, kecamatan, kelurahan):
    q = DBSession.query(Kelurahan).filter_by(
            kd_propinsi=propinsi,
            kd_dati2=kabupaten,
            kd_kecamatan=kecamatan,
            kd_kelurahan=kelurahan)
    r = q.first()
    return r and r.nm_kelurahan or ''

def cari_kecamatan(propinsi, kabupaten, kecamatan):
    q = DBSession.query(Kecamatan).filter_by(
            kd_propinsi=propinsi,
            kd_dati2=kabupaten,
            kd_kecamatan=kecamatan)
    r = q.first()
    return r and r.nm_kecamatan or ''

def cari_propinsi(propinsi):
    q = DBSession.query(Propinsi).filter_by(kd_propinsi=propinsi)
    r = q.first()
    return r and r.nm_propinsi or ''

def sppt2nop(sppt):
    return sppt.kd_propinsi + sppt.kd_dati2 + sppt.kd_kecamatan + \
           sppt.kd_kelurahan + sppt.kd_blok + sppt.no_urut + sppt.kd_jns_op

def nama_jalan_op(sppt):
    return sppt.jln_wp_sppt

def invoice2inquiry(sppt):
    q = DBSession.query(Inquiry).filter_by(
            propinsi=sppt.kd_propinsi,
            kabupaten=sppt.kd_dati2,
            kecamatan=sppt.kd_kecamatan,
            kelurahan=sppt.kd_kelurahan,
            blok=sppt.kd_blok,
            urut=sppt.no_urut,
            jenis=sppt.kd_jns_op,
            tahun=sppt.thn_pajak_sppt)
    return q.order_by('id DESC').first()

def invoice2payment(sppt):
    q = DBSession.query(Payment).filter_by(
            propinsi=sppt.kd_propinsi,
            kabupaten=sppt.kd_dati2,
            kecamatan=sppt.kd_kecamatan,
            kelurahan=sppt.kd_kelurahan,
            blok=sppt.kd_blok,
            urut=sppt.no_urut,
            jenis=sppt.kd_jns_op,
            tahun=sppt.thn_pajak_sppt)
    return q.order_by('ke DESC').first()

def inq2bayar(inq):
    q = query_pembayaran(inq.propinsi, inq.kabupaten, inq.kecamatan,
            inq.kelurahan, inq.blok, inq.urut, inq.jenis, str(inq.tahun))
    q = q.order_by('pembayaran_sppt_ke DESC')
    return q.first()

def pay2invoice_id(pay):
    return ''.join([pay.propinsi, pay.kabupaten, pay.kecamatan,
        pay.kelurahan, pay.blok, pay.urut, pay.jenis, str(pay.tahun)])


FIELD_BANK = ['kd_kanwil_bank', 'kd_kppbb_bank', 'kd_bank_tunggal',
              'kd_bank_persepsi', 'kd_tp']
FIELD_BANK_NON_TP = FIELD_BANK[:-1]


class DbTransaction(BaseDbTransaction):
    def get_field_bank(self):
        return FIELD_BANK

    def get_field_bank_non_tp(self):
        return FIELD_BANK_NON_TP

    def get_calc_cls(self):
        return CalculateInvoice

    def invoice_id2profile(self):
        nama_kelurahan = self.nama_kelurahan()
        nama_kecamatan = self.nama_kecamatan()
        nama_propinsi = self.nama_propinsi()
        self.invoice_profile.from_dict({
            'Propinsi': self.invoice_id['Propinsi'],
            'Kabupaten': self.invoice_id['Kabupaten'],
            'Kecamatan': self.invoice_id['Kecamatan'],
            'Kelurahan': self.invoice_id['Kelurahan'],
            'Blok': self.invoice_id['Blok'],
            'Urut': self.invoice_id['Urut'],
            'Jenis': self.invoice_id['Jenis'],
            'Tahun Pajak': self.invoice_id['Tahun Pajak'],
            'Nama Kelurahan': nama_kelurahan,
            'Nama Kecamatan': nama_kecamatan,
            'Nama Propinsi': nama_propinsi})

    def sppt2profile(self):
        inv = self.calc.invoice
        self.invoice_profile.from_dict({
            'Nama': inv.nm_wp_sppt,
            'Luas Tanah': int(inv.luas_bumi_sppt),
            'Luas Bangunan': int(inv.luas_bng_sppt),
            'Lokasi': nama_jalan_op(inv)})

    def create_inquiry(self):
        inv = self.calc.invoice
        bumi = int(inv.luas_bumi_sppt)
        bangunan = int(inv.luas_bng_sppt)
        njop = inv.njop_bumi_sppt + inv.njop_bng_sppt
        nop = sppt2nop(inv)
        inq = Inquiry(nop=nop, propinsi=inv.kd_propinsi, kabupaten=inv.kd_dati2,
                  kecamatan=inv.kd_kecamatan, kelurahan=inv.kd_kelurahan,
                  blok=inv.kd_blok, urut=inv.no_urut, jenis=inv.kd_jns_op,
                  tahun=inv.thn_pajak_sppt, tgl=self.calc.kini)
        inq.id = inquiry_id()
        inq.tagihan = self.calc.tagihan
        inq.denda = self.calc.denda
        inq.persen_denda = persen_denda
        inq.jatuh_tempo = inv.tgl_jatuh_tempo_sppt
        inq.bulan_tunggakan = self.calc.bln_tunggakan
        return inq

    def bayar(self, inq, total_bayar):
        bayar = inq2bayar(inq)
        if bayar:
            ke = bayar.pembayaran_sppt_ke + 1
        else:
            ke = 1
        bayar = Pembayaran()
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
        bayar.tgl_pembayaran_sppt = self.from_iso.get_transaction_date()
        bayar.jml_sppt_yg_dibayar = total_bayar 
        bayar.denda_sppt = inq.denda
        bayar.nip_rekam_byr_sppt = nip_rekam_byr_sppt
        for fieldname in FIELD_BANK:
            value = self.conf[fieldname]
            value = self.get_real_value(value)
            bayar.from_dict({fieldname: value})
        return bayar, ke

    ############
    # Reversal #
    ############
    def get_reversal_cls(self):
        return PaymentReversal

    ###########
    # Profile #
    ###########
    def nama_kelurahan(self):
        return cari_kelurahan(
            self.invoice_id['Propinsi'],
            self.invoice_id['Kabupaten'],
            self.invoice_id['Kecamatan'],
            self.invoice_id['Kelurahan'])

    def nama_kecamatan(self):
        return cari_kecamatan(
            self.invoice_id['Propinsi'],
            self.invoice_id['Kabupaten'],
            self.invoice_id['Kecamatan'])

    def nama_propinsi(self):
        return cari_propinsi(self.invoice_id['Propinsi'])

    def invoice2inquiry(self):
        return invoice2inquiry(self.calc.invoice)

    def invoice2payment(self):
        return invoice2payment(self.calc.invoice)
