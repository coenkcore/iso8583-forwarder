from types import DictType
from tools import FixLength
from network import Network
from common.transaction import BaseTransaction
from structure import (
    TRANSACTION_BITS,
    PBB_INQUIRY_CODE,
    PBB_PAYMENT_CODE,
    BPHTB_INQUIRY_CODE,
    BPHTB_PAYMENT_CODE,
    PADL_INQUIRY_CODE,
    PADL_PAYMENT_CODE,
    WEBR_INQUIRY_CODE,
    WEBR_PAYMENT_CODE,
    RC_INVALID_NUMBER,
    RC_ALREADY_PAID,
    RC_NOT_AVAILABLE,
    RC_INSUFFICIENT_FUND,
    ERR_INVALID_NUMBER,
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
    CABANG,
    )


METHODS = {
    PBB_INQUIRY_CODE:   'pbb_inquiry_request_handler',
    PBB_PAYMENT_CODE:   'pbb_payment_request_handler',
    BPHTB_INQUIRY_CODE: 'bphtb_inquiry_request_handler',
    BPHTB_PAYMENT_CODE: 'bphtb_payment_request_handler',
    PADL_INQUIRY_CODE:  'padl_inquiry_request_handler',
    PADL_PAYMENT_CODE:  'padl_payment_request_handler',
    WEBR_INQUIRY_CODE:  'webr_inquiry_request_handler',
    WEBR_PAYMENT_CODE:  'webr_payment_request_handler',
    }

REVERSAL_METHODS = {
    PBB_PAYMENT_CODE:   'pbb_reversal_request_handler',
    BPHTB_PAYMENT_CODE: 'bphtb_reversal_request_handler',
    PADL_PAYMENT_CODE:  'padl_reversal_request_handler',
    WEBR_PAYMENT_CODE:  'webr_reversal_request_handler',
    }

INQUIRY_CODES = (PBB_INQUIRY_CODE, BPHTB_INQUIRY_CODE, PADL_INQUIRY_CODE,
                 WEBR_INQUIRY_CODE)

PAYMENT_CODES = (PBB_PAYMENT_CODE, BPHTB_PAYMENT_CODE, PADL_PAYMENT_CODE,
                 WEBR_PAYMENT_CODE)

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

    def is_inquiry_request(self):
        if not self.is_transaction_request():
            return
        code = self.get_transaction_code()
        if code not in INQUIRY_CODES:
            return
        if code in METHODS:
            return METHODS[code]

    def is_inquiry_response(self):
        return self.get_transaction_code() in INQUIRY_CODES

    def is_payment_request(self):
        if not self.is_transaction_request():
            return
        code = self.get_transaction_code()
        if code not in PAYMENT_CODES:
            return
        if code in METHODS:
            return METHODS[code]

    def is_payment_response(self):
        return self.get_transaction_code() in PAYMENT_CODES

    def set_transaction_response(self):
        BaseTransaction.set_transaction_response(self)
        self.copy([47, 49, 59, 60, 61, 63, 102, 107])

    def set_payment_response(self):
        self.set_transaction_response()
        self.copy([4, 48, 62])
        self.set_ntp('')

    def is_reversal_request(self):
        if not BaseTransaction.is_reversal_request(self):
            return
        code = self.get_transaction_code()
        if code in METHODS:
            return REVERSAL_METHODS[code]

    def get_invoice_id(self):
        return self.get_value(61).strip()

    def set_invoice_profile(self, raw):
        self.setBit(62, raw)

    def get_ntb(self):
        return self.get_value(48)

    def set_ntb(self, v):
        self.setBit(48, v)

    def set_ntp(self, v):
        self.setBit(47, v)

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

    def get_cabang(self):
        f = FixLength(CABANG)
        f.set_raw(self.get_value(107))
        return f 

    def ack_invalid_number(self):
        msg = ERR_INVALID_NUMBER.format(
                invoice_id=self.from_iso.get_invoice_id())
        self.ack(RC_INVALID_NUMBER, msg)

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
