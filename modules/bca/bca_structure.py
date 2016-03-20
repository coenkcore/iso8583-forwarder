# Penerjemahan file PDF Iso Spesification Pajak Daerah-BJB Ver 1.7

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
     2: ['PAN', 'Primary Account Number', 'LL', 2+97, 'n'],
     3: ['Processing', 'Processing Code', 'N', 6, 'n'], # '341019'
     4: ['Amount', 'Amount Transaction', 'N', 12, 'n'],
     7: ['Transmission', 'Transmission Datetime', 'N', 10, 'n'],
    11: ['STAN', 'System Trace Audit Number', 'N', 6, 'n'],
    12: ['Time', 'Time Local Transaction', 'N', 6, 'n'],
    13: ['Date', 'Date Local Transaction', 'N', 4, 'n'],
    15: ['Settlement', 'Settlement Date', 'N', 4, 'n'],
    18: ['Merchant', 'Merchant Type', 'N', 4, 'n'],
    22: ['POS', 'POS Entry Mode Code', 'N', 3, 'n'], # '021'
    32: ['Acquiring', 'Acquiring Institution Code', 'LL', 2+97, 'n'], # '110'
    33: ['Forwarding', 'Forwarding Institution ID Code', 'LL', 2+97, 'n'], # '00110'
    35: ['Track', 'Track 2 Data', 'LL', 2+97, 'n'],
    37: ['Sequence', 'Sequence Number', 'N', 12, 'n'],
    39: ['Response', 'Response Code', 'N', 2, 'n'],
    41: ['Terminal', 'Terminal Identification Number', 'N', 8, 'ans'],
    42: ['User', 'Terminal Name / User Identification', 'N', 15, 'ans'],
    43: ['Card', 'Card Acceptor Name / Location', 'ANS', 40, 'ans'],
    47: ['NTP', 'Nomor Transaksi Pemda', 'LLL', 3+996, 'ans'], # Payment
    #48: ['NTB', 'Nomor Transaksi Bank', 'LLL', 3+20, 'ans'], # Payment
    49: ['Currency', 'Transaction Currency Code', 'N', 3, 'n'],
    59: ['Additional', 'Additional Data', 'LLL', 3+996, 'ans'], # 'PAY'
    60: ['Pemda', 'Kode Pemda', 'LLL', 3+3, 'ans'],
    61: ['Invoice', 'Invoice ID', 'LLL', 3+996, 'ans'], # 1-18 NOP, 19-22 Tahun Pajak
    62: ['Profile', 'Invoice Profile', 'LLL', 3+996, 'ans'],
    63: ['Additional', 'Additional Data', 'LLL', 3+996, 'ans'], # '214'
    70: ['Function', 'System Function Code', 'N', 3, 'n'], # Echo test
    102: ['Source', 'Source Account Number', 'LL', 2+97, 'ans'],
    107: ['Cabang', 'Kode Cabang, User ID', 'LLL', 3+996, 'ans'], # 1-4 Kode Cabang, 5-8 User ID
    })

##########################
# Bit 3 to name function #
##########################
INQUIRY_CODE = ['341019','341066','300001','300801']
PAYMENT_CODE = ['541019','541066','500001','500801']

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
ERR_NOT_AVAILABLE = 'Invoice ID {invoice_id} tidak ada di SPPT'
ERR_ALREADY_PAID = 'Invoice ID {invoice_id} sudah dibayar'
ERR_ALREADY_PAID_2 = 'Invoice ID {invoice_id} sudah lunas, '\
                     'tagihannya Rp {nominal}'
ERR_AMOUNT = 'Invoice ID {invoice_id} belum lunas tapi nilai tagihannya ' + \
    '{nominal}'
ERR_INSUFFICIENT_FUND = 'Invoice ID {invoice_id} pembayaran {bayar} ' + \
    'tidak sama dengan {tagihan}'
ERR_INQUIRY_NOT_FOUND = 'Invoice ID {invoice_id} belum di-inquiry'
ERR_PAYMENT_NOT_FOUND = 'Payment request tidak ada'
ERR_PAYMENT_NOT_FOUND_2 = 'Pembayaran invoice ID {invoice_id} ke {ke} ' + \
    'tidak ada'
ERR_CREATE_PAYMENT = 'Ada masalah saat membuat payment ID'
ERR_REVERSAL_OWNER = 'Invoice ID {invoice_id} bukan dibayar oleh ' + \
    'Bank ID {bank_id}' 
ERR_INVOICE_OPEN = 'Status invoice ID {invoice_id} memang belum dibayar'
ERR_SETTLEMENT_DATE = 'Settlement date {raw} tidak benar'
ERR_TRANSACTION_DATETIME = 'Transaction datetime {raw} tidak benar'
ERR_TRANSACTION_DATE = 'Transaction date {raw} tidak benar'
