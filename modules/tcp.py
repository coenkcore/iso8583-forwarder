import os
import socket
from threading import Thread
try:
    from SocketServer import (
        BaseRequestHandler,
        TCPServer,
        ThreadingMixIn,
        )
except ImportError:
    from socketserver import (
        BaseRequestHandler,
        TCPServer,
        ThreadingMixIn,
        )
from time import (
    time,
    sleep,
    )
from datetime import datetime
import signal
import demon


def print_log(s, category='INFO'):
    print('%s %s %s' % (datetime.now().strftime('%Y-%m-%d %H:%M:%S,%f'),
                        category, s))


class BaseDaemon(object):
    def get_log(self):
        return

    def log_message(self, s):
        return s

    def log_info(self, s):
        msg = self.log_message(s)
        print_log(msg)
        log = self.get_log()
        log and log.info(msg)

    def log_error(self, s):
        msg = self.log_message(s)
        print_log(msg, 'ERROR')
        log = self.get_log()
        log and log.error(msg)


class Streamer(object):
    def __init__(self):
        self.raw = ''
        self.size = 0

    # Override please.
    def get(self, raw):
        return raw 

    # Override please.
    def set(self, raw):
        return raw


class NetworkDaemon(BaseDaemon):
    def __init__(self):
        self.remote_host = None
        self.network_timeout = 30
        self.connected_time = None 

    def process(self, raw):
        return

    def is_loop(self):
        sleep(1)
        return self.running

    def before_loop(self):
        self.streamer = self.get_streamer()
        self.last_log_message = None
        self.request.settimeout(self.get_timeout())
        self.running = True
        self.busy = False
        self.log_info('Begin loop')

    def after_loop(self):
        self.log_info('End loop')

    def get_receive_size(self):
        return 2048

    def get_timeout(self):
        return self.network_timeout 

    def run(self):
        self.before_loop()
        while self.is_loop():
            self.busy = True
            self.on_loop()
            self.busy = False
        self.after_loop()

    def on_loop(self):
        raw = self.receive_raw()
        if not raw:
            self.on_receive_empty_raw()
            return
        while True:
            raw = self.streamer.get(raw)
            if not raw:
                return
            raw = self.process(raw)
            if raw:
                raw = self.streamer.set(raw)
                self.send(raw)
            raw = '' # Siapa tahu ada self.streamer.raw

    def receive_raw(self):
        log_message = 'Waiting raw data %d bytes' % self.get_receive_size()
        if self.last_log_message != log_message: # Hemat log
            self.last_log_message = log_message
            self.log_info(log_message)
        try:
            raw = self.request.recv(self.get_receive_size())
            if raw:
                self.on_receive_raw(raw)
            return raw
        except socket.error as err:
            self.on_receive_error(err)
        except socket.timeout as err:
            self.on_receive_error(err)

    def get_streamer(self):
        return Streamer()

    def on_receive_raw(self, raw):
        self.connected_time = time()
        self.log_info('Receive %s' % [raw])

    def on_receive_error(self, err):
        self.on_socket_error(err)

    def on_receive_empty_raw(self):
        if self.is_timeout():
            self.on_timeout()

    def on_timeout(self):
        self.close_connection('timeout')

    def is_timeout(self):
        return time() - self.connected_time > self.get_timeout()

    def send(self, raw):
        self.log_info('Send %s' % [raw])
        try:
            self.request.sendall(raw)
            return True
        except socket.error as err:
            self.on_send_error(err)

    def on_send_error(self, err):
        self.on_socket_error(err)

    def on_socket_error(self, err):
        self.log_error(err)
        self.running = False

    def stop_loop(self, reason):
        self.running = False
        self.log_info('Close connection because %s' % reason)

    def close_connection(self, reason):
        self.stop_loop(reason)
        try:
            self.request.settimeout(1)
            self.request.close()
        except socket.error as err:
            self.log_error(err)

    def log_message(self, s):
        return '%s %d %s' % (self.remote_host, id(self), s)

##########
# Server #
##########
class Server(ThreadingMixIn, TCPServer, BaseDaemon):
    allow_reuse_address = True

    def __init__(self, *args, **kwargs):
        TCPServer.__init__(self, *args, **kwargs)
        BaseDaemon.__init__(self)
        self.clients = []

    def verify_request(self, request, client_address):
        client_ip = client_address[0]
        if self.is_allowed(client_ip):
            self.on_allowed(client_ip)
            return True
        self.on_denied(client_ip)

    def is_allowed(self, ip):
        return True

    def on_allowed(self, ip):
        self.log_info('%s allowed' % ip)

    def on_denied(self, ip):
        self.log_error('%s denied' % ip)

    def shutdown(self, reason=''):
        for client in self.clients:
            client.close_connection(reason)
        msg = 'Stop server'
        if reason:
            msg += ' because %s' % reason
        self.log_info(msg)
        TCPServer.shutdown(self)

    def add(self, client):
        self.clients.append(client)
        self.log_info('%s connected, currently %d connections' % (
            client.remote_host, len(self.clients)))

    def remove(self, client):
        self.clients.remove(client)
        self.log_info('%s closed, currently %d connections' % (
            client.remote_host, len(self.clients)))


class RequestHandler(BaseRequestHandler, NetworkDaemon):
    def __init__(self, *args, **kwargs):
        NetworkDaemon.__init__(self)
        BaseRequestHandler.__init__(self, *args, **kwargs)

    def handle(self): # Override BaseRequestHandler.handle()
        self.connected_time = time()
        self.remote_host = self.client_address[0]
        self.port = self.server.server_address[1]
        self.server.add(self)
        self.run()

    def after_loop(self):
        self.server.remove(self)
        NetworkDaemon.after_loop(self)


class ServerThread(BaseDaemon):
    def __init__(self, server):
        self.server = server
        # Start a thread with the server -- that thread will then start one
        # more thread for each request
        self.thread = Thread(target=server.serve_forever)
        # Exit the server thread when the main thread terminates
        self.thread.daemon = True

    def start(self):
        self.log_info('Server thread start')
        self.thread.start()
        self.server_host, self.server_port = self.server.socket.getsockname()
        self.log_info('Listen at %s port %d pid %d' % (self.server_host,
            self.server_port, os.getpid()))

    def stop(self, reason):
        self.server.shutdown(reason)
        self.log_info('Server thread stop')
        self.thread.join()

    # Bisa digunakan untuk memancing close connection.
    def send_dummy_request(self):
        class DummyClient(Client):
            def process(self, raw):
                Client.process(self, raw)
                self.close_connection('dummy request')

        client = DummyClient('127.0.0.1', self.server_port)
        client.run()


def stop_daemon(pid_file):
    pid = demon.isLive(pid_file)
    print(pid, pid_file)
    if not pid:
        return
    print('kill %d by signal' % pid)
    os.kill(pid, signal.SIGTERM)
    i = 0
    while i < 5:
        sleep(1)
        i += 1
        print i
        if not demon.isLive(pid_file):
            return
    print('kill %d by force' % pid)
    try:
        os.kill(pid, signal.SIGKILL)
    except OSError as err:
        print(err)



##########
# Client #
##########
class Client(NetworkDaemon):
    def __init__(self, host, port):
        super(Client, self).__init__()
        self.host = self.remote_host = host
        self.port = port
        self.address = (host, port)
        self.request = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        self.log_info('Connect to %s port %d' % (self.host, self.port))
        try:
            self.request.connect(self.address)
            return True
        except socket.error as err:
            self.on_connecting_error(err)
        except socket.timeout as err:
            self.on_connecting_error(err)

    def on_connecting_error(self, err):
        self.on_socket_error(err)

    def before_loop(self):
        super(Client, self).before_loop()
        if self.connect():
            self.connected_time = time()
        
        
class ClientThread(Thread, Client):
    def __init__(self, host, port):
        Client.__init__(self, host, port)
        Thread.__init__(self)
        self.daemon = True

    def run(self): # Agar tidak pakai Thread.run()
        Client.run(self)
