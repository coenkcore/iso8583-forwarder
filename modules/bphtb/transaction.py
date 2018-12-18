from tools import FixLength
from common.transaction import BaseTransaction 
from common.transaction.structure import (
    RC_INVALID_NUMBER,
    RC_NOT_AVAILABLE,
    )
from common.bphtb.structure import (
    TRANSACTION_BITS,
    INQUIRY_CODE,
    PAYMENT_CODE,
    get_invoice_profile, 
    INVOICE_PROFILE2,
    ERR_INVALID_LENGTH,
    ERR_INVALID_PREFIX,
    ERR_INVALID_MAX_LENGTH,
    ERR_INVALID_NOP,
    )
from config import bphtb as conf


INVOICE_PROFILE = get_invoice_profile(conf['number_of_ext'])


class Transaction(BaseTransaction):
    def __init__(self, *args, **kwargs):
        BaseTransaction.__init__(self, *args, **kwargs)
        self.invoice_profile = FixLength(INVOICE_PROFILE)
        self.invoice_profile2 = FixLength(INVOICE_PROFILE2)

    # Override
    def get_inquiry_code(self):
        return INQUIRY_CODE

    # Override
    def get_payment_code(self):
        return PAYMENT_CODE

    # Override
    def get_bit_definition(self):
        return TRANSACTION_BITS

    def set_transaction_response(self):
        BaseTransaction.set_transaction_response(self)
        self.copy([49, 58, 59, 60, 62, 63, 102, 107])
        self.setBit(47, '')
        self.setBit(48, '')
        self.setBit(61, '')

    def get_nop(self):
        return self.get_value(61).strip()

    def set_nop(self, nop):
        return self.setBit(61, nop)

    def get_invoice_id(self):
        return self.get_value(62).strip()

    def set_invoice_profile(self):
        raw = self.invoice_profile.get_raw()
        self.setBit(47, raw)
        raw = self.invoice_profile2.get_raw()
        self.setBit(48, raw)

    def set_ntp(self, ntp):
        self.setBit(57, ntp)

    # Nomor Transaksi Bank
    def set_ntb(self, ntb):
        self.setBit(58, ntb)

    def get_ntb(self):
        return self.get_value(58)

    def get_bank_ip(self):
        if 'ip' in self.conf:
            return self.conf['ip']

    def ack_invalid_max_length(self, max_length):
        msg = ERR_INVALID_MAX_LENGTH.format(
                invoice_id=self.invoice_id_raw,
                max_length=max_length)
        self.ack(RC_INVALID_NUMBER, msg)

    def ack_invalid_length(self, length):
        msg = ERR_INVALID_LENGTH.format(
                invoice_id=self.get_invoice_id(), length=length,
                orig_length=len(self.invoice_id_raw))
        self.ack(RC_INVALID_NUMBER, msg)
        
    def ack_invalid_prefix(self, prefix):
        msg = ERR_INVALID_PREFIX.format(
                invoice_id=self.get_invoice_id(), prefix=prefix)
        self.ack(RC_INVALID_NUMBER, msg)

    def ack_invalid_nop(self, nop):
        msg = ERR_INVALID_NOP.format(
                invoice_id=self.get_invoice_id(), nop=nop,
                invalid_nop=self.from_iso.get_nop())
        self.ack(RC_NOT_AVAILABLE, msg)
