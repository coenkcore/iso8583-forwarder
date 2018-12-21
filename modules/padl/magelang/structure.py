from common.transaction.structure import BASE_TRANSACTION_BITS


TRANSACTION_BITS = BASE_TRANSACTION_BITS.copy()
TRANSACTION_BITS.update({
    41: ['PAN', 'Primary Account Number', 'ANS', 10, 'ans'],
    48: ['Invoice', 'Invoice Profile', 'LLL', 999, 'ans'],
    60: ['Reserved', 'reserved', 'LLL', 999, 'ans'],
    90: ['ODE', 'Original Data Element', 'LLL', 999, 'ans'],
    })

#########################
# Response Code, Bit 39 #
#########################
RC_INVALID_NUMBER = '33'
RC_ALREADY_PAID = '01'
RC_NOT_AVAILABLE = '99'
RC_INSUFFICIENT_FUND = '51'
RC_LINK_DOWN = '91'
RC_REVERSAL = '88'

##########################
# Bit 3 to name function #
##########################
INQUIRY_CODE  = '004905'
PAYMENT_CODE  = '004903'
PRINT_CODE    = '004907'
REVERSAL_CODE = '004909'

########################
# ID Billing di bit 48 #
########################
INVOICE_ID = [
    ['Area', 2, 'N'],
    ['Tahun', 4, 'N'],
    ['SPT No', 6, 'N'],
    ]

##########
# Bit 48 #
##########
INVOICE_PROFILE = [
    ['Kode Bank', 2 , 'N'],
    ['ID Billing', 22, 'A'],
    ['NPWPD', 30, 'A'],
    ['Nama OP', 70, 'A'],
    ['Bulan', 2, 'N'],
    ['Tahun', 4, 'N'],
    ['Tanggal Penetapan', 10, 'A'],  #'dd-mm-yyyy'
    ['Tanggal Jatuh Tempo',10, 'A'],
    ['NTPD', 35,'N'],
    ['Tagihan Pokok', 12,'N'],
    ['Jenis Pajak', 50, 'A'],
    ['Masa Pajak',80,'A'],
    ['Uraian Kegiatan', 150, 'A'],
    ['Denda', 12,'N'],
    ]
