from common.transaction.structure import BASE_TRANSACTION_BITS


TRANSACTION_BITS = BASE_TRANSACTION_BITS.copy()
TRANSACTION_BITS.update({
    47: ['NTP', 'Nomor Transaksi Pemda', 'LLL', 3+996, 'ans'], # Payment
    48: ['NTB', 'Nomor Transaksi Bank', 'LLL', 3+996, 'ans'], # Payment
    49: ['Currency', 'Transaction Currency Code', 'N', 3, 'n'],
    59: ['Additional', 'Additional Data', 'LLL', 3+996, 'ans'], # 'PAY'
    60: ['Pemda', 'Kode Pemda', 'LLL', 3+3, 'ans'],
    61: ['Invoice', 'Invoice ID', 'LLL', 3+996, 'ans'],
    62: ['Profile', 'Invoice Profile', 'LLL', 3+996, 'ans'],
    63: ['Additional', 'Additional Data', 'LLL', 3+996, 'ans'], # '214'
    102: ['Source', 'Source Account Number', 'LL', 2+97, 'ans'],
    107: ['Cabang', 'Kode Cabang, User ID', 'LLL', 3+996, 'ans'], # 1-4 Kode Cabang, 5-8 User ID
    })

##########################
# Bit 3 to name function #
##########################
# Pajak Bumi dan Bangunan
PBB_INQUIRY_CODE   = '341019'
PBB_PAYMENT_CODE   = '541019'
# Biaya Penjualan atas Hak Tanah dan Bangunan
BPHTB_INQUIRY_CODE = '341066'
BPHTB_PAYMENT_CODE = '541066'
# Pendapatan Asli Daerah Lainnya
PADL_INQUIRY_CODE  = '300001'
PADL_PAYMENT_CODE  = '500001'
# Web Register - SAMSAT
WEBR_INQUIRY_CODE  = '300020'
WEBR_PAYMENT_CODE  = '500020'

#########################
# Response Code, Bit 39 #
#########################
RC_ALREADY_PAID = '54'
RC_NOT_AVAILABLE = '55'
RC_INSUFFICIENT_FUND = '51'

####################
# Response Message #
####################
ERR_NOT_ALLOWED = 'Bank ID {bank_id} tidak diperkenankan'
ERR_NOT_AVAILABLE = 'Invoice ID {invoice_id} tidak ada'
ERR_ALREADY_PAID = 'Invoice ID {invoice_id} sudah dibayar'
ERR_ALREADY_PAID_2 = 'Invoice ID {invoice_id} sudah lunas, '\
                     'tagihannya Rp {nominal}'
ERR_AMOUNT = 'Invoice ID {invoice_id} belum lunas tapi nilai tagihannya '\
    '{nominal}'
ERR_INSUFFICIENT_FUND = 'Invoice ID {invoice_id} pembayaran {bayar} '\
    'tidak sama dengan {tagihan}'
ERR_INQUIRY_NOT_FOUND = 'Invoice ID {invoice_id} belum di-inquiry'
ERR_PAYMENT_NOT_FOUND = 'Payment request tidak ada'
ERR_PAYMENT_NOT_FOUND_2 = 'Pembayaran invoice ID {invoice_id} tidak melalui '\
    'jalur ini'
ERR_PAYMENT_OWNER = 'Bukan pemilik pembayaran invoice ID {invoice_id}'
ERR_CREATE_PAYMENT = 'Ada masalah saat membuat payment ID'
ERR_REVERSAL_OWNER = 'Invoice ID {invoice_id} bukan dibayar oleh '\
    'Bank ID {bank_id}' 
ERR_INVOICE_OPEN = 'Status invoice ID {invoice_id} memang belum dibayar'
ERR_SETTLEMENT_DATE = 'Settlement date {raw} tidak benar'
ERR_TRANSACTION_DATETIME = 'Transaction datetime {raw} tidak benar'
ERR_TRANSACTION_DATE = 'Transaction date {raw} tidak benar'

# Bit 107 Cabang
CABANG = [
    ('kode', 4, 'A'),
    ('user', 4, 'A'),
    ]

