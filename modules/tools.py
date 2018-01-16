from datetime import datetime
from datetime import timedelta
try:
    from urllib import unquote_plus
except ImportError:
    from urllib.parse import unquote_plus
try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse
from time import sleep
from random import randrange
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
from sqlalchemy import PrimaryKeyConstraint
import traceback
import re
import demon
import sys
import os
import signal
import pytz
import locale
import csv


locale.setlocale(locale.LC_ALL, 'id_ID.UTF-8') 


#######
# Log #
#######
def humanize_time(secs):
    mins, secs = divmod(secs, 60)
    hours, mins = divmod(mins, 60)
    return '%02d:%02d:%02d' % (hours, mins, secs)

def print_log(s, category='INFO'):
    print('%s %s %s' % (datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
          category, s))

def exception_message():
    f = StringIO()
    traceback.print_exc(file=f)
    s = f.getvalue()
    f.close()
    return s 

############
# Database #
############
# Dibutuhkan MS SQL Server
def vs(s):
    return s and unicode(s).encode('utf-8') or None
        
def is_odbc(driver):
    return driver.split('+')[-1] == 'pyodbc'

def extract_netloc(s): # sugiana:a@localhost:5432
    r = {}
    t = s.split('@')
    if t[1:]: # localhost:5432
        h = t[1].split(':')
        if h[1:]:
            r['port'] = int(h[1])
        r['host'] = h[0]
    auth = t[0].split(':')
    if auth[1:]:
        r['pass'] = auth[1]
    r['user'] = auth[0]
    return r

def extract_tds(s):
    items = s.split(';')
    r = {}
    for item in items:
        key, value = item.split('=')
        if key == 'UID':
            r['user'] = value
        elif key == 'PWD':
            r['pass'] = value
        elif key == 'Server':
            r['host'] = value
        elif key == 'Database':
            r['name'] = value
        elif key == 'Port':
            r['port'] = int(value)
    return r

def extract_db_url(db_url):
    p = urlparse(db_url)
    r = {'driver': p.scheme}
    if is_odbc(p.scheme):
        if p.query:
            s = p.query
        else:
            s = p.path.split('?')[-1]
        t = s.split('=')
        s = unquote_plus(t[1])    
        r.update(extract_tds(s))
        return r
    if p.netloc:
        r.update(extract_netloc(p.netloc))
    if p.path[1:]:
        r['name'] = p.path.lstrip('/')
    return r

def eng_profile(db_url):
    url = extract_db_url(db_url)
    return 'driver:%s user:%s host:%s port:%s database:%s' % (
        url['driver'], url['user'], url['host'], url['port'], url['name'])

def trigger_name(sql):
    sql = sql.lower().replace('\n', ' ')
    match = re.compile('trigger (.*) (after|before)').search(sql)
    return match and match.group(1)

def get_pkeys(table):
    r = []
    for c in table.constraints:
        if c.__class__ is PrimaryKeyConstraint:
            for col in c:
                r.append(col.name)
            return r
    return r


class FromCSV(object):
    def __init__(self, Base, DBSession):
        self.Base = Base
        self.DBSession = DBSession

    def restore(self, filename, table):
        keys = get_pkeys(table.__table__)
        f = open(filename)
        reader = csv.DictReader(f)
        for source in reader:
            filter_ = {}
            for key in keys:
                if key in source:
                    filter_[key] = source[key]
                else:
                    uniq = reader.fieldnames[0]
                    filter_[uniq] = source[uniq]
            q = self.DBSession.query(table).filter_by(**filter_)
            if q.first():
                continue
            row = table()
            row.from_dict(source)
            self.DBSession.add(row)
            self.DBSession.flush()
        f.close()
        self.DBSession.commit()


#########################
# Nomor Transaksi Pemda #
#########################
ERR_MAX_LOOP = '*** Max loop for create payment ID. Call your programmer '\
               'please.'

class TransactionID(object):
    def create(self, prefix=''):
        max_loop = 10
        loop = 0
        while True:
            acak = randrange(11111111, 99999999)
            acak = str(acak)
            trx_id = ''.join([prefix, acak])
            if not self.is_found(trx_id):
                return trx_id
            loop += 1
            if loop == max_loop:
                raise Exception(ERR_MAX_LOOP)

    # Override dengan cek NTP di tabel pembayaran
    def is_found(self, trx_id):
        return False


class DbTransactionID(TransactionID):
    def __init__(self, models, DBSession):
        self.models = models
        self.DBSession = DBSession


##########
# Daemon #
##########
def stop_daemon(pid_file):
    pid = demon.isLive(pid_file)
    if not pid:
        sys.exit()
    print('kill %d by signal' % pid)
    os.kill(pid, signal.SIGTERM)
    i = 0
    while i < 5:
        sleep(1)
        i += 1
        if not demon.isLive(pid_file):
            sys.exit()
    print('kill %d by force' % pid)
    os.kill(pid, signal.SIGKILL)
    sys.exit()
    
##########
# String #
##########
def clean(s):
    r = ''
    for ch in s:
        ascii = ord(ch)
        if ascii > 126 or ascii < 32:
            ch = ' '
        r += ch
    return r

def to_str(s):
    s = s or ''
    if not (isinstance(s, str) or isinstance(s, unicode)):
        s = str(s)
    return clean(s)

def left(s, width):
    s = to_str(s)
    return s.ljust(width)[:width]

def right(s, width):
    s = to_str(s)
    return s.zfill(width)[:width]


##################
# Data Structure #
##################
class FixLength(object):
    def __init__(self, struct):
        self.set_struct(struct)

    def set_struct(self, struct):
        self.struct = struct
        self.fields = {}
        new_struct = []
        for s in struct:
            name = s[0]
            size = s[1:] and s[1] or 1
            typ = s[2:] and s[2] or 'A' # N: numeric, A: alphanumeric
            self.fields[name] = {'value': None, 'type': typ, 'size': size}
            new_struct.append((name, size, typ))
        self.struct = new_struct

    def set(self, name, value):
        self.fields[name]['value'] = value

    def get(self, name):
        return self.fields[name]['value']
 
    def __setitem__(self, name, value):
        self.set(name, value)        

    def __getitem__(self, name):
        return self.get(name)
 
    def get_raw(self):
        s = ''
        for name, size, typ in self.struct:
            v = self.fields[name]['value']
            pad_func = typ == 'N' and right or left
            if typ == 'N':
                v = v or 0
                try:
                    i = int(v)
                except ValueError as e:
                    raise Exception('Invalid {k} value: {v}. {e}'.format(
                        k=name, v=v, e=e.message))
                if v == i:
                    v = i
            else:
                v = v or ''
            s += pad_func(v, size)
        return s

    def set_raw(self, raw):
        awal = 0
        for t in self.struct:
            name = t[0]
            size = t[1:] and t[1] or 1
            akhir = awal + size
            value = raw[awal:akhir]
            if not value:
                return
            self.set(name, value)
            awal += size
        return True

    def from_dict(self, d):
        for name in d:
            value = d[name]
            self.set(name, value)

    def to_dict(self):
        d = dict()
        for name in self.fields:
            value = self.fields[name]['value']
            d[name] = value
        return d

    def __repr__(self):
        lines = []
        for name, size, typ in self.struct:
            value = str(self.fields[name]['value'])
            s = '{} ({:d}): {} ({:d})'.format(name, size, value, len(value))
            lines.append(s)
        return '\n'.join(lines)
            

###########
# Numeric #
###########
def should_int(value):
    int_ = int(value)
    return int_ == value and int_ or value

def thousand(value, float_count=None):
    if float_count is None: # autodetection
        if isinstance(value, int) or isinstance(value, long):
            float_count = 0
        else:
            float_count = 2
    return locale.format('%%.%df' % float_count, value, True)

def money(value, float_count=None, currency=None):
    if value < 0:
        v = abs(value)
        format_ = '(%s)'
    else:
        v = value
        format_ = '%s'
    if currency is None:
        currency = locale.localeconv()['currency_symbol']
    s = ' '.join([currency, thousand(v, float_count)])
    return format_ % s

def round_up(n):
    i = int(n)
    if n == i:
        return i 
    if n > 0:
        return i + 1
    return i - 1

############
# Datetime #
############
timezone_file = '/etc/timezone'
if os.path.exists(timezone_file):
    timezone_name = open(timezone_file).read().strip() # Asia/Jakarta
else:
    timezone_name = 'Asia/Jakarta'

# Beberapa zona ada yang kurang pas. Misalnya Jakarta menjadi +07:07, kelebihan
# 7 menit.
# https://stackoverflow.com/questions/24856643/unexpected-results-converting-timezones-in-python
NORMALIZE_ZONES = {
    'Asia/Jakarta': 7,
    }

def get_timezone():
    return pytz.timezone(timezone_name) 

# As local timezone
def as_timezone(tz_date):
    localtz = get_timezone()
    return tz_date.astimezone(localtz)

def create_datetime(year, month, day,
                    hour=0, minute=7, second=0,
                    microsecond=0):
    tz = get_timezone()        
    t = datetime(
            year, month, day, hour, minute, second, microsecond, tzinfo=tz)
    if tz.zone in NORMALIZE_ZONES:
        minutes = NORMALIZE_ZONES[tz.zone]
        t = t + timedelta(minutes=minutes)
        return tz.normalize(t)
    return t

def create_date(year, month, day):    
    return create_datetime(year, month, day)
    
def create_now():
    tz = get_timezone()
    return datetime.now(tz)

##############
# Dictionary #
##############
def dict_copy(d, keys):
    r = dict()
    for key in keys:
        r[key] = d[key]
    return r
