import os
import sys
import logging
import random
from subprocess import (
    Popen,
    PIPE,
    )


logformatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')

def Log(name, file=None):
    if not file:
        file = name
        name = str(random.randrange(1,99999))
    log = logging.getLogger(name)
    handler = logging.FileHandler( file )
    handler.setFormatter( logformatter )
    log.addHandler( handler )
    log.setLevel( logging.INFO )
    return log
    
    
def get_pid(pid):
    if isinstance(pid, int):
        return pid
    try:
        f = open(pid,'r')
        pid_int = int(f.read().split()[0])
        f.close()
        return pid_int
    except IOError:
        return
    except ValueError:
        return
    except IndexError:
        return
 
def isLive(pid):
    pid = get_pid(pid)
    if not pid:
        return
    try:
        os.kill(pid, 0)
    except OSError:
        return
    for i in range(3):
        p1 = Popen(['ps', 'ax'], stdout=PIPE)
        p2 = Popen(['grep', '^%s%d' % (' ' * i, pid)], stdin=p1.stdout,
                stdout=PIPE)
        p3 = Popen(['grep', '-v', 'grep'], stdin=p2.stdout, stdout=PIPE)
        s = p3.communicate()
        s = s[0]
        if s:
            return pid

def make_pid(filename):
    pid = isLive(filename)
    if pid:
        sys.exit('PID saya %d masih ada' % pid)
    pid = os.getpid()
    f = open(filename,'w')
    f.write(str(pid))
    f.close()
    return pid

def my_ip():
    r = []
    for t in commands.getoutput('/sbin/ifconfig |grep "inet "').splitlines():
        # inet addr:192.168.0.254  Bcast:192.168.0.255  Mask:255.255.255.0
        if t.find(':') > -1:
            ip = t.split()[1].split(':')[1]
        else:
            # inet 192.168.1.7  netmask 255.255.255.0  broadcast 192.168.1.255
            ip = t.split()[1]
        r.append(ip)
    return r
