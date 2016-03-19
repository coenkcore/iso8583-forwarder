from CalculateInvoice import (
    Common,
    query_sppt,
    )
from DbTools import query_pembayaran


def pay2bayar(pay):
    q = query_pembayaran(pay.propinsi, pay.kabupaten, pay.kecamatan,
            pay.kelurahan, pay.blok, pay.urut, pay.jenis, str(pay.tahun))
    q = q.filter_by(pembayaran_sppt_ke=pay.ke)
    return q.first()


def pay2sppt(pay):
    q = query_sppt(pay.propinsi, pay.kabupaten, pay.kecamatan, pay.kelurahan,
        pay.blok, pay.urut, pay.jenis, str(pay.tahun))
    return q.first() 


class ReversalCommon(object):
    def set_unpaid(self):
        self.invoice.status_pembayaran_sppt = '0'
        self.bayar.jml_sppt_yg_dibayar = 0 
        self.bayar.denda_sppt = 0


class PaymentReversal(Common, ReversalCommon):
    def __init__(self, pay):
        self.pay = pay
        self.bayar = pay2bayar(pay)
        if not self.bayar:
            return
        self.invoice = pay2sppt(pay)


class ReversalByQuery(Common, ReversalCommon):
    def __init__(self, invoice_id):
        q = query_sppt(invoice_id['Propinsi'], invoice_id['Kabupaten'],
                invoice_id['Kecamatan'], invoice_id['Kelurahan'],
                invoice_id['Blok'], invoice_id['Urut'],
                invoice_id['Jenis'], invoice_id['Tahun Pajak'])
        self.invoice = q.first()
        if not self.invoice:
            return
        q = query_pembayaran(invoice_id['Propinsi'], invoice_id['Kabupaten'],
                invoice_id['Kecamatan'], invoice_id['Kelurahan'],
                invoice_id['Blok'], invoice_id['Urut'],
                invoice_id['Jenis'], invoice_id['Tahun Pajak'])
        q = q.order_by('pembayaran_sppt_ke DESC')
        self.bayar = q.first()
