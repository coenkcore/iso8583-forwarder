from datetime import datetime
from ISO8583Server import (
    DateVar,
    DateTimeVar,
    )
from bphtb_fix_network import Network
from bphtb_fix_structure import (
    TRANSACTION_BITS,
    INQUIRY_CODE,
    PAYMENT_CODE,
    ERR_SETTLEMENT_DATE,
    ERR_TRANSMISSION_DATETIME,
    ERR_TRANSACTION_DATETIME,
    )


class Transaction(Network):
    def __init__(self, *args, **kwargs):
        self.settlement_date = DateVar()
        self.transaction_datetime = DateTimeVar()
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
        return self.get_value(3)

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
        # Sesuai kolom yang berisi E (Equal) pada PDF
        self.copy([2, 3, 7, 11, 12, 13, 15, 18, 22, 32, 33, 35, 37, 41, 42, 43,
                   47, 48, 49, 59, 60, 61, 62, 63, 102, 107])

    def get_transaction_datetime(self):
        raw = self.get_value(13) + self.get_value(12)
        self.transaction_datetime.set_raw(raw)
        try:
            return self.transaction_datetime.get_value()
        except ValueError:
            self.ack_transaction_datetime(raw)

    def get_settlement_date(self):
        raw = self.get_value(15)
        self.settlement_date.set_raw(raw)
        try:
            return self.settlement_date.get_value()
        except ValueError:
            self.ack_settlement_date(raw)

    def get_invoice_id(self):
        return self.get_value(62).strip()

    def get_channel_id(self):
        return int(self.get_value(18))

    def get_amount(self):
        return int(self.get_value(4))

    def get_stan(self):
        return self.get_value(11)

    def get_ntb(self): # Nomor Transaksi Bank
        return self.get_value(58)

    def get_bank_ip(self):
        if 'ip' in self.conf:
            return self.conf['ip']

    def is_reversal(self):
        s = self.getMTI()
        return s[:2] == '04' and 'reversal_response'

    def set_reversal_response(self):
        s = self.from_iso.getMTI()
        mti = s[:2] + '1' + s[3:] # 0400 -> 0410, 0401 -> 0411
        self.setMTI(mti)
        self.copy(from_iso=self.from_iso)
        
    def ack_settlement_date(self, raw):
        msg = ERR_SETTLEMENT_DATE.format(raw=[raw])
        self.error_func(msg)

    def ack_transmission_datetime(self, raw):
        msg = ERR_TRANSMISSION_DATETIME.format(raw=[raw])
        self.error_func(msg)

    def ack_transaction_datetime(self, raw):
        msg = ERR_TRANSACTION_DATETIME.format(raw=[raw])
        self.error_func(msg)
