import sys
sys.path.insert(0, '/usr/share/opensipkd/modules')
from tools import round_up
from sqlalchemy.sql import func
from models import (
    OtherDBSession,
    Invoice,
    Payment,
    )


def query_invoice(invoice_id):
    return OtherDBSession.query(Invoice).filter_by(kd_booking=invoice_id)


class Common(object):
    def is_paid(self):
        return self.invoice.status_bayar == '1'


class CalculateInvoice(Common):
    def __init__(self, invoice_id):
        self.invoice_id = invoice_id
        q = query_invoice(invoice_id)
        self.invoice = q.first()
        if self.invoice:
            self.hitung()
            self.paid = self.is_paid() or self.total < 1 
            if self.paid:
                # Dapatkan NTPD untuk bit 57
                q = OtherDBSession.query(Payment).filter_by(
                        kd_booking=self.invoice.kd_booking).\
                        order_by(Payment.pembayaran_bphtb_ke.desc())
                self.bayar = q.first()

    def hitung(self):
        self.total = self.tagihan = round_up(self.invoice.bphtb_yg_harus_dibayar)
        q = OtherDBSession.query(func.sum(Payment.bphtb_dibayar).\
                label('bayar')).filter_by(
                kd_booking=self.invoice.kd_booking, reversal=0)
        pay = q.first()
        if pay and pay.bayar:
            self.total -= round_up(pay.bayar)

    def set_paid(self):
        self.invoice.status_bayar = '1'
        OtherDBSession.add(self.invoice)

    def get_ntp(self):
        return self.invoice and self.paid and self.bayar and self.bayar.ntpd

    def get_nop(self):
        return self.invoice and self.invoice.nop or ''
