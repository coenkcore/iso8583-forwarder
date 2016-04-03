import sys
from sqlalchemy import create_engine
from datetime import datetime
from time import sleep
from common import Test
sys.path[0:0] = ['/usr/share/opensipkd-forwarder/modules/multi']
from multi_structure import INQUIRY_CODE
sys.path[0:0] = ['/etc/opensipkd']
from multi_conf import (
    #module_name,
    db_url,
    )
sys.path[0:0] = ['/usr/share/opensipkd/modules']
from base_models import Base
engine = create_engine(db_url)
Base.metadata.bind = engine
sys.path[0:0] = ['/usr/share/opensipkd-forwarder/modules/multi/']
from multi_db_transaction import MultiDbTransaction


class Inquiry(MultiDbTransaction):
    def is_response(self):
        return BaseDbTransaction.is_response(self) or self.getMTI() == '0210'

    def inquiry_request(self, invoice_id):
        self.setMTI('0200')
        kini = datetime.now()
        self.setBit(2, kini.strftime('%Y%m%d%H%M%S')) 
        self.setBit(3, '300020')
        self.setBit(7, kini.strftime('%m%d%H%M%S')) 
        self.setBit(11, kini.strftime('%H%M%S')) 
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


class InquiryTest(Test):
    def __init__(self, invoice_id, conf={}):
        self.invoice_id = invoice_id
        self.conf = conf

    def request(self):
        print('Bank kirim inquiry request')
        req_iso = Inquiry()
        req_iso.inquiry_request(self.invoice_id)
        raw = self.get_raw(req_iso)
        print('Pemda terima inquiry request')
        from_iso = MultiDbTransaction()
        from_iso.setIsoContent(raw)
        print('Pemda kirim inquiry response')
        resp_iso = MultiDbTransaction(from_iso=from_iso, conf=self.conf)
        func = getattr(resp_iso, from_iso.get_func_name())
        func()
        self.get_raw(resp_iso)
        return resp_iso


if __name__ == '__main__':
    import os
    from pprint import pprint
    from optparse import OptionParser
    from common import get_streamer_module

    invoice_id = '2232002608150001'
    streamer_name = 'bjb_with_suffix'

    pars = OptionParser()
    pars.add_option('-i', '--invoice-id', default=invoice_id,
                    help='Invoice ID')
    pars.add_option('', '--streamer-name', default=streamer_name,
        help='Nama modul streamer, digunakan saat --raw, default: %s' % streamer_name)
    pars.add_option('-r', '--raw', help='Raw string yang dikirim remote host')    
    option, remain = pars.parse_args(sys.argv[1:])

    streamer_name = option.streamer_name
    conf = {'name': streamer_name}

    if not option.raw:
        test = InquiryTest(option.invoice_id, conf)
        test.request()
        sys.exit()

    if os.path.exists(option.raw):
        raw = open(option.raw).read().strip()
    else:
        raw = option.raw
    module = get_streamer_module(streamer_name)
    streamer = module.Streamer()
    raw_iso = streamer.get(raw)
    iso = DbTransaction(debug=True)
    iso.setIsoContent(raw_iso)
