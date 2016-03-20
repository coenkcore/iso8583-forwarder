# Penerjemahan file PDF Iso Spesification Pajak Daerah-BJB Ver 1.7
# mengenai BPHTB

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
    2: ['PAN', 'Primary Account Number', 'LL', 2+19, 'n'],
    3: ['Processing', 'Processing Code', 'N', 6, 'n'], # '341019'
    4: ['Amount', 'Amount Transaction', 'N', 12, 'n'],
    12: ['Time', 'Time Local Transaction', 'N', 6, 'n'],
    13: ['Date', 'Date Local Transaction', 'N', 4, 'n'],
    15: ['Settlement', 'Settlement Date', 'N', 4, 'n'],
    18: ['Merchant', 'Merchant Type', 'N', 4, 'n'],
    22: ['POS', 'POS Entry Mode Code', 'N', 3, 'n'], # '021'
    32: ['Acquiring', 'Acquiring Institution Code', 'LL', 2+11, 'n'], # '110'
    33: ['Forwarding', 'Forwarding Institution ID Code', 'LL', 2+11, 'n'], # '00110'
    35: ['Track', 'Track 2 Data', 'LL', 2+37, 'n'],
    37: ['Sequence', 'Sequence Number', 'N', 12, 'n'],
    41: ['Terminal', 'Terminal Identification Number', 'N', 8, 'ans'],
    42: ['User', 'Terminal Name / User Identification', 'N', 15, 'ans'],
    43: ['Card', 'Card Acceptor Name / Location', 'ANS', 40, 'ans'],
    47: ['Invoice Profile', 'Nomor Transaksi Pemda', 'LLL', 3+177, 'ans'], # Payment
    48: ['Invoice Profile 2', 'Nomor Transaksi Bank', 'LLL', 3+183, 'ans'], # Payment
    49: ['Currency', 'Transaction Currency Code', 'N', 3, 'n'],
    61: ['Invoice', 'Invoice ID', 'LLL', 3+22, 'ans'], # 1-18 NOP, 19-22 Tahun Pajak
    63: ['Additional', 'Additional Data', 'LLL', 3+3, 'ans'], # '214'
    102: ['Source', 'Source Account Number', 'LL', 2+20, 'ans'],
    107: ['Cabang', 'Kode Cabang, User ID', 'LLL', 3+8, 'ans'], # 1-4 Kode Cabang, 5-8 User ID
    })

##########################
# Bit 3 to name function #
##########################
PAYMENT_CODE = '541066'

#############################################
# Bit 3 to invoice data structure in bit 61 #
#############################################
NOP = [
    ('Propinsi', 2, 'N'),
    ('Kabupaten', 2, 'N'),
    ('Kecamatan', 3, 'N'),
    ('Kelurahan', 3, 'N'),
    ('Blok', 3, 'N'),
    ('Urut', 4, 'N'),
    ('Jenis', 1, 'N'),
    ] 

##########
# Bit 47 #
##########
INVOICE_PROFILE = [
    ('Luas Tanah', 9, 'N'),
    ('Luas Bangunan', 6, 'N'),
    ('NPOP', 15, 'N'),
    ('Jenis Perolehan Hak', 2, 'N'),
    ('Nama Notaris', 40, 'A'),
    ('Nama WP', 40, 'A'),
    ('NPWP', 15, 'A'),
    ('Alamat WP', 50, 'A'),
    ]

##########
# Bit 48 #
##########
INVOICE_PROFILE2 = [ 
    ('RT WP', 3, 'A'),
    ('RW WP', 3, 'A'),
    ('Kode Pos WP', 5, 'A'),
    ('Kelurahan WP', 20, 'A'),
    ('Kecamatan WP', 20, 'A'),
    ('Nama Bank', 30, 'A'),
    ('Nama KCP Bank', 30, 'A'),
    ('Nama Operator Bank', 30, 'A'),
    ('Tahun Pajak', 4, 'N'),
    ('Jenis Setoran', 1, 'A'),
    ('ID Operator Bank', 4, 'A'),
    ('Nomor Transaksi', 13, 'A'),
    ]

BANK_PROFILE = [
    ('Kode Cabang', 4, 'A'),
    ('User ID', 4, 'A'),
    ]

#####################
# Response Messages #
#####################
RC_OK = '00'
RC_INVALID_ID = '33'

RC_INSUFFICIENT_FUND = '51'
RC_ALREADY_CANCELED = '54'
RC_NOT_AVAILABLE = '55'
RC_OTHER_ERROR = '76'
RC_LINK_DOWN = '91'

ERR_NOP = 'NOP {nop} tidak benar'
ERR_NOT_AVAILABLE = 'SPPT untuk NOP {nop} tahun {tahun} tidak ada'
ERR_PROFILE = 'Invoice Profile {profile} tidak benar'
ERR_PROFILE2 = 'Invoice Profile 2 {profile} tidak benar'
ERR_BANK_PROFILE = 'Bank Profile {profile} tidak benar'
ERR_PAYMENT_NOT_FOUND = 'Payment request untuk NOP {nop} '\
        'STAN {stan} tidak ada'
ERR_ALREADY_CANCELED = 'NOP {nop} STAN {stan} memang sudah dibatalkan'
