from datetime import datetime
from ISO8583.ISOErrors import BitNotSet
from ISO8583Server import (
    Data,
    DateTimeVar,
    )
from pbb_structure import (
    NETWORK_BITS,
    RC_OK,
    RC_LINK_DOWN,
    RC_OTHER_ERROR,
    )
import sys
sys.path.insert(0, '/usr/share/opensipkd/modules')
from tools import create_datetime


class Network(Data):
    def __init__(self, *args, **kwargs):
        if 'log_info' in kwargs:
            self.log_info = kwargs['log_info']
            del kwargs['log_info']
        if 'log_error' in kwargs:
            self.log_error = kwargs['log_error']
            del kwargs['log_error']
        if 'conf' in kwargs:
            self.conf = kwargs['conf']
            del kwargs['conf']
        else:
            self.conf = {}
        Data.__init__(self, *args, **kwargs)
        self.raw = ''
        bits = self.get_bit_definition()
        for bit in bits: 
            short_name, long_name, type_, size, format_ = bits[bit]
            self.redefineBit(bit, short_name, long_name, type_, size, format_)
        self.transmission = DateTimeVar()
        if self.from_iso:
            self.set_response()

    def getRawIso(self):
        return str(Data.getRawIso(self)).upper()

    def get_bit_definition(self):
        return NETWORK_BITS

    def get_func_name(self):
        return self.is_echo_test_request() or \
               self.is_sign_on_request() or \
               self.is_sign_off_request()

    def process(self):
        func_name = self.from_iso.get_func_name()
        if func_name:
            func = getattr(self, func_name)
            func()
        else:
            self.error_func()

    def is_response(self):
        return self.is_network_response()

    def set_response(self):
        if self.from_iso.is_network_request():
            self.set_network_response()

    def ack(self, code=RC_OK, log_message=''): # acknowledgment / standard return 
        self.setBit(39, code)
        self.set_transmission()
        if log_message:
            if int(code):
                self.log_error(log_message)
            else:
                self.log_info(log_message)

    def is_ok_response(self):
        try:
            return self.getBit(39) == RC_OK 
        except BitNotSet:
            self.log_error('Bit 39 tidak ada.')

    def error_func(self):
        self.ack(RC_OTHER_ERROR, 'Function not found')

    def error_link(self, message=''):
        self.ack(RC_LINK_DOWN, message)

    def set_transmission(self):
        kini = datetime.now()
        self.setBit(7, kini.strftime('%m%d%H%M%S'))

    def get_transmission(self):
        raw = self.get_value(7)
        self.transmission.set_raw(raw)
        # without time zone
        t = self.transmission.get_value()
        # with time zone
        return create_datetime(t.year, t.month, t.day, t.hour, t.minute, t.second)

    def set_stan(self): # System Trace Audit Number
        kini = datetime.now()
        self.setBit(11, kini.strftime('%H%M%S'))

    ###########
    # Network #
    ###########
    def set_network_request(self):
        self.setMTI('0800')
        self.set_transmission()
        self.set_stan()

    def set_network_response(self):
        self.setMTI('0810')
        self.copy([7, 11, 70])

    def set_func_code(self, code):
        self.set_network_request()
        self.setBit(70, code)

    def get_func_code(self):
        return self.getBit(70)

    def is_network_request(self):
        return self.getMTI() == '0800'

    def is_network_response(self):
        return self.getMTI() == '0810' 

    ###################
    # Network Sign On #
    ###################
    def is_sign_on_request(self):
        return self.is_network_request() and \
               self.get_func_code() == '001' and \
               'sign_on_response'

    def is_sign_on_response(self):
        return self.is_network_response() and \
               self.get_func_code() == '001'

    def sign_on_request(self):
        self.set_func_code('001')

    def sign_on_response(self):
        self.set_network_response()
        self.ack()

    #####################
    # Network Echo Test #
    #####################
    def is_echo_test_request(self):
        return self.is_network_request() and \
               self.get_func_code() == '301' and \
               'echo_test_response'

    def is_echo_test_response(self):
        return self.is_network_response() and \
               self.get_func_code() == '301'

    def is_echo_test(self):
        return self.is_echo_test_request() or self.is_echo_test_response()

    def echo_test_request(self):
        self.set_func_code('301')

    def echo_test_response(self):
        self.set_network_response()
        self.ack()

    ####################
    # Network Sign Off #
    ####################
    def is_sign_off_request(self):
        return self.is_network_request() and \
               self.get_func_code() == '002' and \
               'sign_off_response'

    def is_sign_off_response(self):
        return self.is_network_request() and self.get_func_code() == '002'

    def is_sign_off(self):
        return self.is_sign_off_request() or self.is_sign_off_response()

    def sign_off_request(self):
        self.set_func_code('002')

    def sign_off_response(self):
        self.set_network_response()
        self.ack()
