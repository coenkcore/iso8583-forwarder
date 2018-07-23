# Gunakan Python 3
import os
import sys
import re
import pathmagic
import select
from hashlib import md5
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from optparse import OptionParser
from time import sleep
from subprocess import (
    Popen,
    PIPE,
    )
from mmap import (
    mmap,
    ACCESS_READ,
    )
from tools import create_datetime
from base_models import (
    Base,
    DBSession,
    )
from demon import make_pid
from log.models import (
    Log,
    Jenis,
    )
from log.conf import (
    db_url,
    duplicate_key_message,
    )


class BacaFile(object):
    def __init__(self, filename, cari=''):
        if cari:
            self.is_found = False
        else:
            self.is_found = True
        is_first = True
        self.file = open(filename, 'rb')
        s = mmap(self.file.fileno(), 0, access=ACCESS_READ)
        while cari:
            pos = s.find(cari.encode('utf-8'))
            if pos == -1:  # Tidak ketemu
                return
            if pos == 0:  # Ketemu di baris ke-1
                self.is_found = True
                break
            if not is_first:
                self.file.seek(pos)
                self.file.readline()
                self.is_found = True
                break
            cari = '\n' + cari  # Cari di baris berikutnya
            self.file.seek(0)
            is_first = False

    def close(self):
        self.file.close()

    def readline(self):
        if self.is_found:
            return self.file.readline()


def save():
    if not line_id:
        return
    s = '\n'.join(lines)
    print([s])
    row = Log()
    row.jenis_id = jenis_id
    row.line = s 
    row.line_id = line_id
    row.tgl = waktu
    row.kategori_id = KATEGORI.index(kategori)
    DBSession.add(row)
    try:
        DBSession.flush()
    except IntegrityError as err:
        s_err = str(err)
        if s_err.find(duplicate_key_message) > -1:
            print('  sudah ada')
            DBSession.rollback()
        else:
            raise(err)
    DBSession.commit()


engine = create_engine(db_url)
Base.metadata.bind = engine
DBSession.configure(bind=engine)

lines = []
q = DBSession.query(Jenis).order_by(Jenis.id)
for row in q:
    line = '{}: {}'.format(row.id, row.nama)
    lines.append(line)
help_jenis = ', '.join(lines)

default_pid_file = 'log2db.pid'

pars = OptionParser()
pars.add_option('-j', '--jenis', help=help_jenis)
pars.add_option('-f', '--file', help='log file')
pars.add_option('-t', '--tail-mode-only', action='store_true')
pars.add_option('', '--start-from')
pars.add_option(
    '', '--pid-file', default=default_pid_file,
    help='default '+default_pid_file)
option, remain = pars.parse_args(sys.argv[1:])

pid_file = os.path.realpath(option.pid_file)
make_pid(pid_file)

KATEGORI = (None, 'INFO', 'ERROR', 'WARNING')
REGEX_FIRST_LINE = '^([\d]*)-([\d]*)-([\d]*) '\
        '([\d]*):([\d]*):([\d]*),([\d]*) '\
        '(INFO|ERROR|WARNING)'
REGEX_FIRST_LINE = re.compile(REGEX_FIRST_LINE)

jenis_id = int(option.jenis)
log_file = option.file
start_from = option.start_from

if not option.tail_mode_only:
    lines = []
    line_id = None
    f = BacaFile(log_file, start_from)
    while True:
        line = f.readline()
        if not line:
            save()
            break
        s = line.rstrip().decode('utf-8')
        match = REGEX_FIRST_LINE.search(s)
        if match:
            save()
            del lines[:]
            line_id = md5(line).hexdigest()
            year, month, day, hour, minute, sec, msec, kategori = \
                match.groups()
            waktu = create_datetime(
                    int(year), int(month), int(day), int(hour),
                    int(minute), int(sec), int(msec)*1000)
        lines.append(s)
    f.close()

if log_file[-3:] != 'log':
    print('Selesai.')
    sys.exit()

lines = []
line_id = None
f = Popen(['tail', '-f', log_file], stdout=PIPE, stderr=PIPE)
p = select.poll()
p.register(f.stdout)
while True:
    if p.poll(1):
        line = f.stdout.readline()
        line = line.rstrip()
        line = line.decode('utf-8')
        match = REGEX_FIRST_LINE.search(line)
        if match:
            if line_id:
                save()
            line_id = md5(line.encode('utf-8')).hexdigest()
            lines = [line]
            year, month, day, hour, minute, sec, msec, kategori = \
                match.groups()
            waktu = create_datetime(
                    int(year), int(month), int(day), int(hour),
                    int(minute), int(sec), int(msec)*1000)
        else:
            lines.append(line)
    sleep(0.1)
