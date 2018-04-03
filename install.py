#Instalasi Aplikasi iso8583-forwarder
import sys
import os
from optparse import OptionParser
from pwd import getpwnam  

def create_bat(home, app_name):
    pid_file = "%s/tmp/%s.pid" % (home, app_name)
    log_file = "%s/log/%s" % (home, app_name)
    filename = "%s/bin/start-%s.bat" %(home,app_name)
    with open(filename, 'wb') as f:
        f.write("@echo off\n")
        f.write("set folder=\"%s\"\n" % home)
        f.write("set log_file=\"%%folder%%\\log\\%s\n" % app_name)
        f.write("set tmp_file=\"%%folder%%\\tmp\\%s.pid\n" % app_name)
        f.write("cd %folder%\iso8583-forwarder\n")
        f.write("python iso8583-forwarder.py --pid-file=%%tmp_file%% --log-dir=%%log_file%% %%*")
        f.close()

def create_service(user, home, app_name):
    pid_file = "%s/tmp/%s.pid" % (home, app_name)
    log_file = "%s/log/%s" % (home, app_name)
    filename = "/etc/init.d/%s" % app_name
    with open(filename, 'wb') as f:
        f.write("#!/bin/sh\n")
        f.write("\n")
        f.write("### BEGIN INIT INFO\n")
        f.write("# Provides:          {app_name}\n".format(app_name=app_name))
        f.write("# Required-Start:    cron\n")
        f.write("# Required-Stop:     cron\n")
        f.write("# Default-Start:     2 3 4 5\n")
        f.write("# Default-Stop:      0 1 6\n")
        f.write("# Short-Description: ISO 8583 Forwarder\n")
        f.write("# Description:       Aplikasi {app_name}\n".format(app_name=app_name.upper()))
        f.write("### END INIT INFO\n")
        f.write("\n")
        f.write("USER=\"{user}\"\n".format(user=user))
        f.write("BIN=\"{home}/bin/{app_name}\"\n".format(home=home, app_name=app_name))
        f.write("PID=\"{pid_file}\"\n".format(pid_file=pid_file))
        f.write("DESC=\"Aplikasi {app_name}\"\n".format(app_name=app_name.upper()))
        f.write("\n")
        f.write(". /lib/lsb/init-functions\n")
        f.write("\n")
        f.write("case $1 in\n")
        f.write("  start)\n")
        f.write("    log_begin_msg \"Starting $DESC\"\n")
        f.write("    /sbin/start-stop-daemon --background --pidfile $PID --chuid $USER --startas $BIN --start\n")
        f.write("    log_end_msg $?\n")
        f.write("    ;;\n")
        f.write("\n")
        f.write("  stop)\n")
        f.write("    log_begin_msg \"Stopping $DESC\"\n")
        f.write("    /sbin/start-stop-daemon --pidfile $PID --stop\n")
        f.write("    log_end_msg $?\n")
        f.write("    $BIN --stop\n")
        f.write("    ;;\n")
        f.write("\n")
        f.write("  restart)\n")
        f.write("    $0 stop\n")
        f.write("    sleep 1\n")
        f.write("    $0 start\n")
        f.write("    ;;\n")
        f.write("\n")
        f.write("  *) echo \"Usage: $0 {start|stop|restart}\"\n")
        f.write("esac\n")
        f.write("\n")
        f.write("exit 0\n")
        f.close()
    os.chmod(filename, 0755)

  
def create_systemd(user, home, app_name):
    pid_file = "%s/tmp/%s.pid" % (home, app_name)
    log_file = "%s/log/%s" % (home, app_name)
    filename = "/etc/systemd/system/%s.service" % app_name
    with open(filename, 'wb') as f:
        f.write("[Unit]\n")

        f.write("Description=Aplikasi {app_name}\n".format(app_name=app_name))
        f.write("\n")
        f.write("[Service]\n")
        f.write("Type=forking\n")
        f.write("PIDFile={pid_file}\n".format(pid_file=pid_file))
        f.write("ExecStart=/sbin/start-stop-daemon --background \\\n")
        f.write("    --pidfile {pid_file} \\\n".format(pid_file=pid_file))
        f.write("    --exec /usr/local/bin/{app_name} \\\n".format(app_name=app_name))
        f.write("    --start --quiet\n")
        f.write("ExecStop=/usr/local/bin/{app_name} --stop\n".format(app_name=app_name))
        f.write("Restart=on-abort\n")
        f.write("\n")
        f.write("[Install]\n")
        f.write("WantedBy=multi-user.target\n")
        f.close()
    os.chmod(filename, 0755)


def create_bin(user, home, app_name):
    filename = "/usr/local/bin/%s" % app_name
    with open(filename, 'wb') as f:
        f.write('#!/bin/bash\n')
        f.write('su - {user} -c "{home}/bin/start-{app_name}\n"'.format(user=user, home=home, app_name=app_name))
        f.close()
        
    os.chmod(filename, 0755)
    
def create_dir(filename, uid, gid):
    dirname = os.path.dirname(filename)
    if not os.path.exists(dirname):
        os.makedirs(dirname)
        os.chown(dirname, uid, gid)

def create_start(user, app_name, _here, home):
    #create bin buat manual start
    filename = "%s/bin/start-%s" % (home, app_name)
    pid_file = "%s/tmp/%s.pid" % (home, app_name)
    log_file = "%s/log/%s" % (home, app_name)
    print ("Start application:", filename)

    uid = getpwnam(user).pw_uid
    gid = getpwnam(user).pw_gid
    create_dir(filename, uid, gid)
    create_dir(pid_file, uid, gid)
    create_dir(log_file, uid, gid)
    create_dir(log_file+'/log', uid, gid)
        
    with open(filename, 'wb') as f:
        f.write('#!/bin/bash\n')
        f.write("cd {home}/iso8583-forwarder\n".format(home=home))
        f.write("python {home}/iso8583-forwarder/iso8583-forwarder.py \\\n".format(home=home))
        f.write("    --log-dir={log_file} \\\n".format(log_file=log_file))
        f.write("    --pid-file={pid_file} \n".format(pid_file=pid_file))
        f.close()
    os.chmod(filename, 0755)
    
    #create bin buat service
    filename = "%s/bin/%s" % (home, app_name)
    with open(filename, 'wb') as f:
        f.write('#!/bin/python\n')
        f.write("{home}/bin/start-{app_name} \\\n".format(home=home, app_name))
        f.close()
    os.chmod(filename, 0755)


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
    if not (option.user and option.module and option.sub):
        print ("-m module -s sub -u user ")
        return 
        
    _here = '/home/aagusti/apps/h2h/iso8583-forwarder' #os.path.dirname(__file__)
    home = os.path.dirname(_here)
    app_name = "iso8583-forwarder-"+option.module+'-'+option.sub
    print('Starting Installation')
    print ('Current:', _here)
    print ('Home:', home)
    print ('Module:', app_name)
    create_start(option.user, app_name, _here, home)
    
    create_bin(option.user, home, app_name)
    
    if option.service:
        create_service(option.user, home, app_name)
    else:
        crete_systemd(option.user, home, app_name)
        
    create_bat(home, app_name)
    
    print('Berhasil Install.')

argv = sys.argv
main(argv)