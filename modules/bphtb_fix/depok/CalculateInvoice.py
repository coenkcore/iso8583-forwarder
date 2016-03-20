import sys
sys.path[0:0] = ['/usr/share/opensipkd/modules']
from base_models import DBSession 
from models import (
    Invoice,
    Payment,
    )


def query_invoice(invoice_id):
    return DBSession.query(Invoice).filter_by(source_id=2,
            no_tagihan=invoice_id).order_by('tahun DESC')

def invoice2payment(invoice):
    q = DBSession.query(Payment).filter_by(invoice_id=invoice.id)
    return q.first()


class Common(object):
    def is_paid(self):
        return self.invoice.status_bayar == 1


class CalculateInvoice(Common):
    def __init__(self, invoice_id):
        self.invoice_id = invoice_id
        q = query_invoice(invoice_id)
        self.invoice = q.first()
        if self.invoice:
            self.hitung()
            self.paid = self.is_paid()
            if self.paid:
                self.bayar = invoice2payment(self.invoice)

    def hitung(self):
        self.tagihan = self.total = int(self.invoice.jml_tagihan)

    def set_paid(self):
        self.invoice.status_bayar = 1
        DBSession.add(self.invoice)

    def get_ntp(self):
        return self.invoice and self.paid and self.bayar and self.bayar.ntp

    def get_nop(self):
        return self.invoice and self.invoice.nop or ''
