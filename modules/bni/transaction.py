from types import DictType
from tools import FixLength
from network import Network
from common.transaction import BaseTransaction
from structure import (
    TRANSACTION_BITS,
    BIT_INVOICE_ID,
    BIT_INVOICE_PROFILE,
    BIT_NTB,
    PBB_INQUIRY_CODE,
    PBB_PAYMENT_CODE,
    RC_ALREADY_PAID,
    RC_NOT_AVAILABLE,
    RC_INSUFFICIENT_FUND,
    RC_OTHER,
    ERR_NOT_AVAILABLE,
    ERR_ALREADY_PAID,
    ERR_ALREADY_PAID_2,
    ERR_INQUIRY_NOT_FOUND,
    ERR_PAYMENT_NOT_FOUND,
    ERR_PAYMENT_NOT_FOUND_2,
    ERR_PAYMENT_OWNER,
    ERR_CREATE_PAYMENT,
    ERR_INVOICE_OPEN,
    ERR_INSUFFICIENT_FUND,
    )


METHODS = {
    PBB_INQUIRY_CODE: 'pbb_inquiry_request_handler',
    PBB_PAYMENT_CODE: 'pbb_payment_request_handler',
    }

REVERSAL_METHODS = {
    PBB_PAYMENT_CODE: 'pbb_reversal_request_handler',
    }

INQUIRY_CODES = (PBB_INQUIRY_CODE,)
PAYMENT_CODES = (PBB_PAYMENT_CODE,)


class Transaction(BaseTransaction):
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

    def get_inquiry_codes(self):
        return INQUIRY_CODES

    def get_payment_codes(self):
        return PAYMENT_CODES

    def get_methods(self):
        return METHODS

    def get_reversal_methods(self):
        return REVERSAL_METHODS

    def is_inquiry_request(self):
        if not self.is_transaction_request():
            return
        code = self.get_transaction_code()
        if code not in self.get_inquiry_codes():
            return
        methods = self.get_methods()
        if code in methods: 
            return methods[code]

    def is_inquiry_response(self):
        return self.get_transaction_code() in self.get_inquiry_codes()

    def is_payment_request(self):
        if not self.is_transaction_request():
            return
        code = self.get_transaction_code()
        if code not in self.get_payment_codes():
            return
        methods = self.get_methods()
        if code in methods: 
            return methods[code]

    def is_payment_response(self):
        return self.get_transaction_code() in self.get_payment_codes()

    def set_transaction_response(self):
        BaseTransaction.set_transaction_response(self)
        self.copy([47, 49, 59, 60, 61, 63, 102, 107])

    def set_payment_response(self):
        self.set_transaction_response()
        self.copy([4, 48, 62])

    def is_reversal_request(self):
        if not BaseTransaction.is_reversal_request(self):
            return
        code = self.get_transaction_code()
        methods = self.get_reversal_methods()
        if code in methods: 
            return methods[code]

    def get_transmission(self):
        raw = self.get_value(7)
        self.transmission.set_raw(raw)
        # without time zone
        return self.transmission.get_value()

    def get_settlement(self):
        t = self.get_transmission()
        return t.date()

    def get_invoice_id(self):
        return self.get_value(BIT_INVOICE_ID).strip().lstrip('0')

    def set_invoice_profile(self, raw):
        self.setBit(BIT_INVOICE_PROFILE, raw)

    def get_ntb(self):
        return self.get_value(BIT_NTB)

    def set_ntb(self, v):
        self.setBit(BIT_NTB, v)

    def get_bank_code(self, fieldname):
        value = self.conf[fieldname]
        if type(value) is not DictType:
            return value
        channel = self.get_channel()
        if channel in value:
            return value[channel]
        if 'default' in value:
            return value['default']
        return '00'

    def ack_not_available(self):
        msg = ERR_NOT_AVAILABLE.format(
                invoice_id=self.from_iso.get_invoice_id())
        self.ack(RC_NOT_AVAILABLE, msg)

    def ack_not_available_2(self, invoice_id):
        msg = ERR_NOT_AVAILABLE.format(invoice_id=invoice_id)
        self.ack(RC_NOT_AVAILABLE, msg)

    def ack_already_paid(self):
        msg = ERR_ALREADY_PAID.format(
                invoice_id=self.from_iso.get_invoice_id())
        self.ack(RC_ALREADY_PAID, msg)

    def ack_already_paid_2(self, nominal):
        msg = ERR_ALREADY_PAID_2.format(
                invoice_id=self.from_iso.get_invoice_id(), nominal=nominal)
        self.ack(RC_ALREADY_PAID, msg)

    def ack_create_payment_failed(self):
        self.ack_other(ERR_CREATE_PAYMENT)

    def ack_inquiry_not_found(self):
        msg = ERR_INQUIRY_NOT_FOUND.format(
                invoice_id=self.from_iso.get_invoice_id())
        self.ack_other(msg)

    def ack_insufficient_fund(self, total_tagihan):
        msg = ERR_INSUFFICIENT_FUND.format(
                invoice_id=self.from_iso.get_invoice_id(),
                bayar=self.from_iso.get_amount(), tagihan=total_tagihan)
        self.ack(RC_INSUFFICIENT_FUND, msg)

    def ack_payment_not_found(self):
        self.ack(RC_NOT_AVAILABLE, ERR_PAYMENT_NOT_FOUND)

    def ack_payment_not_found_2(self):
        msg = ERR_PAYMENT_NOT_FOUND_2.format(invoice_id=self.get_invoice_id())
        self.ack(RC_NOT_AVAILABLE, msg)

    def ack_payment_owner(self):
        msg = ERR_PAYMENT_OWNER.format(invoice_id=self.get_invoice_id())
        self.ack(RC_NOT_AVAILABLE, msg)

    def ack_invoice_open(self):
        msg = ERR_INVOICE_OPEN.format(invoice_id=self.get_invoice_id())
        self.ack(RC_ALREADY_PAID, msg)

    def ack_other(self, msg):
        self.ack(RC_OTHER, msg)
