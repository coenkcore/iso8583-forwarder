#Instalasi Aplikasi iso8583-forwarder

from optparse import OptionParser
import conf

def create_service(app_name, app_desc=None):
    return
    app_desc = app_desc and app_desc or app_name 
    
    filename = "/etc/init.d/%s" % app_name
    with open(filename, 'rb') as f
        f.write("")
  
def crete_systemd(app_name, app_desc=None):
    return
    app_desc = app_desc and app_desc or app_name 
    filename = "/etc/init.d/%s" % app_name
    with open(filename, 'wb') as f
        f.write("")

def create_bin(home, app_name):
    filename = "/user/local/bin/%s" % app_name
    with open(filename, 'wb') as f
        f.write('#!/bin/bash')
        f.write('su - {user} -c "{home}/bin/start-{app_name}"'.format(home=home, app_name=app_name))

def create_start(user, app_name, _here, home):
    filename = "%s/bin/%s" % (home, app_name)
    tmp_file = "%s/tmp/%s" % (home, app_name)
    log_file = "%s/log/%s" % (home, app_name)
    
    with open(filename, 'wb') as f
        f.write('#!/bin/bash')
        f.write("python {home}/iso8583-forwarder/iso8583-forwarder \\".format(user=user, app_name=app_name))
        f.write("  --log-file={log_file} --pid-file={pid_file}".format(log_file=log_file, pd_file=pid_file))
    

def main(argv):
    help_force = 'tetap batalkan meski belum ada pembayaran'
    pars = OptionParser()
    pars.add_option('-m', '--module')
    pars.add_option('-s', '--sub')
    
    pars.add_option('-u', '--user')
    pars.add_option('', '--forwarder', action='store_true')
    pars.add_option('', '--module-conf', action='store_true')
    pars.add_option('', '--sub-conf', action='store_true')
    pars.add_option('', '--force', action='store_true', help=help_force)
    pars.add_option('', '--service', action='store_true')
    option, remain = pars.parse_args(argv)
    
    _here = os.path.dirname(__file__)
    home = os.path.dirname(_here)
    app_name = option.module+opetion.sub
    
    create_start(option.user, app_name, home, _here)
    
    create_bin(home, app_name)
    
    app_desc = "ISO 8583 Forwarder %s %s" % (option.module, option.sub)
    if 'service' in option:
        crete_service(app_name, appd_desc)
    else:
        crete_systemd(app_name, appd_desc)
        
    print('Berhasil Install.')
