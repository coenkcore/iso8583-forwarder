from common.transaction.structure import BASE_TRANSACTION_BITS


TRANSACTION_BITS = BASE_TRANSACTION_BITS.copy()
TRANSACTION_BITS.update({
    47: ['NTP', 'Nomor Transaksi Pemda', 'LLL', 3+996, 'ans'],
    48: ['NTB', 'Nomor Transaksi Bank', 'LLL', 3+996, 'ans'],
    49: ['Currency', 'Transaction Currency Code', 'N', 3, 'n'],
    59: ['Additional Data', 'Additional Data', 'LLL', 3+996, 'ans'], # 'PAY'
    60: ['Kode Pemda', 'Kode Pemda', 'LLL', 3+996, 'ans'],
    61: ['Invoice ID', 'Invoice ID', 'LLL', 3+996, 'ans'],
    62: ['Invoice Profile', 'Invoice Profile', 'LLL', 3+996, 'ans'],
    63: ['Additional', 'Additional Data', 'LLL', 3+996, 'n'], # '214'
   102: ['Source', 'Source Account Number', 'LL', 2+97, 'n'],
   107: ['Cabang', 'Kode Cabang', 'LLL', 3+996, 'n'],
    })

REQUEST_BITS = TRANSACTION_BITS.keys()
for bit in (39, 70):
    i = REQUEST_BITS.index(bit)
    del REQUEST_BITS[i]

#########################
# Response Code, Bit 39 #
#########################
RC_INVALID_NUMBER = '33'
RC_ALREADY_PAID = '54'
RC_NOT_AVAILABLE = '55'
RC_INSUFFICIENT_FUND = '51'

####################
# Response Message #
####################
ERR_INVALID_NUMBER = 'Invoice ID {invoice_id} tidak benar'
ERR_NOT_AVAILABLE = 'Invoice ID {invoice_id} tidak ada'
ERR_ALREADY_PAID = 'Invoice ID {invoice_id} sudah lunas'
ERR_AMOUNT = 'Invoice ID {invoice_id} belum lunas tapi nilai tagihannya '\
    '{nominal}'
ERR_INSUFFICIENT_FUND = 'Invoice ID {invoice_id} pembayaran {bayar} '\
    'tidak sama dengan {tagihan}'
ERR_PAYMENT_OWNER = 'Bukan pemilik pembayaran invoice ID {invoice_id}'
ERR_NTB = 'NTB {ntb} atas pembayaran invoice ID {invoice_id} tidak '\
    'sesuai'
ERR_PAYMENT = 'Pembayaran untuk invoice ID {invoice_id} tidak ditemukan'
ERR_ISO_PAYMENT = 'Pembayaran melalui H2H untuk invoice ID {invoice_id} '\
    'tidak ditemukan'
ERR_INVOICE_OPEN = 'Status invoice ID {invoice_id} memang belum dibayar'

##########################
# Bit 3 to name function #
##########################
INQUIRY_CODE = '300002'
PAYMENT_CODE = '500002'

##########
# Bit 62 #
##########
INVOICE_PROFILE = [
    ['No Bayar', 15, 'A'],
    ['Kode Izin', 3, 'N'],
    ['Nama Izin', 35, 'A'],
    ['Jenis Layanan', 35, 'A'],
    ['No Resi', 15, 'A'],
    ['Pemohon', 35, 'A'],
    ['Lokasi', 35, 'A'],
    ['Tagihan',12, 'N'],
    ['Denda',12,'N'],
    ['Total', 12, 'N'],
    ['Pesan',150,'A'],
    ]
