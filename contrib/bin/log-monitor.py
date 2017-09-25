# Kegunaan: pemantau jam log file di baris terakhir. Jika terlalu lama lakukan
#           sesuatu.
# Oleh: Owo Sugiana
# Tanggal: 3 Mei 2017
# Versi Python: 2 & 3

import os
import sys
import re
from datetime import (
    datetime,
    timedelta,
    )
from optparse import OptionParser
from subprocess import call


REGEX_TIME = re.compile(r'^(\d*)\-(\d*)-(\d*) (\d*):(\d*):(\d*)')
DEFAULT_MAX_AGE = 180 # detik

HELP_AGE = 'default {n} detik'.format(n=DEFAULT_MAX_AGE)
HELP_EXECUTE = 'File yang dijalankan saat timeout terjadi.'

pars = OptionParser()
pars.add_option('-l', '--log-file')
pars.add_option('-x', '--execute', help=HELP_EXECUTE)
pars.add_option('-a', '--age', default=DEFAULT_MAX_AGE, help=HELP_AGE)

option, remain = pars.parse_args(sys.argv[1:])

log_file = option.log_file
exe = os.path.realpath(option.execute)
max_age = int(option.age)

if not os.path.exists(exe):
    print('File {s} tidak ada.'.format(s=exe))
    sys.exit()

f = open(log_file)
for line in f.readlines():
    s = line.strip()
    match = REGEX_TIME.search(s)
    if match:
        last_match = match
f.close()
y, m, d, hh, mm, ss = last_match.groups()
y, m, d, hh, mm, ss = int(y), int(m), int(d), int(hh), int(mm), int(ss)
log_time = datetime(y, m, d, hh, mm, ss)
kini = datetime.now()
usia_log = kini - log_time
print('Log : {t}'.format(t=log_time))
print('Kini: {t}'.format(t=kini))
print('Usia: {s} detik'.format(s=usia_log))
if usia_log < timedelta(max_age/24/60/60):
    print('Usia log masih di bawah {n} detik, {e} tidak perlu dijalankan.'.\
            format(n=max_age, e=exe))
    sys.exit()
print('Usia log di atas {d} detik, {e} dijalankan.'.format(d=max_age, e=exe))
call([exe])