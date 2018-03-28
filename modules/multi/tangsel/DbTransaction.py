from tools import FixLength
from ..transaction import RC_NOT_AVAILABLE
from .structure import (
    ERR_KODE_PEMDA,
    ERR_KODE_APLIKASI,
    INQUIRY_CODE,
    PAYMENT_CODE,
    )
import bphtb
import padl
from multi.BogorKota import DbTransaction as BaseDbTransaction
from .conf import (
    kode_pemda,
    kode_bphtb,
    kode_padl,
    )


MODULE = {
    kode_bphtb: bphtb,
    kode_padl: padl,
    }

INVOICE_ID = [
    ('Kode Pemda', 4, 'N'),
    ('Kode Aplikasi', 2, 'N'),
    ('Invoice ID', 12, 'N'),
    ]

METHODS = {
    INQUIRY_CODE: 'inquiry_request_handler',
    PAYMENT_CODE: 'payment_request_handler',
    }

INQUIRY_CODES = (INQUIRY_CODE,)
PAYMENT_CODES = (PAYMENT_CODE,)

REVERSAL_METHODS = {
    PAYMENT_CODE: 'reversal_request_handler',
    }


def get_invoice_id(raw):
    invoice_id = FixLength(INVOICE_ID)
    invoice_id.set_raw(raw)
    return invoice_id


class DbTransaction(BaseDbTransaction):
    # Override
    def get_methods(self):
        return METHODS

    # Override
    def get_inquiry_codes(self):
        return INQUIRY_CODES

    # Override
    def get_payment_codes(self):
        return PAYMENT_CODES

    # Override
    def get_reversal_methods(self):
        return REVERSAL_METHODS

    def request_handler(self, func_name='inquiry'):
        invoice_id_raw = self.get_invoice_id()
        self.invoice_id = get_invoice_id(invoice_id_raw)
        if self.invoice_id['Kode Pemda'] != kode_pemda:
            return self.ack_invalid_kode_pemda()
        kode_app = self.invoice_id['Kode Aplikasi']
        if kode_app in (kode_bphtb, kode_padl):
            self.invoice_id_raw = self.invoice_id['Invoice ID']
            module = MODULE[kode_app]
            func = getattr(module, func_name)
            try:
                func(self)
            except Exception:
                self.ack_unknown()
        else:
            self.ack_invalid_kode_aplikasi()

    # Override
    def inquiry_request_handler(self):
        self.request_handler()

    # Override
    def payment_request_handler(self):
        self.request_handler('payment')

    # Override
    def reversal_request_handler(self):
        self.request_handler('reversal')

    def ack_invalid_kode_pemda(self):
        msg = ERR_KODE_PEMDA.format(kode=self.invoice_id['Kode Pemda'])
        self.ack(RC_NOT_AVAILABLE, msg)

    def ack_invalid_kode_aplikasi(self):
        msg = ERR_KODE_APLIKASI.format(kode=self.invoice_id['Kode Aplikasi'])
        self.ack(RC_NOT_AVAILABLE, msg)
