from datetime import datetime
from pprint import pprint
from time import sleep
from optparse import OptionParser
from structure import PBB_INQUIRY_CODE
import conf


INQUIRY_CODES = dict(pbb=PBB_INQUIRY_CODE)


def default_inquiry_request(iso, module_name, invoice_id, bank_id):
    inquiry_code = INQUIRY_CODES[module_name]
    kini = datetime.now()
    iso.set_transaction_code(inquiry_code) 
    iso.setBit(32, bank_id)
    iso.setBit(48, invoice_id)
 
test_not_found = False
name = '.'.join(['bni', conf.module_name, 'test'])
try:
    module = __import__(name)
except ImportError, test_not_found:
    name = '.'.join(['bni', conf.module_name])
    module = __import__(name)
area_module = getattr(module, conf.module_name)
DbTransaction = area_module.DbTransaction

if test_not_found:
    inquiry_request = default_inquiry_request
else:
    inquiry_request = area_module.test.inquiry_request


class TestInquiry(object):
    def __init__(self, argv):
        self.option = get_option(argv)
        if not self.option:
            return
        self.module_name = self.option.module
        self.invoice_id = self.option.invoice_id
        streamer_name, bank_id = split_bank(self.option.bank)
        self.conf = dict(name=streamer_name, ip='127.0.0.1', bank_id=bank_id)

    def run(self):
        if not self.option:
            return
        print('Bank kirim inquiry request')
        req_iso = DbTransaction()
        req_iso.set_transaction_request()
        inquiry_request(req_iso, self.module_name, self.invoice_id,
            self.conf['bank_id'])
        raw = self.get_raw(req_iso)
        print('Pemda terima inquiry request')
        from_iso = DbTransaction()
        from_iso.setIsoContent(raw)
        print('Pemda kirim inquiry response')
        resp_iso = DbTransaction(from_iso=from_iso, conf=self.conf)
        func = getattr(resp_iso, from_iso.get_func_name())
        func()
        self.get_raw(resp_iso)
        return resp_iso # Untuk test_payment.py

    def get_raw(self, iso):
        msg = 'MTI {mti}'.format(mti=iso.getMTI())
        print(msg)
        pprint(iso.getBitsAndValues())
        raw = iso.getRawIso()
        sleep(1)
        print([raw])
        return raw


def get_option(argv):
    module_name = 'pbb'
    bank = 'bni'
    pars = OptionParser()
    help_module = 'default {m}'.format(m=module_name)
    help_bank = 'default {b}. Contoh lain: mitracomm,14 dimana 14 adalah BCA'.\
            format(b=bank)
    pars.add_option('-m', '--module', default=module_name, help=help_module)
    pars.add_option('-i', '--invoice-id')
    pars.add_option('-b', '--bank', default=bank, help=help_bank)
    option, remain = pars.parse_args(argv)
    if not option.invoice_id:
        print('--invoice-id harus diisi.')
        return
    return option

def split_bank(s):
    t = s.split(',')
    if t[1:]:
        streamer_name = t[0]
        bank_id = int(t[1])
    else:
        streamer_name = s 
        bank_id = 9  
    return streamer_name, bank_id

def main(argv):
    test = TestInquiry(argv)
    test.run()
