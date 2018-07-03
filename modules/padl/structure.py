from common.transaction.structure import BASE_TRANSACTION_BITS


TRANSACTION_BITS = BASE_TRANSACTION_BITS.copy()
TRANSACTION_BITS.update({
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

####################
# Response Message #
####################
ERR_INVALID_NUMBER = 'Invoice ID {invoice_id} tidak benar'
ERR_NOT_AVAILABLE = 'Invoice ID {invoice_id} tidak ada'
ERR_ALREADY_PAID = 'Invoice ID {invoice_id} sudah lunas'
ERR_ALREADY_PAID_2 = 'Invoice ID {invoice_id} status tertagih tapi '\
    'sudah ada pembayaran'
ERR_AMOUNT = 'Invoice ID {invoice_id} belum lunas tapi nilai tagihannya '\
    '{nominal}'
ERR_INSUFFICIENT_FUND = 'Invoice ID {invoice_id} pembayaran Rp {bayar} '\
    'tidak sama dengan tagihan Rp {tagihan}'
ERR_OTHER = 'Status {status} belum terdaftar'
ERR_NTB = 'NTB {ntb} atas pembayaran invoice ID {invoice_id} tidak '\
    'sesuai'
ERR_PAYMENT = 'Pembayaran untuk invoice ID {invoice_id} tidak ditemukan'
ERR_ISO_PAYMENT = 'Pembayaran melalui H2H untuk invoice ID {invoice_id} '\
    'tidak ditemukan'
ERR_PAYMENT_OWNER = 'Bukan pemilik pembayaran invoice ID {invoice_id}'
ERR_INVOICE_OPEN = 'Status invoice ID {invoice_id} memang belum dibayar'

##########################
# Bit 3 to name function #
##########################
INQUIRY_CODE = '300001'
PAYMENT_CODE = '500001'

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
