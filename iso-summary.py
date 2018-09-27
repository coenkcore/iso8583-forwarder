# Gunakan Python 3
import sys
import os
from sqlalchemy import create_engine
import pathmagic
from optparse import OptionParser
from demon import make_pid
from tcp import stop_daemon
from base_models import (
    Base,
    DBSession,
    )
from tools import create_now
from log.models import (
    Conf,
    Iso,
    Method,
    Bank,
    Summary,
    )
from log.conf import db_url
from pkb.structure import (
    INQUIRY_CODE as PKB_INQUIRY_CODE,
    PAYMENT_CODE as PKB_PAYMENT_CODE,
    )
from tsamsat.structure import (
    INQUIRY_CODE as TSAMSAT_INQUIRY_CODE,
    PAYMENT_CODE as TSAMSAT_PAYMENT_CODE,
    )


INQUIRY_CODES = (PKB_INQUIRY_CODE, TSAMSAT_INQUIRY_CODE)
PAYMENT_CODES = (PKB_PAYMENT_CODE, TSAMSAT_PAYMENT_CODE)
METHOD_CODES = INQUIRY_CODES + PAYMENT_CODES


def save_conf():
    conf.nilai_int = r_iso.id
    conf.updated = create_now()
    DBSession.add(conf)
    DBSession.flush()
    DBSession.commit()


def save():
    vals = dict()
    data = r_iso.to_dict()
    for key in ('tgl', 'mti', 'bit_003', 'bit_004', 'bit_032'):
        vals[key] = data[key]
    tgl = r_iso.tgl.date()
    amount = float(r_iso.bit_004)
    if r_iso.mti == '0210':
        if r_iso.bit_003 in INQUIRY_CODES:
            method_id = 1
        else:
            method_id = 2
    else:
        method_id = 3
    method_name = methods[method_id]
    bank_id = r_iso.bit_032[-3:]
    bank_id = int(bank_id)
    bank_name = banks[bank_id]
    msg = '{id} {data} -> {tgl} {bank} {method} {amount}'.format(
            id=r_iso.id, tgl=tgl, bank=bank_name, method=method_name,
            amount=amount, data=vals)
    print(msg)
    q = DBSession.query(Summary).filter_by(
            jenis_id=r_iso.jenis_id, tgl=tgl, method_id=method_id,
            bank_id=bank_id)
    r_sum = q.first()
    if r_sum:
        r_sum.trx_count += 1
        r_sum.trx_amount += amount
    else:
        r_sum = Summary()
        r_sum.jenis_id = r_iso.jenis_id
        r_sum.tgl = tgl
        r_sum.method_id = method_id
        r_sum.bank_id = bank_id
        r_sum.trx_count = 1
        r_sum.trx_amount = amount
    DBSession.add(r_sum)
    save_conf()


def get_forwarder_name():
    t = forwarder.split()
    return t[0]


default_limit = 10000
default_pid = 'iso-summary.pid'
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

engine = create_engine(db_url)
Base.metadata.bind = engine
DBSession.configure(bind=engine)

methods = dict()
q = DBSession.query(Method)
for row in q:
    methods[row.id] = row.nama

banks = dict()
q = DBSession.query(Bank)
for row in q:
    banks[row.id] = row.nama

q_conf = DBSession.query(Conf).filter_by(nama='last id iso summary')
conf = q_conf.first()
offset = 0
while True:
    q_iso = DBSession.query(Iso).filter(Iso.id > conf.nilai_int)
    q_iso = q_iso.filter_by(bit_039='00')
    q_iso = q_iso.order_by(Iso.id).offset(offset).limit(limit)
    found = False
    for r_iso in q_iso:
        found = True
        if r_iso.mti not in ('0210', '0410') or \
                r_iso.bit_003 not in METHOD_CODES: 
            save_conf()
            continue
        save()
    if not found:
        break
    offset += limit
