from pprint import pprint
from pbb.cikarang.DbTransaction import Inquiry as BaseQuery
from pbb.BogorKota.DbTransaction import (
    CalculateInvoice as BaseCalc,
    DbTransaction as BaseTrx,
    InquiryResponse as BaseInqResp,
    PaymentResponse as BasePayResp,
    debug_label,
    debug,
    )
from pbb_g2.structure import INVOICE_PROFILE


def debug_dict(label, d):
    debug(label)
    print(d)


# Agar saat Payment tidak perlu lagi mencari tahun_sisa.
class Inquiry(BaseQuery):
    def before_save(self, calc, inq):
        inq.tahun_sisa = calc.tahun_sisa


class CalculateInvoice(BaseCalc):
    def __init__(self, *args, **kwargs):
        self.hitung_tahun_sisa = True
        BaseCalc.__init__(self, *args, **kwargs)

    def hitung(self):
        BaseCalc.hitung(self)
        if not self.hitung_tahun_sisa:
            return
        tahun = int(self.invoice.thn_pajak_sppt)
        for i in range(5):
            tahun -= 1
            s_tahun = str(tahun)
            invoice = self.invoice_tahun(s_tahun)
            if not invoice:
                continue
            tagihan, denda, bln_tunggakan, kini = self.hitung_invoice(invoice)
            if tagihan > 0:
                self.tahun_sisa = s_tahun
                debug_label('Tahun Sisa', s_tahun)
                return
        self.tahun_sisa = '0000'


class InquiryResponse(BaseInqResp):
    def set_invoice_profile(self):
        BaseInqResp.set_invoice_profile(self)
        self.invoice_profile.from_dict({
            'Discount': self.calc.discount,
            'Tahun Sisa': self.calc.tahun_sisa,
            })
        debug_dict('Invoice Profile', self.invoice_profile)

    # Override
    def get_query_cls(self):
        return Inquiry

    # Override
    def get_calc_cls(self):
        return CalculateInvoice

    # Override
    def get_invoice_profile_structure(self):
        return INVOICE_PROFILE


def inquiry(parent):
    handler = InquiryResponse(parent)
    handler.response()


class PayCalc(CalculateInvoice):
    def __init__(self, *args, **kwargs):
        self.hitung_tahun_sisa = False
        BaseCalc.__init__(self, *args, **kwargs)


class PaymentResponse(BasePayResp):
    def get_calc_cls(self):
        return PayCalc

    def get_invoice_profile_structure(self):
        return INVOICE_PROFILE

    def set_invoice_profile(self):
        BaseInqResp.set_invoice_profile(self)
        self.invoice_profile.from_dict({
            'Discount': self.calc.discount,
            })

    def create_payment(self, inq):
        BasePayResp.create_payment(self, inq)
        self.invoice_profile.from_dict({
            'Tahun Sisa': inq.tahun_sisa,
            })
        debug_dict('Invoice Profile', self.invoice_profile)


def payment(parent):
    handler = PaymentResponse(parent)
    handler.response()


class DbTransaction(BaseTrx):
    # Override
    def inquiry_request_handler(self):
        try:
            inquiry(self)
        except Exception:
            self.ack_unknown()

    # Override
    def payment_request_handler(self):
        try:
            payment(self)
        except Exception:
            self.ack_unknown()
