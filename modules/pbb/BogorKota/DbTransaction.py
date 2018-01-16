from sismiop.query import CalculateInvoice as BaseCalc
from pbb.cikarang.DbTransaction import (
    InquiryResponse as BaseInqResp,
    PaymentResponse as BasePayResp,
    DbTransaction as BaseTrx,
    )


def debug(s):
    print('*** DEBUG {}'.format(s))


def debug_label(label, s):
    debug('{:22}: {}'.format(label, s))


def debug_rp(label, n):
    debug('{:22}: Rp {:9d}'.format(label, n))


class CalculateInvoice(BaseCalc):
    def hitung(self):
        BaseCalc.hitung(self)
        # 1-10-2017 Perwal penghapusan denda Kota Bogor
        debug_label('Tahun Pajak', self.invoice.thn_pajak_sppt)
        if self.invoice.thn_pajak_sppt < '2013':
            debug_rp('Total Sebelum Discount', self.total)
            self.discount = self.denda
            debug_rp('Discount', self.discount)
            self.denda = 0
            self.total -= self.discount
            debug_rp('Total Setelah Discount', self.total)
        else:
            self.discount = 0

    def before_save(self, bayar):
        bayar.discount = self.discount


class InquiryResponse(BaseInqResp):
    def get_calc_cls(self):
        return CalculateInvoice


def inquiry(parent):
    handler = InquiryResponse(parent)
    handler.response()


class PaymentResponse(BasePayResp):
    def get_calc_cls(self):
        return CalculateInvoice


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
