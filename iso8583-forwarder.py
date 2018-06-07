import os
import sys
import traceback
import imp
import signal
import gc
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
from datetime import datetime
from threading import Thread
from optparse import OptionParser
from glob import glob
from time import (
    sleep,
    time,
    )
import pathmagic
import demon
from tcp import (
    Server,
    ServerThread,
    RequestHandler,
    ClientThread,
    stop_daemon,
    BaseDaemon,
    )
from tools import print_log
from streamer_loader import get_streamer_module


# gc.set_debug(gc.DEBUG_LEAK)
gc.enable()


def join_ip_port(ip, port):
    return ':'.join([ip, str(port)])


#################
# Common Daemon #
#################
class Common(object):
    def get_log(self):
        return log

    def get_conf(self):
        ip_port = join_ip_port(self.remote_host, self.port)
        return ip_conf[ip_port]

    def get_conf_val(self, key):
        cfg = self.get_conf()
        return cfg[key]

    def get_streamer(self):
        cls = self.get_conf_val('streamer')
        return cls()

    def log_message(self, s):
        cfg = self.get_conf()
        name = cfg['name']
        return '%s %s %d %s' % (self.remote_host, name, id(self), s)

    def get_bank_log(self):
        cfg = self.get_conf()
        name = cfg['name']
        return logs[name]

    def bank_log_info(self, s):
        bank_log = self.get_bank_log()
        s = self.log_message(s)
        bank_log.info(s)

    def bank_log_error(self, s):
        bank_log = self.get_bank_log()
        s = self.log_message(s)
        bank_log.error(s)

    def before_loop(self):
        if not self.connected_time:
            return
        self.job = self.create_job_instance()
        hosts.add(self)
        self.job.before_loop()

    def _process(self, raw):
        parser = ParserThread(self, raw)
        parser.start()

    def process(self, raw):
        try:
            self._process(raw)
        except Exception:
            f = StringIO()
            traceback.print_exc(file=f)
            self.log_error(f.getvalue())
            f.close()

    def after_loop(self):
        pass

    def on_receive_raw(self, raw):
        self.job.on_receive_raw(raw)

    def get_timeout(self):
        cfg = self.get_conf()
        return cfg.get('timeout', self.network_timeout)

    def create_job_instance(self):
        module = self.get_conf_val('iso_module')
        return module.Job(self)

    def check_job(self):
        iso = self.job.get_iso()
        iso and self.send_iso(iso)

    def send_iso(self, iso):
        raw = iso.getRawIso()
        raw = raw.upper()
        raw = str(raw)  # Jangan sampai unicode
        streamer = self.get_streamer()
        raw = streamer.set(raw)
        func = self.get_send_func()
        try:
            return func(self, raw)
        except Exception:
            f = StringIO()
            traceback.print_exc(file=f)
            self.log_error(f.getvalue())
            f.close()


##########################
# Sebagai network server #
##########################
class AsServerThread(ServerThread):
    # Override
    def get_log(self):
        return log


class AsServer(Server):
    # Override
    def is_allowed(self, ip):
        return ip in allowed_ips

    # Override
    def get_log(self):
        return log

    def log_message(self, s):
        return '%s (server)' % s


class Request(RequestHandler, Common):
    def get_log(self):
        return Common.get_log(self)

    def log_message(self, s):
        return Common.log_message(self, s)

    def get_bank_log(self):
        return Common.get_bank_log(self)

    def log_info(self, s):
        RequestHandler.log_info(self, s)
        Common.bank_log_info(self, s)

    def log_error(self, s):
        RequestHandler.log_error(self, s)
        Common.bank_log_error(self, s)

    def before_loop(self):
        RequestHandler.before_loop(self)
        Common.before_loop(self)

    def process(self, raw):
        return Common.process(self, raw)

    def after_loop(self):
        RequestHandler.after_loop(self)
        Common.after_loop(self)

    def on_receive_raw(self, raw):
        RequestHandler.on_receive_raw(self, raw)
        Common.on_receive_raw(self, raw)

    def get_timeout(self):
        return Common.get_timeout(self)

    def get_send_func(self):
        return RequestHandler.send

    def get_streamer(self):
        return Common.get_streamer(self)


##########################
# Sebagai network client #
##########################
class Client(ClientThread, Common):
    def get_log(self):
        return Common.get_log(self)

    def log_message(self, s):
        return Common.log_message(self, s)

    def get_bank_log(self):
        return Common.get_bank_log(self)

    def log_info(self, s):
        ClientThread.log_info(self, s)
        Common.bank_log_info(self, s)

    def log_error(self, s):
        ClientThread.log_error(self, s)
        Common.bank_log_error(self, s)

    def before_loop(self):
        ClientThread.before_loop(self)
        Common.before_loop(self)

    def process(self, raw):
        return Common.process(self, raw)

    def after_loop(self):
        ClientThread.after_loop(self)
        Common.after_loop(self)

    def on_receive_raw(self, raw):
        ClientThread.on_receive_raw(self, raw)
        Common.on_receive_raw(self, raw)

    def get_timeout(self):
        return Common.get_timeout(self)

    def get_send_func(self):
        return ClientThread.send

    def get_streamer(self):
        return Common.get_streamer(self)


#########
# Other #
#########
def out(sig=None, func=None):
    if sig:
        reason = 'Kill by signal {}'.format(sig)
    else:
        reason = 'Kill by keyboard interrupt'
    for port in servers:
        server_thread = servers[listen_port]
        server_thread.stop(reason)
        sleep(1)
    if running:
        del running[0]  # Akhiri loop utama
    for ip_port, host in hosts:
        host.close_connection('killed')
        sleep(1)


def check_connection():
    for ip_port in ip_conf:
        cfg = ip_conf[ip_port]
        if ip_port in hosts:
            index = -1
            while True:
                index += 1
                if not hosts[index:]:
                    break
                this_ip_port, host = hosts[index]
                if this_ip_port != ip_port:
                    continue
                if host.running:
                    continue
                hosts.remove(index)
                break
            continue
        if cfg['listen']:
            continue
        host = Client(cfg['ip'], cfg['port'])
        host.start()
        sleep(5)


def check_timeout():
    for ip_port, host in hosts:
        if host.running:
            host.check_timeout()


def check_job():
    for ip_port, host in hosts:
        if host.running:
            host.check_job()


def stop_thread(stopped_name=None):
    for ip_port, host in hosts:
        if stopped_name:
            if stopped_name != host.conf['name']:
                continue
        host.log_info('admin try to close when not busy')
        busy_timeout = host.get_timeout()  # seconds
        is_force = True  # tutup paksa ?
        awal = time()
        while time() - awal < busy_timeout:
            if not host.busy:
                is_force = False
                break
            sleep(0.5)
        if is_force:
            host.close_connection('forcibly closed by admin')
        else:
            host.close_connection('closed by admin')


def watch_stop_dir():
    pattern = os.path.join(stop_dir, '*')
    for filename in glob(pattern):
        t = os.path.split(filename)
        name = t[-1]
        stop_thread(name)
        os.remove(filename)


class Host(object):
    def __init__(self):
        self.hosts = []
        self.unused = []

    def count(self, ip_port):
        count = 0
        for this_ip_port, this_host in self.hosts:
            if this_ip_port == ip_port:
                count += 1
        return count

    def get_first(self, ip_port):
        index = -1
        for this_ip_port, host in self.hosts:
            index += 1
            if this_ip_port == ip_port:
                return host, index
        return None, None

    def get_last(self, ip_port):
        index = -1
        found_host = found_index = None
        for this_ip_port, host in self.hosts:
            index += 1
            if this_ip_port == ip_port:
                found_host = host
                found_index = index
        return found_host, found_index

    def add(self, host):
        ip_port = join_ip_port(host.remote_host, host.port)
        old_host, index = self.get_first(ip_port)
        host.conf = ip_conf[ip_port]
        self.hosts.append([ip_port, host])
        count = self.count(ip_port)
        host.log_info('connected, currently {c} connections'.format(c=count))
        if not old_host:
            return
        old_host.close_connection('new connection found')
        sleep(2)

    def remove(self, index):
        ip_port, host = self.hosts[index]
        del self.hosts[index][0]
        del self.hosts[index][0]
        del self.hosts[index]
        sleep(0.1)
        count = self.count(ip_port)
        host.log_info('closed, currently %d connections' % count)

    def __iter__(self):  # for loop
        for ip_port, host in self.hosts:
            yield [ip_port, host]

    def __contains__(self, ip_port):  # in operator
        host, index = self.get_first(ip_port)
        return index > -1

    def __getitem__(self, s):
        if isinstance(s, str):  # key like dictionary
            ip_port = s
            host, index = self.get_last(ip_port)
            return host
        return self.hosts[s]  # slice like list


#################
# Parser Thread #
#################
class ParserThread(Thread, BaseDaemon, Common):
    def __init__(self, parent, raw):
        self.parent = parent
        self.get_log = parent.get_log
        self.remote_host = parent.remote_host
        self.raw = raw
        BaseDaemon.__init__(self)
        Thread.__init__(self)

    def run(self):
        iso = self.parent.job.iso_from_raw(self.raw)
        if iso:
            self.parent.send_iso(iso)

    def log_info(self, s):
        BaseDaemon.log_info(self, s)
        Common.bank_log_info(self, s)

    def log_error(self, s):
        BaseDaemon.log_error(self, s)
        Common.bank_log_error(self, s)

    # Override
    def log_message(self, s):
        name = self.get_conf_val('name')
        return '%s %s %s -> %s %s' % (
                self.remote_host, name, id(self.parent), id(self), s)


##############
# Blok Utama #
##############
conf_file = os.path.join('conf', 'forwarder.py')
pid_file = 'iso8583-forwarder.pid'
log_dir = 'logs'

pars = OptionParser()
pars.add_option(
    '-c', '--conf-file', default=conf_file, help='default ' + conf_file)
pars.add_option(
    '-p', '--pid-file', default=pid_file, help='default ' + pid_file)
pars.add_option('-l', '--log-dir', default=log_dir, help='default ' + log_dir)
pars.add_option('', '--stop', action='store_true', help='Stop daemon')
pars.add_option('', '--stop-thread', help='Stop thread name')
pars.add_option('', '--stop-all-thread', help='Stop all thread')
option, remain = pars.parse_args(sys.argv[1:])

conf_file = os.path.realpath(option.conf_file)
pid_file = os.path.realpath(option.pid_file)
log_dir = os.path.realpath(option.log_dir)

if option.stop:
    print('Stop Daemon')
    stop_daemon(pid_file)
    sys.exit()

stop_dir = os.path.splitext(pid_file)[0] + '-stop'

if option.stop_thread:
    filename = os.path.join(stop_dir, option.stop_thread)
    f = open(filename, 'w')
    f.close()
    print('Kill thread signal sent. See log file.')
    sys.exit()

conf = imp.load_source('conf', conf_file)

pid = demon.make_pid(pid_file)
if not os.path.exists(log_dir):
    os.mkdir(log_dir)
main_log_file = os.path.join(log_dir, 'main.log')
log = demon.Log(main_log_file)
if not os.path.exists(stop_dir):
    os.mkdir(stop_dir)

listen_ports = []
ip_conf = {}
allowed_ips = []
hosts = Host()  # Kumpulan request
logs = {}  # Kumpulan log

for name in conf.host:
    cfg = conf.host[name]
    if 'active' in cfg:
        if not cfg['active']:
            continue
    else:
        cfg['active'] = True
    log_file = os.path.join(log_dir, name + '.log')
    logs[name] = demon.Log(log_file)
    cfg['name'] = name
    if 'streamer' in cfg:
        streamer_name = cfg['streamer']
    else:
        streamer_name = name
    module = get_streamer_module(streamer_name)
    cfg['streamer'] = module.Streamer
    if 'module' in cfg:
        module_name = cfg['module']
    else:
        module_name = 'network'
        print('Key module tidak ada jadi gunakan default yaitu {s}'.format(
            s=module_name))
    cfg['iso_module'] = iso_module = __import__(module_name)
    ip = cfg['ip']
    port = cfg['port']
    ip_port = join_ip_port(ip, cfg['port'])
    is_server = 'listen' in cfg and cfg['listen']
    cfg['listen'] = is_server
    if is_server:
        if port not in listen_ports:
            listen_ports.append(port)
        if ip not in allowed_ips:
            allowed_ips.append(ip)
    else:
        ip_port = join_ip_port(ip, cfg['port'])
        if ip_port in ip_conf:
            print('IP {} port {} ganda. Perbaiki konfigurasi.'.format(
                ip, port))
            sys.exit()
        print('Client from IP {} port {}'.format(ip, port))
    ip_conf[ip_port] = cfg

servers = {}
for listen_port in listen_ports:
    listen_address = ('0.0.0.0', listen_port)
    server = AsServer(listen_address, Request)
    server_thread = AsServerThread(server)
    server_thread.start()
    servers[listen_port] = server_thread

# Antisipasi kill
signal.signal(signal.SIGTERM, out)
running = [True]

try:
    while running:
        check_connection()
        check_job()
        watch_stop_dir()
        sleep(5)
except KeyboardInterrupt:
    out()
os.remove(pid_file)
