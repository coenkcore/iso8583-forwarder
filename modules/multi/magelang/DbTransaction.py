from tools import FixLength
from ..transaction import Transaction
from structure import (
    INQUIRY_CODE,
    PAYMENT_CODE,
    INVOICE_PROFILE,
    ERR_INVALID_LENGTH,
    )
import bphtb
import padl


class DbTransaction(Transaction):
    def __init__(self, *args, **kwargs):
        self.invoice_profile = FixLength(INVOICE_PROFILE)
        Transaction.__init__(self, *args, **kwargs)

    # Override
    def get_bit_definitions(self):
        return TRANSACTION_BITS

    # Override
    def get_inquiry_codes(self):
        return (INQUIRY_CODE,)

    # Override
    def get_payment_codes(self):
        return (PAYMENT_CODE,)

    # Override
    def get_methods(self):
        return { 
            INQUIRY_CODE: 'inquiry_request_handler',
            PAYMENT_CODE: 'payment_request_handler',
            }

    # Override
    def set_transaction_response(self):
        self.setMTI('0210')
        # Sesuai kolom yang berisi E (Equal) pada dokumentasi
        self.copy([2, 3, 7, 11, 12, 13, 15, 18, 37, 41, 48, 90])
        raw = self.get_invoice_profile()
        self.invoice_profile.set_raw(raw)

    # Override
    # Ini dipanggil dengan from_iso.
    def get_invoice_id(self):
        raw = self.get_invoice_profile()
        self.invoice_profile.set_raw(raw)
        bank_invoice_id_raw = self.invoice_profile['ID Billing'].strip()
        return bank_invoice_id_raw[2:]

    def inquiry_request_handler(self):
        self.transaction_request_handler('inquiry')

    def payment_request_handler(self):
        self.transaction_request_handler('payment')

    def jenis_pajak(self):
        self.invoice_id_raw = self.get_invoice_id()
        length = len(self.invoice_id_raw)
        if length == 12:
            return 'bphtb'
        elif length == 10:
            return 'padl'
        self.ack_invalid_number()
 
    def transaction_request_handler(self, name):
        jenis_pajak = self.jenis_pajak()
        if not jenis_pajak:
            return
        func_name = '{j}_{n}_request_handler'.format(j=jenis_pajak, n=name)
        func = getattr(self, func_name)
        func()

    def get_invoice_profile(self):
        return self.get_value(48)

    # Override
    def set_invoice_profile(self):
        raw = self.invoice_profile.get_raw()
        self.setBit(48, raw)

    # Override
    def set_ntp(self, ntp):
        self.invoice_profile['NTPD'] = ntp

    # Override
    def get_cabang(self):
        return dict(kode=None, user=None)

    # Override
    def get_ntb(self):
        return self.get_value(90).lstrip('0')

    # Override
    def is_reversal_request(self):
        ok = Transaction.is_reversal_request(self)
        if ok:
            return ok
        jenis_pajak = self.jenis_pajak()
        if jenis_pajak:
            return '{j}_reversal_request_handler'.format(j=jenis_pajak)

    def bphtb_inquiry_request_handler(self):
        try:
            bphtb.inquiry(self)
        except:
            self.ack_unknown()

    def bphtb_payment_request_handler(self):
        try:
            bphtb.payment(self)
        except:
            self.ack_unknown()

    def padl_inquiry_request_handler(self):
        try:
            padl.inquiry(self)
        except:
            self.ack_unknown()

    def padl_payment_request_handler(self):
        try:
            padl.payment(self)
        except:
            self.ack_unknown()

    # Override
    def bphtb_reversal_request_handler(self):
        try:
            bphtb.reversal(self)
        except:
            self.ack_unknown()

    # Override
    def padl_reversal_request_handler(self):
        try:
            padl.reversal(self)
        except:
            self.ack_unknown()

    def ack_invalid_length(self):
        msg = ERR_INVALID_LENGTH.format(id=self.invoice_id_raw)
        self.ack(RC_INVALID_NUMBER, msg)
