# Gunakan Python 3
import sys
import re
from hashlib import md5
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
import pathmagic
from tools import create_datetime
from base_models import (
    Base,
    DBSession,
    )
from log.models import Log
from log.conf import db_url


def save():
    print(lines)
    row = Log()
    row.jenis_id = jenis_id
    row.line = '\n'.join(lines)
    row.line_id = line_id
    row.tgl = waktu
    row.kategori_id = KATEGORI.index(kategori)
    DBSession.add(row)
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


KATEGORI = (None, 'INFO', 'ERROR', 'WARNING')
REGEX_FIRST_LINE = '^([\d]*)-([\d]*)-([\d]*) ([\d]*):([\d]*):([\d]*),([\d]*) '\
        '(INFO|ERROR|WARNING)'
REGEX_FIRST_LINE = re.compile(REGEX_FIRST_LINE)

jenis_id = int(sys.argv[1])
log_file = sys.argv[2]

engine = create_engine(db_url)
Base.metadata.bind = engine
DBSession.configure(bind=engine)

lines = []
line_id = None
f = open(log_file)
for line in f.readlines():
    s = line.rstrip()
    match = REGEX_FIRST_LINE.search(s)
    if match:
        if line_id:
            save()
        line_id = md5(s.encode('utf-8')).hexdigest()
        lines = [s]
        year, month, day, hour, minute, sec, msec, kategori = match.groups()
        waktu = create_datetime(
                    int(year), int(month), int(day), int(hour),
                    int(minute), int(sec), int(msec)*1000)
    else:
        lines.append(s)
f.close()
if line_id:
    save()
