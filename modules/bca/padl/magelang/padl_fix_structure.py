#################
# Redefine bits #
#################
NETWORK_BITS = {
    7: ['Transmission', 'Transmission Datetime', 'N', 10, 'n'],
    11: ['STAN', 'System Trace Audit Number', 'N', 6, 'n'],
    39: ['Response', 'Response Code', 'N', 2, 'n'],
    # 001: sign on, 002: sign off, 301: echo test
    70: ['Function', 'System Function Code', 'N', 3, 'n'],
    }

TRANSACTION_BITS = NETWORK_BITS.copy()
TRANSACTION_BITS.update({
    41: ['Terminal ID', 'Primary Account Number', 'ANS', 10, 'ans'],
    18: ['Merchant', 'Merchant Type', 'N', 4, 'n'],
    90: ['ODE', 'Original Data Element', 'LLL', 999, 'ans'],
    60: ['Reserved', 'reserved', 'LLL', 999, 'ans'],
    })

#########################
# Response Code, Bit 39 #
#########################
RC_OK = '00'
RC_INVALID_NUMBER = '33'
RC_ALREADY_PAID = '01'
RC_NOT_AVAILABLE = '99'
RC_INSUFFICIENT_FUND = '51'
RC_OTHER_ERROR = '76'
RC_LINK_DOWN = '91'
RC_REVERSAL = '88'

####################
# Response Message #
####################
ERR_INVALID_NUMBER = 'Invoice ID {invoice_id} tidak benar'
ERR_NOT_AVAILABLE = 'Invoice ID {invoice_id} tidak ada'
ERR_ALREADY_PAID = 'Invoice ID {invoice_id} sudah lunas'
ERR_ALREADY_PAID_2 = 'Invoice ID {invoice_id} status tertagih tapi ' + \
                     'sudah ada pembayaran'
ERR_AMOUNT = 'Invoice ID {invoice_id} belum lunas tapi nilai tagihannya ' + \
             '{nominal}'
ERR_INSUFFICIENT_FUND = 'Invoice ID {invoice_id} pembayaran {bayar} ' + \
    'tidak sama dengan {tagihan}'
ERR_OTHER = 'Status {status} belum terdaftar'
ERR_REVERSAL_DONE = 'Invoice ID {invoice_id} memang sudah dibatalkan'
ERR_PAYMENT_NOT_FOUND = 'Pembayaran untuk invoice ID {invoice_id} tidak ditemukan'
ERR_SETTLEMENT_DATE = 'Settlement date {raw} tidak benar'
ERR_TRANSACTION_TIME = 'Transaction datetime {raw} tidak benar'


##########################
# Bit 3 to name function #
##########################
INQUIRY_CODE  = '004905'
PAYMENT_CODE  = '004903'
PRINT_CODE    = '004907'
REVERSAL_CODE = '004909'

#####################
# Bit 15 Settlement #
#####################
DATE = [
    ['Bulan', 2, 'N'],
    ['Tanggal', 2, 'N'],
    ]

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
    ['Tanggal Penetapan', 10, 'A'], #'dd-mm-yyyy'
    ['Tanggal Jatuh Tempo',10, 'A'],
    ['NTPD', 35,'N'],
    ['Tagihan Pokok', 12,'N'],
    ['Jenis Pajak', 50, 'A'],
    ['Masa Pajak',80,'A'],
    ['Uraian Kegiatan', 150, 'A'],
    ['Denda', 12,'N'],
    ]
