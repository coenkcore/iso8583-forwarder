import re
import traceback
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
from tools import TransactionID
from .transaction import Transaction
from .query import (
    CalculateInvoice,
    InvoiceQuery,
    )
from .models import (
    IsoPayment,
    IsoReversal,
    )


class NTP(TransactionID):
    def __init__(self, DBSession):
        self.DBSession = DBSession

    # Override
    def is_found(self, ntp):
        q = self.DBSession.query(IsoPayment).filter_by(ntp=ntp)
        return q.first()


class DbTransaction(Transaction):
    def get_invoice(self):
        self.get_invoice_id()
        self.calc = CalculateInvoice(
            self.invoice_id['Tahun'], self.invoice_id['SPT No']) 
        if not self.calc.invoice:
            return self.ack_not_available()
        self.set_invoice_profile()
        if self.calc.is_paid():
            return self.ack_already_paid()
        d = {'Tagihan Pokok': self.calc.tagihan, 'Denda': self.calc.denda}
        self.invoice_profile.from_dict(d)
        self.set_invoice_profile()
        return True

    def inquiry(self):
        if self.get_invoice():
            self.set_amount(self.calc.total)
            self.ack()

    def set_invoice_profile(self):
        inv = self.calc.invoice
        cust = self.calc.get_customer()
        rek = self.calc.get_rekening()
        no_rek = re.sub('[^0-9]', '', rek.rekeningkd)
        self.invoice_profile.from_dict({
            'NPWPD': cust.npwpd,
            'Nama OP': cust.customernm,
            'Bulan': inv.masadari.strftime('%m'),
            'Tahun': inv.masadari.strftime('%Y'),
            'Tanggal Penetapan': inv.terimatgl.strftime('%d-%m-%Y'),
            'Tanggal Jatuh Tempo': inv.jatuhtempotgl.strftime('%d-%m-%Y'),
            'Jenis Pajak': ' '.join([no_rek, rek.rekeningnm]),
            'Masa Pajak': ' s.d '.join(
                [inv.masadari.strftime('%d-%m-%Y'),
                 inv.masasd.strftime('%d-%m-%Y')]),
            })
        Transaction.set_invoice_profile(self)

    def inquiry_request_handler(self):
        try:
            self.inquiry()
        except:
            self.ack_other()

    def payment(self):
        self.copy([4])
        if not self.get_invoice():
            return
        if self.calc.total != self.get_amount():
            return self.ack_insufficient_fund(self.calc.total)
        pay = self.calc.set_paid()
        ntp_generator = NTP(self.calc.DBSession)
        ntp = ntp_generator.create()
        iso_pay = IsoPayment()
        iso_pay.sspd_id = pay.id
        iso_pay.invoice_no = self.get_invoice_id()
        iso_pay.iso_request = self.from_iso.raw.upper()
        iso_pay.transmission = self.from_iso.get_transmission()
        iso_pay.settlement = self.from_iso.get_settlement()
        iso_pay.stan = self.from_iso.get_stan()
        iso_pay.ntb = self.from_iso.get_ntb()
        iso_pay.ntp = ntp
        iso_pay.bank_id = self.get_bank_id() 
        iso_pay.channel_id = self.get_channel() 
        iso_pay.bank_ip = self.get_bank_ip()
        iso_pay.invoice_id = self.calc.invoice.id
        self.calc.DBSession.add(iso_pay)
        self.calc.DBSession.flush()
        self.invoice_profile['NTPD'] = ntp
        self.set_invoice_profile()
        self.calc.DBSession.commit()
        self.ack()

    def payment_request_handler(self):
        try:
            self.payment()
        except:
            self.ack_other()

    def reversal(self):
        invoice_id = self.get_invoice_id()
        rev = InvoiceQuery(self.invoice_id['Tahun'], self.invoice_id['SPT No'])
        if not rev.invoice:
            return self.ack_not_available()
        if not rev.is_paid():
            return self.ack_invoice_open()
        amount = self.get_amount()
        pay = rev.get_payment()
        if not pay:
            return self.ack_iso_payment_not_found()
        if pay.jml_bayar != amount:
            return self.ack_insufficient_fund()
        ntb = self.get_ntb()
        q = rev.DBSession.query(IsoPayment).filter_by(sspd_id=pay.id)
        iso_pay = q.first() 
        if not iso_pay:
            return self.ack_iso_payment_not_found()
        rev.set_unpaid(pay)
        rev.DBSession.commit()
        self.ack()
 
    def reversal_request_handler(self):
        try:
            self.reversal()
        except:
            self.ack_other()

    def ack_other(self):
        Transaction.ack_other(self)
        f = StringIO()
        traceback.print_exc(file=f)
        self.log_error(f.getvalue())
        f.close()
