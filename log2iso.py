# Gunakan Python 3
import sys
import os
import re
from hashlib import md5
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
import pathmagic
from optparse import OptionParser
from demon import make_pid
from tcp import stop_daemon
from base_models import (
    Base,
    DBSession,
    )
from log.models import (
    Conf,
    Log,
    Iso,
    )
from log.conf import db_url


def save():
    print('{line} -> {ip} {forwarder} {is_send} {mti} {bits}'.format(
        line=r_log.line, ip=ip, forwarder=forwarder, is_send=is_send, mti=mti,
        bits=bits))
    r_iso = Iso()
    r_iso.id = conf.nilai_int = r_log.id
    r_iso.ip = ip
    r_iso.forwarder = forwarder
    r_iso.is_send = is_send
    r_iso.mti = mti
    for key in bits:
        value = bits[key]
        n = str(key).zfill(3)
        fieldname = 'bit_{n}'.format(n=n)
        setattr(r_iso, fieldname, value)
    DBSession.add(r_iso)
    DBSession.add(conf)
    try:
        DBSession.flush()
    except IntegrityError as err:
        s_err = str(err)
        if s_err.find('duplicate key') > -1:
            print('  sudah ada')
            DBSession.rollback()
        else:
            raise(err)
    DBSession.commit()


def get_forwarder_name():
    t = forwarder.split()
    return t[0]


default_limit = 10000
default_pid = 'log2iso.pid'
help_limit = 'Jumlah record yang diproses di setiap loop, default {}'.\
        format(default_limit)
help_pid = 'default ' + default_pid
pars = OptionParser()
pars.add_option('', '--limit', help=help_limit, default=default_limit)
pars.add_option('', '--pid-file', default=default_pid, help=help_pid)
pars.add_option('', '--stop', action='store_true')
option, remain = pars.parse_args(sys.argv[1:])

pid_file = os.path.realpath(option.pid_file)

if option.stop:
    print('Stop Daemon')
    stop_daemon(pid_file)
    sys.exit()

make_pid(pid_file)

limit = int(option.limit)

REGEX_ISO = 'INFO ([\d]*)\.([\d]*)\.([\d]*)\.([\d]*) (.*) (Encode|Decode) MTI'\
        ' ([\d]*) Data (.*)'
REGEX_ISO = re.compile(REGEX_ISO)

REGEX_FORWARDER = '^([a-b]*)'
REGEX_FORWARDER = re.compile(REGEX_FORWARDER)

engine = create_engine(db_url)
Base.metadata.bind = engine
DBSession.configure(bind=engine)

q_conf = DBSession.query(Conf).filter_by(nama='last id log to iso')
conf = q_conf.first()
offset = 0
while True:
    q_log = DBSession.query(Log).filter(Log.id > conf.nilai_int).\
            order_by(Log.id).offset(offset).limit(limit)
    found = False
    for r_log in q_log:
        found = True
        match = REGEX_ISO.search(r_log.line)
        if not match:
            continue
        ip1, ip2, ip3, ip4, forwarder, arus, mti, bits = match.groups()
        ip = '.'.join([ip1, ip2, ip3, ip4])
        forwarder = get_forwarder_name()
        is_send = arus == 'Encode'
        bits = eval(bits)
        save()
    if not found:
        break
    offset += limit
