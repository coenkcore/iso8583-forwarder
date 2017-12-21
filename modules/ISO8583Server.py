from tcp import print_log
from datetime import (
    datetime,
    date,
    time,
    )
from ISO8583.ISO8583 import ISO8583


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
        for s in struct:
            name = s[0]
            size = s[1:] and s[1] or 1
            typ = s[2:] and s[2] or 'A' # N: numeric, A: alphanumeric
            self.fields[name] = {'value': None, 'type': typ, 'size': size} 

    def set(self, name, value):
        self.fields[name]['value'] = value

    def get(self, name):
        v = self.fields[name]['value']
        if self.fields[name]['type'] != 'N':
            return v
        if v:
            return int(v)
 
    def __setitem__(self, name, value):
        self.set(name, value)        

    def __getitem__(self, name):
        return self.get(name)
 
    def get_raw(self):
        s = ''
        for name, size, typ in self.struct:
            v = self.fields[name]['value']
            pad_func = typ == 'N' and right or left
            if v and typ == 'N':
                i = int(v)
                if v == i:
                    v = i
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
 

class DateVar(FixLength):
    def __init__(self):
        super(DateVar, self).__init__([
            ['month', 2, 'N'],
            ['day', 2, 'N'],
            ])

    def get_value(self, year=None):
        year = year or date.today().year
        return date(year, self.get('month'), self.get('day'))


class DateTimeVar(FixLength):
    def __init__(self):
        super(DateTimeVar, self).__init__([
            ['month', 2, 'N'],
            ['day', 2, 'N'],
            ['hour', 2, 'N'],
            ['minute', 2, 'N'],
            ['second', 2, 'N'],
            ])

    def get_value(self, year=None):
        year = year or date.today().year
        return datetime(year, self.get('month'), self.get('day'),
                        self.get('hour'), self.get('minute'),
                        self.get('second'))


class TimeVar(FixLength):
    def __init__(self):
        super(TimeVar, self).__init__([
            ['hour', 2, 'N'],
            ['minute', 2, 'N'],
            ['second', 2, 'N'],
            ])

    def get_value(self):
        return time(self.get('hour'), self.get('minute'), self.get('second'))


#########################
# Inherit ISO8583 class #
#########################
class Data(ISO8583):
    def __init__(self, from_iso=None, debug=False):
        ISO8583.__init__(self, debug=debug)
        self.from_iso = from_iso
        if from_iso:
            self.from_data = self.get_values()

    def get_value(self, bit):
        v = self.getBit(bit)
        type_ = self.getBitType(bit)
        if type_.find('LL') < 0:
            return v
        size_length = len(type_)
        return v[size_length:]

    def get_values(self):
        r = {}
        for item in self.getBitsAndValues():
            bit = int(item['bit'])
            r[bit] = self.get_value(bit)
        return r

    def copy(self, bits=[], from_iso=None):
        if not from_iso:
            from_iso = self.from_iso
        values = from_iso.get_values()
        for bit in values:
            if bits and bit not in bits: # Hanya bit tertentu ?
                continue
            value = values[bit]
            self.setBit(bit, value)

    # Override
    def setIsoContent(self, raw):
        self.log_info('Raw to ISO8583 %s' % [raw])
        ISO8583.setIsoContent(self, raw)
        data = self.get_values()
        self.log_info('Decode MTI %s Data %s' % (self.getMTI(), data))

    # Override
    def getRawIso(self):
        data = self.get_values()
        self.log_info('Encode MTI %s Data %s' % (self.getMTI(), data))
        raw = ISO8583.getRawIso(self)
        self.log_info('ISO8583 to raw %s' % [raw])
        return raw

    def log_info(self, s):
        print_log(s)

    def log_error(self, s):
        print_log(s, 'ERROR')
