from datetime import datetime
from pprint import pprint
from time import sleep
from optparse import OptionParser
from structure import INQUIRY_CODE
from transaction import Transaction
import conf


name = '.'.join(['pbb', conf.module_name])
module = __import__(name)
area_module = getattr(module, conf.module_name)
InquiryResponse = area_module.InquiryResponse


class Inquiry(Transaction):
    def inquiry_request(self, module_name, invoice_id):
        self.set_transaction_request()
        kini = datetime.now()
        self.setBit(2, kini.strftime('%Y%m%d%H%M%S')) 
        self.set_transaction_code(INQUIRY_CODE) 
        self.setBit(12, kini.strftime('%H%M%S')) 
        self.setBit(13, kini.strftime('%m%d')) 
        self.setBit(15, kini.strftime('%m%d')) 
        self.setBit(18, '6010') 
        self.setBit(22, '021')
        self.setBit(32, '110')
        self.setBit(33, '00110')
        self.setBit(35, '')
        self.setBit(37, kini.strftime('%H%M%S')) 
        self.setBit(41, '000')
        self.setBit(42, '000000000000000')
        self.setBit(43, 'Nama Bank')
        self.setBit(49, '390')
        self.setBit(59, 'PAY')
        self.setBit(60, '142')
        self.setBit(61, invoice_id)
        self.setBit(63, '')
        self.setBit(102, '')
        self.setBit(107, '')


class Test(object):
    def get_raw(self, iso):
        msg = 'MTI {mti}'.format(mti=iso.getMTI())
        print(msg)
        pprint(iso.getBitsAndValues())
        raw = iso.getRawIso()
        sleep(1)
        print([raw])
        return raw


class TestInquiry(Test):
    def __init__(self, module_name, invoice_id, conf={}):
        self.module_name = module_name
        self.invoice_id = invoice_id
        self.conf = conf

    def run(self):
        print('Bank kirim inquiry request')
        req_iso = Inquiry()
        req_iso.inquiry_request(self.module_name, self.invoice_id)
        raw = self.get_raw(req_iso)
        print('Pemda terima inquiry request')
        from_iso = Transaction()
        from_iso.setIsoContent(raw)
        print('Pemda kirim inquiry response')
        resp_iso = InquiryResponse(from_iso=from_iso, conf=self.conf)
        func = getattr(resp_iso, from_iso.get_func_name())
        func()
        self.get_raw(resp_iso)
        return resp_iso # Untuk test_payment.py


def get_option(argv):
    module_name = 'pbb'
    bank = 'btn'
    pars = OptionParser()
    help_module = 'default {m}'.format(m=module_name)
    help_bank = 'default {b}'.format(b=bank)
    pars.add_option('-m', '--module', default=module_name, help=help_module)
    pars.add_option('-i', '--invoice-id')
    pars.add_option('-b', '--bank', default=bank, help=help_bank)
    option, remain = pars.parse_args(argv)
    if not option.invoice_id:
        print('--invoice-id harus diisi.')
        return
    return option

def main(argv):
    option = get_option(argv)
    if not option:
        return
    module_name = option.module
    invoice_id = option.invoice_id
    conf = dict(name=option.bank, ip='127.0.0.1')
    test = TestInquiry(module_name, invoice_id, conf)
    test.run()
