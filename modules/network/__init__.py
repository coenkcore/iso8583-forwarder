from time import time
from datetime import datetime
from ISO8583.ISOErrors import BitNotSet
from ISO8583Server import (
    Data,
    DateTimeVar,
    )
from structure import (
    NETWORK_BITS,
    RC_OK,
    RC_OTHER_ERROR,
    )
from tools import (
    create_datetime,
    exception_message,
    )


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
        return self.is_echo_test_request() or self.is_sign_on_request() or \
               self.is_sign_off_request()

    def process(self):
        func_name = self.from_iso.get_func_name()
        if func_name:
            func = getattr(self, func_name)
            func()
        else:
            self.ack_function_not_found()

    def is_response(self):
        return self.is_network_response()

    def set_response(self):
        if self.from_iso.is_network_request():
            self.set_network_response()

    def is_ok_response(self):
        try:
            return self.getBit(39) == RC_OK 
        except BitNotSet:
            self.log_error('Bit 39 tidak ada.')

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

    def get_stan(self):
        return self.get_value(11)

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

    ###################
    # Acknowledgement #
    ###################
    def ack(self, code=RC_OK, log_message=''):
        self.setBit(39, code)
        self.set_transmission()
        if log_message:
            if int(code):
                self.log_error(log_message)
            else:
                self.log_info(log_message)

    def ack_other(self, msg):
        self.ack(RC_OTHER_ERROR, msg)

    def ack_function_not_found(self):
        self.ack_other('Fungsi tidak ditemukan')

    def ack_unknown(self):
        s = exception_message()
        self.log_error(s)
        self.ack_other('Unknown')


class Job(object):
    def __init__(self, parent):
        self.parent = parent
        self.log_info = parent.log_info
        self.log_error = parent.log_error
        self.conf = parent.get_conf()
        self.echo_time = None 
        self.sign_on_time = False
        self.do_echo = False

    def get_iso_class(self):
        return Network

    def create_iso(self, **kwargs):
        cls = self.get_iso_class()
        return cls(log_info=self.log_info, log_error=self.log_error,
                   conf=self.conf, **kwargs)

    # Dipanggil iso8583-forwarder.py
    def get_iso(self):
        if self.do_echo:
            self.do_echo = False
            return self.echo_request()
        if not self.is_need_echo():
            return
        timeout_seconds = self.conf.get('timeout', self.parent.network_timeout)
        jeda = time() - self.parent.connected_time
        is_timeout = jeda >= timeout_seconds - 5
        if not self.echo_time and is_timeout:
            return self.echo_request()

    # Dipanggil iso8583-forwarder.py
    def iso_from_raw(self, raw):
        from_iso = self.create_iso()
        try:
            from_iso.setIsoContent(raw)
        except:
            return self.log_exception()
        if from_iso.is_response():
            if not self.sign_on_time:
                return self.sign_on_request()
            return
        iso = self.create_iso(from_iso=from_iso)
        try:
            iso.process()
            return iso
        except:
            # Ada fatal error tidak perlu dijawab, biarkan timeout
            self.log_exception()

    # Dipanggil iso8583-forwarder.py
    def on_receive_raw(self, raw):
        self.echo_time = None

    # Dipanggil iso8583-forwarder.py
    def before_loop(self):
        if self.is_need_echo():
            self.do_echo = True

    def is_need_echo(self):
        return self.conf.get('need echo', True)

    def echo_request(self):
        self.echo_time = time()
        iso = self.create_iso()
        iso.echo_test_request()
        return iso

    def sign_on_request(self):
        iso = self.create_iso()
        iso.sign_on_request()
        self.sign_on_time = time()
        return iso

    def log_exception(self):
        s = exception_message()
        self.log_error(s)
