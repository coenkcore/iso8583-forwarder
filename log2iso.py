# Gunakan Python 3
import sys
import re
from hashlib import md5
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
import pathmagic
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
    print('{line} -> {ip} {forwarder} {arus} {mti} {bits}'.format(
        line=r_log.line, ip=ip, forwarder=forwarder, arus=is_send, mti=mti,
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

thread_ids = dict()

q_log = DBSession.query(Log).filter(Log.id > conf.nilai_int).order_by(Log.id)
for r_log in q_log:
    match = REGEX_ISO.search(r_log.line)
    if not match:
        continue
    ip1, ip2, ip3, ip4, forwarder, arus, mti, bits = match.groups()
    ip = '.'.join([ip1, ip2, ip3, ip4])
    forwarder = get_forwarder_name()
    is_send = arus == 'Encode' 
    bits = eval(bits)
    save()
