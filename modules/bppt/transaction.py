from tools import FixLength
from network import Network
from common.transaction import BaseTransaction
from structure import (
    INVOICE_PROFILE,
    TRANSACTION_BITS,
    INQUIRY_CODE,
    PAYMENT_CODE,
    INVOICE_PROFILE,
    RC_INVALID_NUMBER,
    RC_NOT_AVAILABLE,
    RC_ALREADY_PAID,
    ERR_INVALID_NUMBER,
    ERR_NOT_AVAILABLE,
    ERR_ALREADY_PAID,
    ERR_INVOICE_OPEN,
    ERR_PAYMENT,
    ERR_ISO_PAYMENT,
    ERR_PAYMENT_OWNER,
    ERR_NTB,
    )


class Transaction(BaseTransaction):
    def __init__(self, *args, **kwargs):
        BaseTransaction.__init__(self, *args, **kwargs)
        self.invoice_profile = FixLength(INVOICE_PROFILE)

    # Override
    def get_bit_definition(self):
        return TRANSACTION_BITS

    # Override
    def set_response(self):
        if self.from_iso.is_network_request():
            Network.set_response(self)
        if self.from_iso.is_payment_request():
            self.set_payment_response()
        elif self.from_iso.is_transaction_request():
            self.set_transaction_response()
        elif self.from_iso.is_reversal_request():
            self.set_reversal_response()

    def get_payment_codes(self):
        return PAYMENT_CODES

    def get_methods(self):
        return METHODS

    def get_invoice_id(self):
        return self.get_value(61).strip()

    def is_inquiry_request(self):
        return self.is_transaction_request() and \
                self.get_transaction_code() == INQUIRY_CODE and \
                'inquiry_request_handler'

    def is_inquiry_response(self):
        return self.is_transaction_response() and \
                self.get_transaction_code() == INQUIRY_CODE

    def is_payment_request(self):
        return self.is_transaction_request() and \
                self.get_transaction_code() == PAYMENT_CODE and \
                'payment_request_handler'

    def is_payment_response(self):
        return self.is_transaction_response() and \
                self.get_transaction_code() == PAYMENT_CODE 

    def set_transaction_response(self):
        BaseTransaction.set_transaction_response(self)
        self.copy([48, 49, 59, 60, 61, 62, 63, 102, 107])

    def set_payment_response(self):
        self.set_transaction_response()
        self.copy([4, 48, 62])
        self.set_ntp('')

    def set_invoice_profile(self, raw):
        self.setBit(62, raw)

    def get_ntb(self):
        return self.get_value(48)

    def set_ntb(self, v):
        self.setBit(48, v)

    def set_ntp(self, v):
        self.setBit(47, v)

    def set_amount(self, value):
        self.setBit(4, value)

    def get_amount(self):
        return int(self.get_value(4))

    def get_channel_id(self):
        return self.get_value(18)

    def get_bank_ip(self):
        return self.conf['ip']

    ############
    # Reversal #
    ############
    def is_reversal_request(self):
        return BaseTransaction.is_reversal_request(self) and \
                self.get_transaction_code() == PAYMENT_CODE and \
                'reversal_request_handler'

    ###################
    # Acknowledgement #
    ###################
    def ack_invalid_number(self):
        msg = ERR_INVALID_NUMBER.format(
                invoice_id=self.from_iso.get_invoice_id())
        self.ack(RC_INVALID_NUMBER, msg)

    def ack_not_available(self):
        msg = ERR_NOT_AVAILABLE.format(
                invoice_id=self.from_iso.get_invoice_id())
        self.ack(RC_NOT_AVAILABLE, msg)

    def ack_already_paid(self):
        msg = ERR_ALREADY_PAID.format(
                invoice_id=self.from_iso.get_invoice_id())
        self.ack(RC_ALREADY_PAID, msg)

    def ack_insufficient_fund(self, total_tagihan):
        msg = ERR_INSUFFICIENT_FUND.format(
                invoice_id=self.from_iso.get_invoice_id(),
                bayar=self.from_iso.get_amount(), tagihan=total_tagihan)
        self.ack(RC_INSUFFICIENT_FUND, msg)

    def ack_payment_not_found(self):
        self.ack(RC_NOT_AVAILABLE, ERR_PAYMENT.format(
            invoice_id=self.get_invoice_id()))

    def ack_iso_payment_not_found(self):
        self.ack(RC_NOT_AVAILABLE, ERR_ISO_PAYMENT.format(
            invoice_id=self.get_invoice_id()))

    def ack_payment_owner(self):
        msg = ERR_PAYMENT_OWNER.format(invoice_id=self.get_invoice_id())
        self.ack(RC_NOT_AVAILABLE, msg)

    def ack_invoice_open(self):
        msg = ERR_INVOICE_OPEN.format(invoice_id=self.get_invoice_id())
        self.ack(RC_ALREADY_PAID, msg)

    def ack_payment_owner(self):
        msg = ERR_PAYMENT_OWNER.format(invoice_id=self.get_invoice_id())
        self.ack(RC_NOT_AVAILABLE, msg)

    def ack_ntb(self):
        msg = ERR_NTB.format(
                ntb=self.get_ntb(), invoice_id=self.get_invoice_id())
