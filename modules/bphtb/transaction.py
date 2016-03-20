import sys
sys.path.insert(0, '/usr/share/opensipkd/modules')
from tools import FixLength
from network import Network
from structure import (
    RC_INVALID_ID,
    RC_NOT_AVAILABLE,
    RC_OTHER_ERROR,
    RC_ALREADY_CANCELED,
    ERR_NOP,
    ERR_NOT_AVAILABLE,
    ERR_PROFILE,
    ERR_PROFILE2,
    ERR_BANK_PROFILE,
    ERR_PAYMENT_NOT_FOUND,
    ERR_ALREADY_CANCELED,
    TRANSACTION_BITS,
    PAYMENT_CODE,
    NOP,
    INVOICE_PROFILE,
    INVOICE_PROFILE2,
    BANK_PROFILE,
    )


class Transaction(Network):
    def __init__(self, *args, **kwargs):
        self.nop = FixLength(NOP)
        self.invoice_profile = FixLength(INVOICE_PROFILE)
        self.invoice_profile2 = FixLength(INVOICE_PROFILE2)
        self.bank_profile = FixLength(BANK_PROFILE)
        Network.__init__(self, *args, **kwargs)

    def get_nop(self):
        return self.get_value(61)

    def get_profile(self):
        return self.get_value(47)

    def get_profile2(self):
        return self.get_value(48)

    def get_bank_profile(self):
        return self.get_value(107)

    def get_amount(self):
        return self.get_value(4)

    def get_seq(self):
        return self.get_value(37)

    def err_nop(self):
        msg = ERR_NOP.format(nop=self.from_iso.get_nop())
        self.ack(RC_INVALID_ID, msg)

    def err_not_available(self, tahun):
        msg = ERR_NOT_AVAILABLE.format(nop=self.from_iso.get_nop(), tahun=tahun)
        self.ack(RC_NOT_AVAILABLE, msg)

    def err_profile(self):
        msg = ERR_PROFILE.format(profile=self.from_iso.get_profile())
        self.ack(RC_INVALID_ID, msg)

    def err_profile2(self):
        msg = ERR_PROFILE2.format(profile=self.from_iso.get_profile2())
        self.ack(RC_INVALID_ID, msg)

    def err_bank_profile(self):
        msg = ERR_BANK_PROFILE.format(profile=self.from_iso.get_bank_profile())
        self.ack(RC_INVALID_ID, msg)

    def err_other(self, msg):
        self.ack(RC_OTHER_ERROR, msg)

    def err_payment_not_found(self):
        msg = ERR_PAYMENT_NOT_FOUND.format(nop=self.from_iso.get_nop(),
                stan=self.from_iso.get_stan())
        self.ack(RC_NOT_AVAILABLE, msg)

    def err_already_canceled(self):
        msg = ERR_ALREADY_CANCELED.format(nop=self.from_iso.get_nop(),
                stan=self.from_iso.get_stan())
        self.ack(RC_ALREADY_CANCELED, msg)

    # Override
    def get_bit_definition(self):
        return TRANSACTION_BITS

    # Override
    def get_func_name(self):
        return self.is_echo_test_request() or self.is_payment() or \
               self.is_sign_on_request() or self.is_sign_off_request() or \
               self.is_reversal()

    # Override
    def set_response(self):
        if self.from_iso.is_network_request():
            Network.set_response(self)
        elif self.from_iso.is_transaction():
            self.set_transaction_response()
        elif self.from_iso.is_reversal():
            self.set_reversal_response()

    # Override
    def setIsoContent(self, raw):
        Network.setIsoContent(self, raw)
        self.raw = raw

    def is_transaction_response(self):
        return self.getMTI() == '0210'

    def is_response(self):
        return Network.is_response(self) or self.is_transaction_response()

    def is_transaction(self):
        return self.getMTI() in ['0200', '0210']

    def get_transaction_code(self):
        return self.get_value(3)

    def is_payment(self):
        if not self.is_transaction():
            return
        code = self.get_transaction_code()
        return code == PAYMENT_CODE and 'payment_response'

    def set_transaction_response(self):
        self.setMTI('0210')
        # Sesuai kolom yang berisi E (Equal) pada PDF
        self.copy([2, 3, 4, 11, 15, 18, 22, 32, 33, 35, 37, 41, 42, 43, 47, 48,
                   49, 59, 60, 61, 62, 63, 102, 107])
