import sys
from datetime import datetime
from sqlalchemy.sql import func
sys.path.insert(0, '/usr/share/opensipkd/modules')
from tools import (
    round_up,
    FixLength,
    )
sys.path.insert(0, '/usr/share/opensipkd-forwarder/modules/bca/')
from bphtb import BphtbDBSession
from bphtb_fix_structure import NOP
from bphtb_models import (
    Invoice,
    Pembayaran,
    #IsoPayment,
    )
from bphtb_fix_structure import INVOICE_ID, NOP, INVOICE_PROFILE
sys.path.insert(0, '/etc/opensipkd')
from bca_conf import persen_denda


def query_invoice(tahun, kode, no_sspd):
    return BphtbDBSession.query(Invoice).filter_by(
            tahun = tahun, kode = kode, no_sspd = no_sspd)

def get_last_payment(invoice):
    q = BphtbDBSession.query(Pembayaran).filter_by(sspd_id=invoice.id)
    q = q.order_by(Pembayaran.id.desc())
    return q.first()


class Common(object):
    def is_paid(self):
        return self.invoice.status_pembayaran == 1

    def set_paid(self):
        self.invoice.status_pembayaran = 1
        BphtbDBSession.add(self.invoice)

    # def set_unpaid(self):
        # self.invoice.status_pembayaran = 0
        # BphtbDBSession.add(self.invoice)


class CommonInvoice(Common):
    def __init__(self, invoice_id):
        self.invoice_id = invoice_id
        self.invoice_struct = FixLength(INVOICE_ID)
        self.invoice_struct.set_raw(invoice_id)
        q = query_invoice(self.invoice_struct['tahun'],
                str(int(self.invoice_struct['kode'])),
                self.invoice_struct['no_urut'])
        self.invoice = q.first()

        

class CalculateInvoice(CommonInvoice):
    def __init__(self, invoice_id):
        CommonInvoice.__init__(self, invoice_id)
        if not self.invoice:
            return
        self.nop_struct = FixLength(NOP)
        self.nop_struct.from_dict({
            'propinsi': self.invoice.kd_propinsi,
            'kabupaten': self.invoice.kd_dati2,
            'kecamatan': self.invoice.kd_kecamatan,
            'kelurahan': self.invoice.kd_kelurahan,
            'blok': self.invoice.kd_blok,
            'urut': self.invoice.no_urut,
            'jenis': self.invoice.kd_jns_op,
            })
        self.hitung()
        self.paid = self.is_paid() or self.total < 1
        # if self.paid:
            # # Dapatkan NTPD untuk bit 57
            # self.payment = self.get_payment()

    def hitung(self):
        # bayar = PbbDbSession.query(
                    # func.sum(Pembayaran.jml_sppt_yg_dibayar).\
                         # label('jml_sppt_yg_dibayar'),
                    # func.sum(Pembayaran.denda_sppt).\
                         # label('denda_sppt')).\
                    # filter_by(kd_propinsi=self.invoice.kd_propinsi,
                              # kd_dati2=self.invoice.kd_dati2,
                              # kd_kecamatan=self.invoice.kd_kecamatan,
                              # kd_kelurahan=self.invoice.kd_kelurahan,
                              # kd_blok=self.invoice.kd_blok,
                              # no_urut=self.invoice.no_urut,
                              # kd_jns_op=self.invoice.kd_jns_op,
                              # thn_pajak_sppt=self.invoice.thn_pajak_sppt).one()
        # jml_bayar = bayar.jml_sppt_yg_dibayar or 0
        # denda_lalu = bayar.denda_sppt or 0
        
        kini = datetime.now()
        jatuh_tempo = self.invoice.tgl_jatuh_tempo
        self.tagihan = round_up(self.invoice.bphtb_harus_dibayarkan)
        self.denda = self.invoice.denda
        self.pokok = self.tagihan-self.denda
        if jatuh_tempo:
            x = (kini.year - jatuh_tempo.year) * 12
            y = kini.month - jatuh_tempo.month
            bln_tunggakan = x + y + 1
            if kini.day <= jatuh_tempo.day:
                bln_tunggakan -= 1
            if bln_tunggakan < 1:
                bln_tunggakan = 0
            if bln_tunggakan > 24:
                bln_tunggakan = 24
            self.denda = self.denda + (bln_tunggakan * persen_denda / 100.0 * self.pokok)
            if self.pokok and self.denda/self.pokok>0.48:
                  self.denda = round_up(0.48*self.pokok)
                  
        self.denda = round_up(self.denda)
        self.total = self.pokok + self.denda

    def get_nop(self):
        return self.invoice and self.nop_struct.get_raw() or ''

    def get_payment(self):
        return get_last_payment(self.invoice)
