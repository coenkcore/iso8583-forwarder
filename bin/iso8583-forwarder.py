#!/usr/bin/python

import os
import sys
import traceback
import imp
import signal
from StringIO import StringIO
from datetime import datetime
import demon
from threading import Thread
from optparse import OptionParser
from glob import glob
from time import (
    sleep,
    time,
    )
from tcp import (
    Server,
    ServerThread,
    RequestHandler,
    ClientThread,
    stop_daemon,
    BaseDaemon,
    )
sys.path.insert(0, '/usr/share/opensipkd/modules')
from tools import print_log
sys.path.insert(0, '/usr/share/opensipkd-forwarder/modules')
from streamer_loader import get_streamer_module


#################
# Common Daemon #
#################
class Common(object):
    def get_log(self):
        return log

    def log_message(self, s):
        name = ip_conf[self.remote_host]['name']
        return '%s %s %d %s' % (self.remote_host, name, id(self), s)

    def get_bank_log(self):
        name = ip_conf[self.remote_host]['name']
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
        self.echo_time = None
        hosts.add(self)
        if self.need_echo():
            self.echo()
        self.sign_on_time = False

    def _process(self, raw):
        parser = ParserThread(self, raw)
        parser.start()

    def process(self, raw):
        try:
            self._process(raw)
        except:
            f = StringIO()
            traceback.print_exc(file=f)
            self.log_error(f.getvalue())
            f.close()

    def after_loop(self):
        if not self.connected_time:
            return
        hosts.remove(self)

    def on_receive_raw(self, raw):
        self.echo_time = None

    def echo(self):
        self.echo_time = time()
        iso = Data(log_info=self.log_info,
                   log_error=self.log_error)
        iso.echo_test_request()
        self.send_iso(iso)

    def sign_on(self):
        iso = Data(log_info=self.log_info,
                   log_error=self.log_error)
        iso.sign_on_request()
        self.sign_on_time = time()
        self.send_iso(iso)

    def get_timeout(self):
        cfg = ip_conf[self.remote_host]
        return cfg.get('timeout', self.network_timeout) 

    def is_timeout(self):
        return time() - self.connected_time >= self.get_timeout() - 5

    def need_echo(self):
        cfg = ip_conf[self.remote_host]
        return cfg.get('need echo', True)

    def check_timeout(self):
        if not self.echo_time and self.is_timeout() and self.need_echo():
            self.echo()

    def check_job(self):
        try:
            func = getattr(iso_module, 'get_job')
        except AttributeError:
            return
        iso = func()
        if iso:
            self.send_iso(iso)

    def send_iso(self, iso):
        raw = iso.getRawIso()
        raw = self.streamer.set(raw)
        raw = raw.upper()
        func = self.get_send_func()
        try:
            return func(self, raw)
        except:
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
        return ip in ip_conf 

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

    def get_streamer(self):
        cls = ip_conf[self.remote_host]['streamer']
        return cls()

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

    def is_timeout(self):
        return Common.is_timeout(self)

    def get_send_func(self):
        return RequestHandler.send

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

    def get_streamer(self):
        cls = ip_conf[self.remote_host]['streamer']
        return cls()

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

    def is_timeout(self):
        return Common.is_timeout(self)

    def get_send_func(self):
        return ClientThread.send

#########
# Other #
#########
def out(sig=None, func=None):
    if running:
        del running[0] # Akhiri loop utama
    for host in hosts:
        host.close_connection('killed')

def check_connection():
    for ip in ip_conf:
        cfg = ip_conf[ip]
        if 'port' not in cfg:
            continue
        if ip in hosts:
            continue
        host = Client(cfg['ip'], cfg['port'])
        host.start()
        sleep(5)

def check_timeout():
    for host in hosts:
        if host.running:
            host.check_timeout()

def check_job():
    for host in hosts:
        if host.running:
            host.check_job()

def stop_thread(stopped_name=None):
    for host in hosts:
        if stopped_name:
            if stopped_name != host.conf['name']: 
                continue
        host.log_info('admin try to close when not busy')
        busy_timeout = host.get_timeout() # seconds
        is_force = True # tutup paksa ?
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
    for filename in glob('%s/*' % stop_dir):
        t = os.path.split(filename)
        name = t[-1]
        stop_thread(name)
        os.remove(filename)


class Host(object):
    def __init__(self):
        self.hosts = {} 

    def add(self, host):
        ip = host.remote_host
        host.conf = ip_conf[ip]
        count = ip in self.hosts and 2 or 1
        host.log_info('connected, currently %d connections' % count)
        if ip in self.hosts:
            old_host = self.hosts[ip]
            old_host.close_connection('new connection found')
            self.remove(old_host, True)
        self.hosts[ip] = host

    def remove(self, host, reconnect=False):
        ip = host.remote_host
        if ip in self.hosts:
            del self.hosts[ip]
        count = reconnect and 1 or 0
        host.log_info('closed, currently %d connections' % count)

    def __iter__(self): # for loop
        for ip in self.hosts:
            yield self.hosts[ip]

    def __contains__(self, ip): # in operator
        return ip in self.hosts

    def __getitem__(self, ip):
        return self.hosts[ip]


#################
# Parser Thread #
#################
class ParserThread(Thread, BaseDaemon, Common):
    def __init__(self, parent, raw):
        self.parent = parent
        self.get_log = parent.get_log
        self.remote_host = self.from_ip = parent.remote_host
        self.conf = ip_conf[self.from_ip]
        self.raw = raw
        BaseDaemon.__init__(self)
        Thread.__init__(self)

    def _run(self):
        from_iso = Data(log_info=self.log_info,
                        log_error=self.log_error)
        try:
            from_iso.setIsoContent(self.raw)
        except:
            self.log_exception()
            return
        #if not from_iso.is_transaction_response():
        #    if from_iso.is_response():
        #        if not self.parent.sign_on_time:
        #            self.parent.sign_on()
        #        return
        if from_iso.is_response():
            if not self.parent.sign_on_time:
                self.parent.sign_on()
            return
        iso = Data(from_iso=from_iso,
                log_info=self.log_info,
                log_error=self.log_error,
                conf=self.conf)
        try:
            iso.process()
        except:
            # Ada fatal error tidak perlu dijawab, biarkan timeout
            self.log_exception()
            return
        self.parent.send_iso(iso)

    def run(self):
        self._run()

    def log_info(self, s):
        BaseDaemon.log_info(self, s)
        Common.bank_log_info(self, s)

    def log_error(self, s):
        BaseDaemon.log_error(self, s)
        Common.bank_log_error(self, s)

    # Override
    def log_message(self, s):
        name = ip_conf[self.from_ip]['name']
        return '%s %s %s -> %s %s' % (self.conf['ip'], name, id(self.parent),
                    id(self), s)

    def log_exception(self):        
        f = StringIO()
        traceback.print_exc(file=f)
        self.log_error(f.getvalue())
        f.close()


##############
# Blok Utama #
##############
conf_file = '/etc/opensipkd/forwarder.py'
pid_file = '/var/run/iso8583-forwarder.pid'
log_dir = '/var/log/iso8583-forwarder'

pars = OptionParser()
pars.add_option('-c', '--conf-file', default=conf_file, help='default ' + conf_file)
pars.add_option('-p', '--pid-file', default=pid_file,
    help='default ' + pid_file)
pars.add_option('-l', '--log-dir', default=log_dir, help='default ' + log_dir)
pars.add_option('', '--stop', action='store_true', help='Stop daemon')
pars.add_option('', '--stop-thread', help='Stop thread name')
pars.add_option('', '--stop-all-thread', help='Stop all thread')
option, remain = pars.parse_args(sys.argv[1:])

conf_file = os.path.realpath(option.conf_file)
pid_file = os.path.realpath(option.pid_file)
log_dir = os.path.realpath(option.log_dir)

if option.stop:
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

if not conf.module_name:
    print('Sesuaikan module_name pada ' + conf_file)
    sys.exit()

iso_module = __import__(conf.module_name)
Data = iso_module.DbTransaction

pid = demon.make_pid(pid_file)
main_log_file = os.path.join(log_dir, 'main.log')
log = demon.Log(main_log_file)
if not os.path.exists(stop_dir):
    os.mkdir(stop_dir)

need_iso8583_server = False 
ip_conf = {}
hosts = Host() # Kumpulan request
logs = {} # Kumpulan log

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
    module = get_streamer_module(name)
    cfg['streamer'] = module.Streamer
    ip = cfg['ip']
    ip_conf[ip] = cfg
    if 'port' not in cfg:
        need_iso8583_server = True

if need_iso8583_server:
    # ISO 8583 Server
    server = AsServer(conf.iso8583_listen_address, Request)
    server_thread = AsServerThread(server)
    server_thread.start()

# Antisipasi kill
signal.signal(signal.SIGTERM, out)
running = [True]

try:
    while running: 
        check_connection()
        check_timeout()
        check_job()
        watch_stop_dir()
        sleep(5)
except KeyboardInterrupt:
    out()
