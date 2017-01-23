from datetime import datetime
from random import randrange
from structure import (
    INQUIRY_CODE,
    PAYMENT_CODE,
    )


kode_wilayah = '71'

def inquiry_request(iso, module_name, invoice_id, bank_id):
    kini = datetime.now()
    invoice_id_by_teller = kode_wilayah + invoice_id
    data = { 2: '0000000000000000000',
             3: INQUIRY_CODE, 
            # 7: '1222103027',
            11: randrange(100000, 999999),
            12: kini.strftime('%H%M%S'),
            13: kini.strftime('%m%d'),
            15: kini.strftime('%m%d'),
            18: '6010',
            37: kini.strftime('%H%M%S'),
            41: 'W001DS58  ',
            48: kode_wilayah + invoice_id_by_teller.rjust(22)}
    for bit in data:
        value = data[bit]
        iso.setBit(bit, value)

def payment_request(iso, module_name, inq_resp_iso, bank_id):
    ntb = datetime.now().strftime('%Y%m%d%H%M')
    iso.copy([4, 12, 13, 15, 18, 37, 48], inq_resp_iso)
    data = { 3: PAYMENT_CODE,
            90: ntb}
    for bit in data:
        value = data[bit]
        iso.setBit(bit, value)
