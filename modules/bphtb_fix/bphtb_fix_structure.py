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
    3: ['Processing', 'Processing Code', 'N', 6, 'n'], # '341066'
    4: ['Amount', 'Amount Transaction', 'N', 12, 'n'],
    7: ['Transmission', 'Transmission Datetime', 'N', 10, 'n'],
    11: ['STAN', 'System Trace Audit Number', 'N', 6, 'n'],
    12: ['Time', 'Time Local Transaction', 'N', 6, 'n'],
    13: ['Date', 'Date Local Transaction', 'N', 4, 'n'],
    15: ['Settlement', 'Settlement Date', 'N', 4, 'n'],
    18: ['Merchant', 'Merchant Type', 'N', 4, 'n'],  # 6010 Teller, 6011 ATM 
    22: ['POS', 'POS Entry Mode Code', 'N', 3, 'n'], # '021'
    32: ['Acquiring', 'Acquiring Institution Code', 'LL', 2+11, 'n'], # '110'
    33: ['Forwarding', 'Forwarding Institution ID Code', 'LL', 2+11, 'n'], # '00110'
    35: ['Track', 'Track 2 Data', 'LL', 2+37, 'n'],
    37: ['Sequence', 'Sequence Number', 'N', 12, 'n'],
    #38: ['NTP', 'Nomor Transaksi Pemda', 'LL', 2+20, 'n'],
    39: ['Response', 'Response Code', 'N', 2, 'n'],
    41: ['Terminal', 'Terminal Identification Number', 'N', 8, 'ans'],
    42: ['User', 'Terminal Name / User Identification', 'N', 15, 'ans'],
    43: ['Card', 'Card Acceptor Name / Location', 'ANS', 40, 'ans'],
    47: ['Invoice Profile', 'Nomor Transaksi Pemda', 'LLL', 3+996, 'ans'], # Payment
    48: ['Invoice Profile 2', 'Nomor Transaksi Bank', 'LLL', 3+163, 'ans'], # Payment
    49: ['Currency', 'Transaction Currency Code', 'N', 3, 'n'],
    57: ['NTP', 'Nomor Transaksi Pemda', 'LLL', 3+996, 'ans'],
    58: ['NTB', 'Nomor Transaksi Bank', 'LLL', 3+996, 'ans'],
    59: ['Additional Data', 'Additional Data', 'LLL', 3+3, 'ans'], # 'PAY'
    60: ['Kode Pemda', 'Kode Pemda', 'LLL', 3+3, 'ans'],
    61: ['Invoice', 'Invoice ID', 'LLL', 3+20, 'ans'], # NOP 
    62: ['Nomor Permohonan', 'Nomor Permohonan', 'LLL', 3+20, 'ans'],
    63: ['Additional', 'Additional Data', 'LLL', 3+3, 'ans'], # '214'
    70: ['Function', 'System Function Code', 'N', 3, 'n'], # Echo test
    102: ['Source', 'Source Account Number', 'LL', 2+20, 'ans'],
    107: ['Cabang', 'Kode Cabang, User ID', 'LLL', 3+8, 'ans'], # 1-4 Kode Cabang, 5-8 User ID
    })

##########################
# Bit 3 to name function #
##########################
INQUIRY_CODE = '341066'
PAYMENT_CODE = '541066'

#############################################
# Bit 3 to invoice data structure in bit 47 #
#############################################
def get_invoice_profile(akhiran_nol_pada_luas=0):
    digit_luas = 6 + akhiran_nol_pada_luas
    return [
        ['Luas Tanah', digit_luas, 'N'],
        ['Luas Bangunan', digit_luas, 'N'],
        ['NPOP', 15, 'N'],
        ['Jenis Perolehan Hak', 2, 'N'],
        ['Nama Notaris', 40, 'A'],
        ['Nama Wajib Pajak', 40, 'A'],
        ['NPWP', 15, 'A'],
        ['Alamat WP', 50, 'A'],
        ['Alamat OP', 50, 'A'],
        ['Kota OP', 22, 'A'],
        ['Kelurahan WP', 22, 'A'],
        ['Kecamatan WP', 22, 'A'],
        ['Jumlah Bayar', 15, 'N'],
        ['Jumlah Denda', 15, 'N'],
        ]

INVOICE_PROFILE2 = [ 
    ['RT WP', 3, 'N'],
    ['RW WP', 3, 'N'],
    ['Kode Pos WP', 5, 'A'],
    ['Kelurahan OP', 20, 'A'],
    ['Kecamatan OP', 20, 'A'],
    ['Nama Bank', 30, 'A'],
    ['Nama KCP Bank', 30, 'A'],
    ['Nama Operator Bank', 30, 'A'],
    ['Tahun Pajak', 4, 'N'],
    ['Jenis Setoran', 1, 'A'],
    ['ID Operator Bank', 4, 'A'],
    ['Nomor Transaksi', 13, 'A'],
    ]

NOP = [
    ('Propinsi', 2, 'N'),
    ('Kabupaten', 2, 'N'),
    ('Kecamatan', 3, 'N'),
    ('Kelurahan', 3, 'N'),
    ('Blok', 3, 'N'),
    ('Urut', 4, 'N'),
    ('Jenis', 1, 'N'),
    ]

RC_OK = '00'
RC_INSUFFICIENT_FUND = '51'
RC_ALREADY_PAID = '54'
RC_NOT_AVAILABLE = '55'
RC_OTHER_ERROR = '76'
RC_LINK_DOWN = '91'

ERR_ALREADY_PAID = 'Invoice ID {invoice_id} sudah dibayar'
ERR_NOT_AVAILABLE = 'Invoice ID {invoice_id} tidak ada'
ERR_SETTLEMENT_DATE = 'Settlement date {raw} tidak benar'
ERR_TRANSMISSION_DATETIME = 'Transmission datetime {raw} tidak benar'
ERR_TRANSACTION_DATETIME = 'Transaction datetime {raw} tidak benar'
ERR_INSUFFICIENT_FUND = 'Invoice ID {invoice_id} pembayaran {bayar} '\
    'tidak sama dengan tagihan {tagihan}'
ERR_PAYMENT_NOT_FOUND = 'Pembayaran invoice ID {invoice_id} tidak ada'
ERR_INVOICE_OPEN = 'Status invoice ID {invoice_id} memang belum dibayar'
