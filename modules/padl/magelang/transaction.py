from tools import FixLength
from common.transaction import BaseTransaction
from .structure import (
    INVOICE_ID,
    INVOICE_PROFILE,
    TRANSACTION_BITS,
    INQUIRY_CODE,
    PAYMENT_CODE,
    )


class Transaction(BaseTransaction):
    def __init__(self, *args, **kwargs):
        self.invoice_id = FixLength(INVOICE_ID)
        self.invoice_profile = FixLength(INVOICE_PROFILE)
        BaseTransaction.__init__(self, *args, **kwargs)
        self.invoice_id_raw = None
 
    # Override
    def get_bit_definition(self):
        return TRANSACTION_BITS

    # Override
    def get_inquiry_code(self):
        return INQUIRY_CODE

    # Override
    def get_payment_code(self):
        return PAYMENT_CODE

    # Override
    def set_transaction_response(self):
        self.setMTI('0210')
        self.copy([2, 3, 7, 11, 12, 13, 15, 18, 32, 37, 41, 48, 90])

    # Override
    def get_invoice_id(self):
        if self.invoice_id_raw is not None:
            return self.invoice_id_raw
        raw = self.get_value(48)
        self.invoice_profile.set_raw(raw)
        self.invoice_id_raw = self.invoice_profile['ID Billing'].strip()
        self.invoice_id.set_raw(self.invoice_id_raw)
        return self.invoice_id_raw

    def set_invoice_id(self, raw):
        self.invoice_profile['ID Billing'] = raw
        self.set_invoice_profile()

    # Override
    def set_invoice_profile(self):
        self.setBit(48, self.invoice_profile.get_raw())

    # Override
    def set_ntp(self, ntp):
        self.invoice_profile['NTPD'] = ntp

    # Override
    def get_ntb(self):
        return self.get_value(90)

    def set_ntb(self, raw):
        self.setBit(90, raw)

    # Override
    def payment_response(self):
        self.copy([4])
