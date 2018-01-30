from datetime import datetime
from .structure import (
    INQUIRY_CODE,
    PAYMENT_CODE,
    )


def inquiry_request(iso, module_name, invoice_id, bank_id):
    inquiry_code = INQUIRY_CODE
    kini = datetime.now()
    iso.setBit(2, kini.strftime('%Y%m%d%H%M%S')) 
    iso.set_transaction_code(inquiry_code) 
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
    iso.setBit(43, 'Test Bank')
    iso.setBit(49, '390')
    iso.setBit(59, 'PAY')
    iso.setBit(60, '142')
    iso.setBit(61, invoice_id)
    iso.setBit(63, '')
    iso.setBit(102, '')
    iso.setBit(107, '')
 

def payment_request(iso, module_name, inq_resp_iso, bank_id):
    iso.copy(
        [4, 12, 13, 15, 18, 22, 32, 33, 35, 37, 41, 42, 43, 49, 59, 60, 61, 63,
         102, 107], inq_resp_iso)
    iso.set_transaction_code(PAYMENT_CODE)
    ntb = datetime.now().strftime('%Y%m%d%H%M')
    iso.set_ntb(ntb)
