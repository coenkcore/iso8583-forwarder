import sys
sys.path[0:0] = ['/usr/share/pbb/modules']
from common import PBB as Data
sys.path[0:0] = ['/etc/pbb']
from config import timeout_seconds
from datetime import datetime
from pprint import pprint
from time import time, sleep
from StringIO import StringIO
import socket
import traceback


STATE_OFF, STATE_OPEN, STATE_TRX = range(3)


class Parser:
    def __init__(self):
        self.state = STATE_OPEN

    def _process(self, raw):
        self.from_iso = Data(self)
        data = self.from_iso.decode(raw)
        if not data: # Ada masalah format ISO, abaikan saja
            return
        if self.from_iso.is_echo_test_response():
            return
        if self.from_iso.is_sign_on_response() and self.from_iso.is_sign_ok():
            self.state = STATE_TRX
            return
        self.to_iso = Data(self, self.from_iso)
        func_name = self.from_iso.get_func_name()
        if not func_name:
            return self.error_func()
        # Transaksi harus didahului sign on 
        if not self.from_iso.is_network_request() and self.state != STATE_TRX:
            return self.error_link('Transaksi tanpa Sign On')
        func = getattr(self.to_iso, func_name)
        try:
            func()
        except OperationalError, err: # Biasanya database loss connection
            return self.error_link(err)
        if self.from_iso.is_sign_on_request():
            self.state = STATE_TRX
        elif self.from_iso.is_sign_off_request():
            self.state = STATE_OFF
        if not self.from_iso.is_network_response():
            return self.to_iso

    def _process_cli(self, raw):
        command = '%s "%s"' % (forwarder, raw)
        self.log_info('Forwarder send %s' % command)
        return getoutput(command)

    def _process_url(self, raw):
        p = {'iso': raw}
        url = '%s?%s' % (forwarder, urlencode(p))
        self.log_info('Forwarder send %s' % url)
        try:
            r = mechanize.urlopen(url)
            return r.read()
        except HTTPError, err:
            self.log_error(err)
        except URLError, err:
            self.log_error(err)

    def _process_forwarder(self, raw):
        if os.path.exists(forwarder):
            s = self._process_cli(raw)
        elif forwarder.find('http') == 0:
            s = self._process_url(raw)
        else:
            return self.error_link('Invalid forwarder %s' % forwarder)
        s = s or ''
        self.log_info('Forwarder receive %s' % [s])
        if not s:
            return self.error_link('Empty response')
        iso = Data(self)
        if iso.decode(s):
            return iso
        return self.error_link('Invalid ISO 8583')

    def process(self, raw):
        try:
            iso = self._process(raw)
        except:
            f = StringIO()
            traceback.print_exc(file=f)
            self.log_error(f.getvalue())
            f.close()
            return
        if not self.from_iso.is_response():
            return iso

    def error_raw(self):
        self.iso.error_raw()
        return self.iso

    def error_func(self): # Function not found
        self.to_iso.error_func()
        return self.to_iso

    def error_link(self, message=''):
        self.to_iso.error_link(message)
        #self.state = STATE_OFF
        return self.to_iso

    def log_info(self, s):
        log_info(s)

    def log_error(self, s):
        log_error(s)



class NetworkClient(object):
    def __init__(self):
        self.address = (host, port) 
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.log_info('Set timeout %d seconds' % timeout_seconds)
        self.sock.settimeout(timeout_seconds)
        self.running = True
        self.connecting_time = None
        self.connected_time = None
        self.sign_on_first = True
        self.sign_on_request_time = None 
        self.sign_on_response_ok = False
        self.echo_test_time = None
        self.last_network_error = None
        self.busy = False
        self.parser = Parser()

    def run(self):
        self.log_info('Client begin')
        awal = time()
        while self.running:
            if not self.is_connected() and not self.connect():
                break
            self.busy = True
            if not self.sign_on_response_ok and self.sign_on_first and \
                (not self.sign_on_request_time or \
                time() - self.sign_on_request_time > timeout_seconds):
                self.sign_on()
            raw = self.receive()
            if raw:
                self.echo_test_time = None
                self.process(raw)
                awal = time()
            elif self.echo_test_time:
                jeda = int(time() - self.echo_test_time)
                if jeda > timeout_seconds:
                    self.stop_thread('Echo test timeout, ' + \
                        'more than %d seconds ' % timeout_seconds + \
                        '(%d seconds).' % jeda)
            elif time() - awal > timeout_seconds:
                self.echo_test()
            self.busy = False
            sleep(1)
        self.log_info('Client end')

    def is_need_sign_on(self):
        return not self.sign_on_response_ok and self.sign_on_first and (\
            not self.sign_on_request_time or \
            time() - self.sign_on_request_time > timeout_seconds)

    def sign_on(self):
        iso = Data(self)
        iso.sign_on_request()
        self.send(iso)
        self.sign_on_request_time = time() 

    def echo_test(self):
        self.echo_test_time = time()
        iso = Data(self)
        iso.echo_test_request()
        self.send(iso)

    def sign_off(self):
        iso = Data(self)
        iso.sign_off_request()
        self.send(iso)

    def connect(self):
        self.connected_time = None
        self.connecting_time = time()
        self.log_info('Connecting with timeout %d seconds' % \
                  self.sock.gettimeout())
        try:
            self.sock.connect(self.address)
            self.connected_time = time()
            self.log_info('Connected')
            return True
        except socket.error, err:
            self.log_error(err)
        except socket.timeout, err:
            self.log_error(err)

    def _process(self, raw):
        iso = self.parser.process(raw)
        if iso:
            self.send(iso)
            return self.parser.from_iso.next_raw()
        if self.sign_on_first and self.sign_on_request_time and \
           self.parser.from_iso.is_sign_on_response():
            if self.parser.state == STATE_TRX:
                self.sign_on_response_ok = True 
            else:
                self.stop_thread('Sign On Response failed.')

    def process(self, raw):
        while self.running and raw:
            try:
                raw = self._process(raw)
            except:
                f = StringIO()
                traceback.print_exc(file=f)
                self.log_error(f.getvalue())
                f.close()
                self.sign_off()
                self.stop_thread('Unknown error found.')

    def send(self, iso):
        raw = iso.encode()
        raw = raw.upper()
        self.log_info('Send %s' % [raw])
        try:
            self.sock.sendall(raw)
        except socket.error, err:
            self.log_error(err)

    def receive(self):
        size = 2048
        self.log_info('Waiting raw data %d bytes' % size)
        try:
            raw = self.sock.recv(size)
            self.last_network_error = None
            if raw:
                self.log_info('Receive %s' % [raw])
                return raw
        except socket.timeout, err:
            self.log_error(err)
            if err == self.last_network_error:
                self.stop_thread('Too many timeout.')
            self.last_network_error = err
        except socket.error, err:
            self.log_error(err)
            self.last_network_error = err
            self.stop_thread('Network problem.')

    def disconnect(self):
        self.log_info('Disconnecting')
        try:
            self.sock.settimeout(1)
            self.sock.close()
        except socket.error, err:
            self.log_error(err)

    def stop_thread(self, reason):
        reason += ' Stop thread.'
        self.log_error(reason)
        self.running = False

    def join(self):
        self.disconnect()
        self.log_info('Thread join to main process')

    def is_connected(self):
        return self.connected_time

    def is_timeout(self):
        if not self.connecting_time or self.is_connected():
            return
        return time() - self.connecting_time > self.sock.gettimeout()

    def log_message(self, s):
        return '%s %s' % (self.address, s)

    def log_info(self, s):
        s = self.log_message(s)
        log_info(s)

    def log_error(self, s):
        s = self.log_message(s)
        log_error(s)



"""
class PBBTest(PBB):
    def ack(self, code='00', log_message=''):
        kini = datetime.now()
        self.setBit(7, kini.strftime('%m%d%H%M%S'))
        self.setBit(11, kini.strftime('%H%M%S'))
        self.setBit(39, code)
"""

def log_info(s):
    print('%s INFO %s' % (log_print_time(), s))

def log_error(s):
    print('%s ERROR %s' % (log_print_time(), s))

def log_print_time():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


host = '127.0.0.1'
port = 8584
client = NetworkClient()
try:
    client.run()
except KeyboardInterrupt, e:
    print(e)

sys.exit()
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
address = (host, port)
sock.connect(address)
 
print 'BRI kirim sign on request'
req_iso = PBBTest()
req_iso.sign_on_request()
pprint(req_iso.getBitsAndValues())
raw = req_iso.encode()
print 'Kirim ke', address, [raw]
sock.send(raw)
size = 2048
while True:
    raw = sock.recv(size)
    if raw:
        print 'Terima dari', address, [raw]
        resp_iso = PBBTest()
        resp_iso.decode(raw)
        pprint(resp_iso.getBitsAndValues())
        break
sys.exit()

print 'BJB kirim sign on response'
resp_iso = PBBTest(from_iso=req_iso)
func = getattr(resp_iso, req_iso.get_func_name())
func()
print 'MTI', resp_iso.getMTI()
pprint(resp_iso.getBitsAndValues())
print [resp_iso.getRawIso()]

print 'Pemda kirim echo test request'
req_iso = PBBTest()
req_iso.echo_test_request()
print 'MTI', req_iso.getMTI()
pprint(req_iso.getBitsAndValues())
print [req_iso.getRawIso()]

print 'BJB kirim echo test response'
resp_iso = PBBTest(from_iso=req_iso)
func = getattr(resp_iso, req_iso.get_func_name())
func()
print 'MTI', resp_iso.getMTI()
pprint(resp_iso.getBitsAndValues())
print [resp_iso.getRawIso()]
