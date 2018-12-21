from datetime import datetime
from .structure import (
    INQUIRY_CODE,
    PAYMENT_CODE,
    TRANSACTION_BITS,
    )
from .transaction import Transaction


def inquiry_request(iso, invoice_id, bank_id):
    kini = datetime.now()
    iso.setBit(2, kini.strftime('%Y%m%d%H%M%S'))
    iso.set_transaction_code(INQUIRY_CODE)
    iso.setBit(12, kini.strftime('%H%M%S'))
    iso.setBit(13, kini.strftime('%m%d'))
    iso.setBit(15, kini.strftime('%m%d'))
    iso.setBit(18, '6010')
    iso.setBit(22, '021')
    iso.setBit(32, bank_id)
    iso.setBit(33, '00110')
    iso.setBit(35, '')
    iso.setBit(37, kini.strftime('%H%M%S'))
    iso.set_invoice_id(invoice_id)


def payment_request(iso, inq_resp_iso):
    REQUEST_BITS = TRANSACTION_BITS.keys()
    for bit in (39, 70):
        i = REQUEST_BITS.index(bit)
        del REQUEST_BITS[i]
    iso.copy(REQUEST_BITS, inq_resp_iso)
    iso.set_transaction_code(PAYMENT_CODE)
    ntb = datetime.now().strftime('%Y%m%d%H%M%S')
    iso.set_ntb(ntb)
