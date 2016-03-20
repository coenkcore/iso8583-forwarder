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
    2: ['PAN', 'Primary Account Number', 'LL', 99, 'n'],
    3: ['Processing', 'Processing Code', 'N', 6, 'n'], # 300001 / 500001
    4: ['Amount', 'Amount Transaction', 'N', 12, 'n'],
    12: ['Time', 'Time Local Transaction', 'N', 6, 'n'],
    13: ['Date', 'Date Local Transaction', 'N', 4, 'n'],
    15: ['Settlement', 'Settlement Date', 'N', 4, 'n'],
    18: ['Merchant', 'Merchant Type', 'N', 4, 'n'],  # 6010 Teller, 6011 ATM 
    22: ['POS', 'POS Entry Mode Code', 'N', 3, 'n'], # '021'
    32: ['Acquiring', 'Acquiring Institution Code', 'LL', 99, 'n'], # '110'
    33: ['Forwarding', 'Forwarding Institution ID Code', 'LL', 99, 'n'], # '00110'
    35: ['Track', 'Track 2 Data', 'LL', 99, 'n'],
    37: ['Sequence', 'Sequence Number', 'N', 12, 'n'],
    39: ['Response Code', 'Response Code', 'N', 2, 'n'],
    41: ['Terminal', 'Terminal Identification Number', 'ANS', 8, 'ans'],
    42: ['User', 'Terminal Name / User Identification', 'N', 15, 'ans'],
    43: ['Card', 'Card Acceptor Name / Location', 'ANS', 40, 'ans'],
    47: ['NTP', 'Nomor Transaksi Pemda', 'LL', 99, 'ans'],
    48: ['NTB', 'Nomor Transaksi Bank', 'LL', 99, 'ans'],
    49: ['Currency', 'Transaction Currency Code', 'N', 3, 'n'],
    59: ['Additional Data', 'Additional Data', 'LL', 99, 'ans'], # 'PAY'
    60: ['Kode Pemda', 'Kode Pemda', 'LL', 99, 'ans'],
    61: ['Invoice ID', 'Invoice ID', 'LL', 99, 'ans'],
    62: ['Invoice Profile', 'Invoice Profile', 'LLL', 999, 'ans'],
    63: ['Additional', 'Additional Data', 'LL', 99, 'n'], # '214'
   102: ['Source', 'Source Account Number', 'LL', 99, 'n'],
   107: ['Cabang', 'Kode Cabang', 'LLL', 999, 'n'],
    })


#########################
# Response Code, Bit 39 #
#########################
RC_OK = '00'
RC_INVALID_NUMBER = '33'
RC_ALREADY_PAID = '54'
RC_NOT_AVAILABLE = '55'
RC_INSUFFICIENT_FUND = '51'
RC_OTHER_ERROR = '76'
RC_LINK_DOWN = '91'

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
INQUIRY_CODE = '300001'
PAYMENT_CODE = '500001'

#####################
# Bit 15 Settlement #
#####################
DATE = [
    ['Bulan', 2, 'N'],
    ['Tanggal', 2, 'N'],
    ]

##########
# Bit 61 #
##########
INVOICE_ID = [
    ['Tahun', 4, 'N'],
    ['Bulan', 2, 'N'],
    ['Usaha ID', 2, 'N'],
    ['SPT No', 5, 'N'],
    ]


##########
# Bit 62 #
##########
INVOICE_PROFILE = [
    ['NPWPD', 30, 'A'],
    ['Nama', 35, 'A'],
    ['Alamat 1', 40, 'A'],
    ['Alamat 2', 40, 'A'],
    ['Tagihan', 12, 'N'],
    ['Denda', 12, 'N'],
    ['Total', 12, 'N'],
    ['Kode Rekening', 15, 'A'],
    ['Nama Rekening', 40, 'A'],
    ['Masa 1', 8, 'N'],
    ['Masa 2', 8, 'N'],
    ]
