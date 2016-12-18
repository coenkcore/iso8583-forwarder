from sqlalchemy import create_engine
from base_models import (
    Base,
    DBSession,
    )
from models import Models
from sismiop.query import (
    Query,
    sppt2nop,
    CalculateInvoice,
    )
from multi.transaction import Transaction


class Inquiry(Transaction):
    def inquiry_request(self, invoice_id):
        self.set_transaction_request()
        kini = datetime.now()
        self.setBit(2, kini.strftime('%Y%m%d%H%M%S')) 
        self.setBit(3, INQUIRY_CODE)
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


class TestInquiry(Test):
    def __init__(self, invoice_id):
        self.invoice_id = invoice_id

    def run(self):
        print('Bank kirim inquiry request')
        req_iso = Inquiry()
        req_iso.inquiry_request(self.invoice_id)
        raw = self.get_raw(req_iso)
        print('Pemda terima inquiry request')
        from_iso = Transaction()
        from_iso.setIsoContent(raw)
        print('Pemda kirim inquiry response')
        resp_iso = DbTransaction(from_iso=from_iso, conf=self.conf)
        func = getattr(resp_iso, from_iso.get_func_name())
        func()
        self.get_raw(resp_iso)
        return resp_iso
