from ISO8583Server import (
    DateVar,
    DateTimeVar,
    TimeVar,
    )
from network import Network
from .structure import (
    BASE_TRANSACTION_BITS,
    RC_INVALID_NUMBER,
    RC_NOT_AVAILABLE,
    RC_ALREADY_PAID,
    ERR_SETTLEMENT_DATE,
    ERR_TRANSACTION_DATETIME,
    ERR_TRANSACTION_DATE,
    ERR_INVALID_BANK,
    ERR_INVALID_NUMBER,
    ERR_ALREADY_PAID,
    ERR_NOT_AVAILABLE,
    ERR_ISO_PAYMENT,
    )


class BaseTransaction(Network):
    def __init__(self, *args, **kwargs):
        self.settlement = DateVar()
        self.transaction_datetime = DateTimeVar()
        self.transaction_date = DateVar()
        self.transaction_time = TimeVar()
        Network.__init__(self, *args, **kwargs)

    # Override
    def get_bit_definition(self):
        return BASE_TRANSACTION_BITS

    # Override
    def get_func_name(self):
        return self.is_echo_test_request() or self.is_sign_on_request() or \
               self.is_sign_off_request() or self.is_inquiry_request() or \
               self.is_payment_request() or self.is_reversal_request()

    # Override
    def set_response(self):
        if self.from_iso.is_network_request():
            Network.set_response(self)
        elif self.from_iso.is_transaction_request():
            self.set_transaction_response()
        elif self.from_iso.is_reversal_request():
            self.set_reversal_response()

    # Override
    def setIsoContent(self, raw):
        Network.setIsoContent(self, raw)
        self.raw = raw

    def is_transaction_request(self):
        return self.getMTI() == '0200'

    def is_transaction_response(self):
        return self.getMTI() == '0210'

    def is_response(self):
        return Network.is_response(self) or self.is_transaction_response() or \
                self.is_reversal_response()

    def get_transaction_code(self):
        return self.get_value(3)

    def set_transaction_code(self, code):
        self.setBit(3, code)

    def get_inquiry_code(self):
        pass

    def is_inquiry_request(self):
        if not self.is_transaction_request():
            return
        code = self.get_transaction_code()
        return code == self.get_inquiry_code() and 'inquiry_request_handler'

    def is_inquiry_response(self):
        return self.get_transaction_code() == self.get_inquiry_code() 

    def get_payment_code(self):
        pass

    def is_payment_request(self):
        if not self.is_transaction_request():
            return
        code = self.get_transaction_code()
        return code == self.get_payment_code() and 'payment_request_handler'

    def is_payment_response(self):
        return self.get_transaction_code() == self.get_payment_code() 

    def set_transaction_response(self):
        self.setMTI('0210')
        # Sesuai kolom yang berisi E (Equal) pada PDF
        self.copy([2, 3, 7, 11, 12, 13, 15, 18, 22, 32, 33, 35, 37, 41, 42, 43])

    def set_transaction_request(self):
        self.setMTI('0200')
        self.set_transmission()
        self.set_stan()

    def get_settlement(self):
        raw = self.get_value(15)
        self.settlement.set_raw(raw)
        try:
            return self.settlement.get_value()
        except ValueError:
            self.ack_settlement_date(raw)

    def get_transaction_datetime_raw(self):
        return self.get_transaction_date_raw() + self.get_transaction_time_raw()

    def get_transaction_datetime(self):
        raw = self.get_transaction_datetime_raw()
        self.transaction_datetime.set_raw(raw)
        try:
            return self.transaction_datetime.get_value()
        except ValueError:
            self.ack_transaction_datetime()

    def get_transaction_time_raw(self):
        return self.get_value(12)

    def get_transaction_time(self):
        raw = self.get_transaction_time_raw()
        self.transaction_time.set_raw(raw)
        try:
            return self.transaction_time.get_value()
        except ValueError:
            self.ack_transaction_time()

    def get_transaction_date_raw(self):
        return self.get_value(13)

    def get_transaction_date(self):
        raw = self.get_transaction_date_raw()
        self.transaction_date.set_raw(raw)
        try:
            return self.transaction_date.get_value()
        except ValueError:
            self.ack_transaction_date()

    def get_channel(self):
        return int(self.get_value(18))

    def get_bank_id(self):
        return int(self.get_value(32))

    def get_forwarder(self):
        return self.get_value(33)

    def get_sequence(self):
        return self.get_value(37)

    def get_invoice_id(self):
        return self.get_value(61).strip()

    def get_amount(self):
        return int(self.get_value(4))

    def set_amount(self, v):
        self.setBit(4, v)

    def get_channel(self):
        return int(self.get_value(18)) # Merchant / Channel 

    def get_bank_ip(self):
        return self.conf['ip']

    def is_reversal_request(self):
        s = self.getMTI()
        return s[:3] == '040' and 'reversal_request_handler'

    def is_reversal_response(self):
        s = self.getMTI()
        return s[:3] == '041'

    def set_reversal_response(self):
        s = self.from_iso.getMTI()
        mti = s[:2] + '1' + s[3:] # 0400 -> 0410, 0401 -> 0411
        self.setMTI(mti)
        self.copy(from_iso=self.from_iso)
        self.copy([7, 12])

    def set_reversal_request(self):
        self.setMTI('0400')
        self.set_transmission()
        self.set_stan()

    def ack_settlement_date(self, raw):
        msg = ERR_SETTLEMENT_DATE.format(raw=[raw])
        self.ack_other(msg)

    def ack_transaction_datetime(self):
        raw = self.get_transaction_datetime_raw()
        msg = ERR_TRANSACTION_DATETIME.format(raw=[raw])
        self.ack_other(msg)

    def ack_transaction_date(self):
        raw = self.get_transaction_date_raw()
        msg = ERR_TRANSACTION_DATE.format(raw=[raw])
        self.ack_other(msg)

    def ack_transaction_time(self):
        raw = self.get_transaction_time_raw()
        msg = ERR_TRANSACTION_TIME.format(raw=[raw])
        self.ack_other(msg)

    def ack_invalid_number(self):
        msg = ERR_INVALID_NUMBER.format(
                invoice_id=self.from_iso.get_invoice_id())
        self.ack(RC_INVALID_NUMBER, msg)

    def ack_not_allowed(self):
        msg = ERR_INVALID_BANK.format(id=self.from_iso.get_bank_id())
        self.ack(RC_INVALID_NUMBER, msg)

    def ack_not_available(self):
        msg = ERR_NOT_AVAILABLE.format(invoice_id=self.from_iso.get_invoice_id())
        self.ack(RC_NOT_AVAILABLE, msg)

    def ack_already_paid(self):
        msg = ERR_ALREADY_PAID.format(invoice_id=self.from_iso.get_invoice_id())
        self.ack(RC_ALREADY_PAID)

    def ack_insufficient_fund(self, nilai_tagihan):
        msg = ERR_INSUFFICIENT_FUND.format(
                invoice_id=self.from_iso.get_invoice_id(),
                bayar=self.from_iso.get_amount(),
                tagihan=nilai_tagihan)
        self.ack(RC_INSUFFICIENT_FUND)

    def ack_iso_payment_not_found(self):
        self.ack(RC_NOT_AVAILABLE, ERR_ISO_PAYMENT.format(
            invoice_id=self.get_invoice_id()))
