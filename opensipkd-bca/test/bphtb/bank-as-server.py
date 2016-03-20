# Daemon ini adalah simulasi server BJB.

import os
import sys
timeout_seconds = 30
from glob import glob
from threading import Thread
from time import (
    sleep,
    time,
    )
from datetime import datetime
from test_inquiry import InquiryTest
from tcp import (
    Server,
    RequestHandler,
    )
from pprint import pprint
import socket
from optparse import OptionParser


def get_custom_module(name):
    modules_path = os.path.dirname(__file__)
    filename = '%s/%s.py' % (modules_path, name) 
    if not os.path.exists(filename):
        return
    try:
        return __import__(name)
    except ImportError:
        return


class TestServer(Server):
    def verify_request(self, request, client_address):
        print('Connection from %s' % client_address[0])
        return True


class Request(RequestHandler):
    def before_loop(self):
        self.connected_time = time() 
        self.echo_test_time = None
        self.running = True
        self.timeout_need_echo = 30
        self.invoice_id = None 
        self.conf = {'module': module}
        clients.append(self)
        self.log_info('connected, currently %d connections' % len(clients))
        sleep(1)

    def after_loop(self):
        clients.remove(self)
        self.log_info('closed, currently %d connections' % len(clients))

    def state_loop(self):
        return self.running

    def process(self, raw):
        self.connected_time = time()
        self.echo_test_time = None
        from_iso = InquiryTest(self)
        from_iso.decode(raw)
        pprint(from_iso.getBitsAndValues())
        if from_iso.is_response():
            return
        func_name = from_iso.get_func_name()
        to_iso = InquiryTest(self, from_iso)
        if func_name:
            print('Function %s' % func_name)
            func = getattr(to_iso, func_name)
            func()
            if to_iso.is_sign_ok():
                self.invoice_id = invoice_id
        else:
            print('Function not found')
            to_iso.set_response()
            to_iso.error_func()
        return to_iso

    def send(self, iso):
        raw = iso.getNetworkISO()
        self.log_info('Send %s' % [raw])
        pprint(iso.getBitsAndValues())
        try:
            self.request.sendall(raw)
            return True
        except socket.error, err:
            self.log_info(err)

    def now(self):
        return datetime.now().strftime('%d-%m-%Y %H:%M:%S')

    def log_info(self, s):
        print('%s INFO %s %s' % (self.now(), self.client_address[0], s))

    def log_error(self, s):
        print('%s ERROR %s %s' % (self.now(), self.client_address[0], s))

    def is_timeout(self):
        return time() - self.connected_time > self.timeout_need_echo 

    def is_echo_timeout(self):
        return time() - self.echo_test_time > timeout_seconds

    def echo_test(self):
        self.echo_test_time = time()
        iso = InquiryTest(self)
        iso.echo_test_request()
        self.running = self.send(iso)
        if not self.running:
            self.close_connection('send echo test failed')

    def check_timeout(self):
        if self.echo_test_time:
            if self.is_echo_timeout():
                self.close_connection('echo timeout')
        elif self.is_timeout():
            self.echo_test()

    def close_connection(self, reason):
        self.log_info('Close connection because %s' % reason)
        self.request.close()

    def invoice(self):
        iso = InquiryTest(self)
        iso.invoice(self.invoice_id)
        self.send(iso)
        self.invoice_id = None

    def sign_off(self):
        iso = InquiryTest(self)
        iso.sign_off_request()
        self.send(iso)


def out():
    for conn in clients:
        conn.sign_off()
        print('Close %s' % conn.client_address[0])
        conn.request.close()
    print('Shutdown')
    listener.shutdown()
    del running[0]


def inquiry():
    client = clients[-1] # client terakhir
    if client.invoice_id:
        client.invoice()


client = 'bjb'
invoice_id = '3278003011017029502012'
pars = OptionParser()
pars.add_option('-c', '--client', default=client, help='Nama bank')
pars.add_option('-i', '--invoice-id', default=invoice_id)

option, remain = pars.parse_args(sys.argv[1:])
client = option.client
invoice_id = option.invoice_id
module = get_custom_module(client)

running = [True]
clients = []
listen_address = ('0.0.0.0', 10002)
listener = TestServer(listen_address, Request)
listener_thread = Thread(target=listener.serve_forever)
listener_thread.daemon = True
listener_thread.start()
print('Listen at %s %s' % listen_address)
try:
    while running:
        if clients:
            inquiry()
        clients and clients[0].check_timeout()
        sleep(1)
except KeyboardInterrupt:
    out()
