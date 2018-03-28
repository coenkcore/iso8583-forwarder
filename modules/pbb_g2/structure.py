from common.pbb.structure import INVOICE_PROFILE as BASE_INVOICE_PROFILE


INVOICE_PROFILE = BASE_INVOICE_PROFILE + [
    ('Discount', 12, 'N'),
    ('Tahun Sisa', 4, 'N'),
    ]
