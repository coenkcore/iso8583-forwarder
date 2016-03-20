from datetime import datetime
from ISO8583Server import (
    DateVar,
    DateTimeVar,
    )
from padl_fix_network import Network
from padl_fix_structure import (
    TRANSACTION_BITS,
    INQUIRY_CODE,
    PAYMENT_CODE,
    RC_OK,
    RC_INVALID_NUMBER,
    ERR_INVALID_NUMBER,
    RC_NOT_AVAILABLE,
    ERR_NOT_AVAILABLE,
    RC_ALREADY_PAID,
    ERR_ALREADY_PAID,
    ERR_AMOUNT,
    RC_INSUFFICIENT_FUND,
    ERR_INSUFFICIENT_FUND,
    ERR_REVERSAL_DONE,
    ERR_PAYMENT_NOT_FOUND,
    ERR_SETTLEMENT_DATE,
    ERR_TRANSACTION_TIME,
    )
import sys
sys.path.insert(0, '/usr/share/opensipkd/modules')
from tools import create_datetime


class Transaction(Network):
    def __init__(self, *args, **kwargs):
        self.settlement = DateVar()
        self.transaction_time = DateTimeVar()
        Network.__init__(self, *args, **kwargs)

    # Override
    def get_bit_definition(self):
        return TRANSACTION_BITS

    # Override
    def get_func_name(self):
        return self.is_echo_test_request() or self.is_inquiry() or \
               self.is_payment() or self.is_sign_on_request() or \
               self.is_sign_off_request() or \
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
        return self.getBit(3)

    def is_inquiry_response(self):
        return self.getMTI() == '0210' and \
            self.get_transaction_code() == INQUIRY_CODE

    def is_inquiry(self):
        if not self.is_transaction():
            return
        code = self.get_transaction_code()
        return code == INQUIRY_CODE and 'inquiry_response'

    def is_payment(self):
        if not self.is_transaction():
            return
        code = self.get_transaction_code()
        return code == PAYMENT_CODE and 'payment_response'

    def set_transaction_response(self):
        self.setMTI('0210')
        # Sesuai kolom yang berisi E (Equal) pada dokumentasi 
        self.copy([2, 3, 7, 11, 12, 13, 15, 18, 22, 32, 33, 35, 37, 41, 43, 49,
                   61, 62])

    def get_settlement(self):
        raw = self.get_value(15)
        self.settlement.set_raw(raw)
        try:
            return self.settlement.get_value()
        except ValueError:
            self.ack_settlement_date(raw)

    def get_transaction_time(self):
        raw = self.get_value(13) + self.get_value(12)
        self.transaction_time.set_raw(raw)
        try:
            return self.transaction_time.get_value()
        except ValueError:
            self.ack_transaction_time(raw)

    def get_invoice_id(self):
        return self.get_value(61).strip()

    def set_invoice_profile(self):
        self.setBit(62, self.invoice_profile.get_raw())

    def set_amount(self, n):
        self.setBit(4, n)

    def set_ntp(self, ntp):
        self.setBit(47, ntp)

    def get_ntb(self):
        return self.get_value(48)

    def get_stan(self):
        return self.get_value(11)

    def payment_response(self):
        self.copy([4, 48])

    def get_amount(self):
        return int(self.get_value(4))

    def get_channel_id(self):
        return int(self.get_value(18))

    def get_bank_ip(self):
        return self.conf['ip']

    def get_bank_id(self):
        return self.conf['id']

    def is_reversal(self):
        s = self.getMTI()
        return s[:2] == '04' and 'reversal_response'

    def set_reversal_response(self):
        s = self.from_iso.getMTI()
        mti = s[:2] + '1' + s[3:] # 0400 -> 0410, 0401 -> 0411
        self.setMTI(mti)
        self.copy(from_iso=self.from_iso)

    def ack_invalid_invoice_id(self):
        msg = ERR_INVALID_NUMBER.format(invoice_id=self.invoice_id_raw)
        return self.ack(RC_INVALID_NUMBER, msg)

    def ack_invoice_not_available(self):
        msg = ERR_NOT_AVAILABLE.format(invoice_id=self.invoice_id_raw)
        return self.ack(RC_NOT_AVAILABLE, msg)

    def ack_already_paid(self):
        msg = ERR_ALREADY_PAID.format(invoice_id=self.invoice_id_raw)
        return self.ack(RC_ALREADY_PAID, msg) 

    def ack_invalid_amount(self):
        msg = ERR_AMOUNT.format(invoice_id=self.invoice_id_raw,
                nominal=self.calc.total)
        return self.ack(RC_ALREADY_PAID, msg)

    def ack_insufficient_fund(self):
        msg = ERR_INSUFFICIENT_FUND.format(invoice_id=self.invoice_id_raw,
                bayar=self.from_iso.get_amount(),
                tagihan=self.calc.total)
        self.ack(RC_INSUFFICIENT_FUND, msg)

    def ack_already_canceled(self):
        msg = ERR_REVERSAL_DONE.format(invoice_id=self.invoice_id_raw)
        return self.ack(RC_ALREADY_PAID, msg) 

    def ack_payment_not_found(self):
        msg = ERR_PAYMENT_NOT_FOUND.format(invoice_id=self.invoice_id_raw)
        return self.ack(RC_NOT_AVAILABLE, msg) 

    def ack_settlement_date(self, raw):
        msg = ERR_SETTLEMENT_DATE.format(raw=[raw])
        self.error_func(msg)

    def ack_transaction_time(self, raw):
        msg = ERR_TRANSACTION_TIME.format(raw=[raw])
        self.error_func(msg)
