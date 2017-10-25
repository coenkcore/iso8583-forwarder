from pprint import pprint
from time import sleep
from optparse import OptionParser
from streamer_loader import get_streamer_module
import conf


name = '.'.join(['bni', conf.module_name])
module = __import__(name)
area_module = getattr(module, conf.module_name)
DbTransaction = area_module.DbTransaction


class TestRaw(object):
    def __init__(self, argv):
        self.option = get_option(argv)
        if not self.option:
            return
        self.streamer_module = get_streamer_module(self.option.streamer)
        self.filename = self.option.file
        self.conf = dict(ip='127.0.0.1', bank_id=self.option.bank_id)

    def run(self):
        if not self.option:
            return
        streamer = self.streamer_module.Streamer()
        print('Pemda terima raw')
        f = open(self.filename)
        raw = f.read()
        f.close()
        iso_raw = streamer.get(raw)
        from_iso = DbTransaction()
        from_iso.setIsoContent(iso_raw)
        self.get_raw(from_iso)
        if from_iso.is_response():
            return
        print('Pemda kirim raw')
        resp_iso = DbTransaction(from_iso=from_iso, conf=self.conf)
        func = getattr(resp_iso, from_iso.get_func_name())
        func()
        self.get_raw(resp_iso)

    def get_raw(self, iso):
        msg = 'MTI {mti}'.format(mti=iso.getMTI())
        print(msg)
        pprint(iso.getBitsAndValues())
        raw = iso.getRawIso()
        sleep(1)
        print([raw])
        return raw


def get_option(argv):
    streamer_name = 'none'
    bank_id = 9
    pars = OptionParser()
    help_streamer = 'default {m}'.format(m=streamer_name)
    help_bank = 'default {b}'.format(b=bank_id)
    pars.add_option('-f', '--file')
    pars.add_option('-s', '--streamer', default=streamer_name, help=help_streamer)
    pars.add_option('-b', '--bank-id', default=bank_id, help=help_bank)
    option, remain = pars.parse_args(argv)
    if not option.file:
        print('--file harus diisi.')
        return
    return option

def main(argv):
    test = TestRaw(argv)
    test.run()
