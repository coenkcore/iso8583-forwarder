import sys
from CalculateInvoice import (
    Common,
    query_sppt,
    )
from DbTools import query_pembayaran

from pbb_structure import INVOICE_ID, INVOICE_PROFILE
sys.path[0:0] = ['/usr/share/opensipkd-forwarder/modules/bca/']
from pbb import PbbDbSession

sys.path[0:0] = ['/usr/share/opensipkd/modules']
from pbb_db_transaction import MyFixLength

def pay2bayar(pay,invoice_id):
    q = query_pembayaran(invoice_id['Propinsi'],
            invoice_id['Kabupaten'],
            invoice_id['Kecamatan'],
            invoice_id['Kelurahan'],
            invoice_id['Blok'],
            invoice_id['Urut'],
            invoice_id['Jenis'],
            invoice_id['Tahun Pajak'])
    q = q.filter_by(pembayaran_sppt_ke=pay.ke)
    return q.first()


def pay2sppt(pay, invoice_id):
    q = query_sppt(invoice_id['Propinsi'],
            invoice_id['Kabupaten'],
            invoice_id['Kecamatan'],
            invoice_id['Kelurahan'],
            invoice_id['Blok'],
            invoice_id['Urut'],
            invoice_id['Jenis'],
            invoice_id['Tahun Pajak'])
    return q.first() 


class ReversalCommon(object):
    def set_unpaid(self):
        self.invoice.status_pembayaran_sppt = '0'
        self.bayar.jml_sppt_yg_dibayar = 0 
        self.bayar.denda_sppt = 0


class PbbReversal(Common, ReversalCommon):
    def __init__(self, pay):
        self.invoice_id = MyFixLength(INVOICE_ID)
        self.pay = pay
        self.invoice_id.set_raw(pay.invoice_id)
        self.bayar = pay2bayar(pay, self.invoice_id)
        if not self.bayar:
            return
        self.invoice = pay2sppt(pay, self.invoice_id)
    def is_paid(self):
        return int(self.invoice.status_pembayaran_sppt)
    
    def commit(self):
        PbbDbSession.add(self.invoice)
        PbbDbSession.add(self.bayar)
        PbbDbSession.flush()
        PbbDbSession.commit()

class PbbReversalByQuery(Common, ReversalCommon):
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
