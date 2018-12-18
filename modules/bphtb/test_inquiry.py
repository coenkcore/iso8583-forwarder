from datetime import datetime
from pprint import pprint
from time import sleep
from optparse import OptionParser
from common.bphtb.structure import INQUIRY_CODE
from config import module_name


def inquiry_request(iso, invoice_id, bank_id, nop):
    kini = datetime.now()
    iso.setBit(2, kini.strftime('%Y%m%d%H%M%S')) 
    iso.setBit(3, INQUIRY_CODE)
    iso.setBit(7, kini.strftime('%m%d%H%M%S')) 
    iso.setBit(11, kini.strftime('%H%M%S')) 
    iso.setBit(12, kini.strftime('%H%M%S')) 
    iso.setBit(13, kini.strftime('%m%d')) 
    iso.setBit(15, kini.strftime('%m%d')) 
    iso.setBit(18, '6010') 
    iso.setBit(22, '021')
    iso.setBit(32, bank_id)
    iso.setBit(33, '00110')
    iso.setBit(35, '')
    iso.setBit(37, kini.strftime('%H%M%S')) 
    iso.setBit(41, '000')
    iso.setBit(42, '000000000000000')
    iso.setBit(43, 'Nama Bank')
    iso.setBit(49, '390')
    iso.setBit(59, 'PAY')
    iso.setBit(60, '142')
    iso.setBit(61, nop)
    iso.setBit(62, invoice_id)
    iso.setBit(63, '')
    iso.setBit(102, '')
    iso.setBit(107, '')

 
name = '.'.join(['bphtb', module_name])
module = __import__(name)
area_module = getattr(module, module_name)
DbTransaction = area_module.DbTransaction


class TestInquiry:
    def __init__(self, argv):
        self.option = get_option(argv)
        if not self.option:
            return
        self.invoice_id = self.option.invoice_id
        streamer_name, self.bank_id = split_bank(self.option.bank)
        self.conf = dict(name=streamer_name, ip='127.0.0.1')

    def run(self):
        if not self.option:
            return
        print('Bank kirim inquiry request')
        req_iso = DbTransaction()
        req_iso.set_transaction_request()
        nop = self.option.nop or ''
        inquiry_request(req_iso, self.invoice_id, self.bank_id, nop)
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
    bank = 'bjb,110'
    pars = OptionParser()
    help_bank = 'default {b}. Contoh lain: mitracomm,14 dimana 14 adalah BCA'
    help_bank = help_bank.format(b=bank)
    pars.add_option('-i', '--invoice-id')
    pars.add_option('', '--nop')
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
        bank_id = 0 
    return streamer_name, bank_id

def main(argv):
    test = TestInquiry(argv)
    test.run()
