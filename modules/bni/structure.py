# Bersumber dari file yang dikirim oleh Bu Yardian Wensdi pada 25-9-2017
# bernama "Technical Specification ISO 8583.pdf". Pada halaman 2 tertulis
# Release 1.0, 2017, Arvid Theodorus.

from network.structure import NETWORK_BITS

#################
# Redefine bits #
#################
TRANSACTION_BITS = NETWORK_BITS.copy()
TRANSACTION_BITS.update({
     3: ['Processing', 'Processing Code', 'N', 6, 'n'],
     4: ['Amount', 'Transaction Amount', 'N', 12, 'n'],
     7: ['Transmission', 'Transmission Date and Time', 'N', 10, 'n'],
    11: ['STAN', 'System Trace Audit Number', 'N', 6, 'n'],
    32: ['Acquiring', 'Acquiring Institution Code', 'LL', 2+11, 'n'],
    33: ['Forwarding', 'Forwarding Institution ID Code', 'LL', 2+97, 'n'],
    37: ['Sequence', 'Retrieval Reference Number', 'N', 12, 'n'],
    48: ['Additional', 'Additional Data', 'LLL', 3+200, 'ans'],
    90: ['Original', 'Original Data Element', 'LLL', 3+31, 'ans'],
    })

BIT_NTB = 37
BIT_INVOICE_ID = BIT_INVOICE_PROFILE = 48

##########################
# Bit 3 to name function #
##########################
# Pajak Bumi dan Bangunan
PBB_INQUIRY_CODE = '360000'
PBB_PAYMENT_CODE = '560000'

#########################
# Response Code, Bit 39 #
#########################
RC_INSUFFICIENT_FUND = '03'
RC_OTHER = '04'
RC_CREATE_PAYMENT = '05'
RC_NOT_AVAILABLE = '10'
RC_ALREADY_PAID = '13'
RC_PAYMENT_NOT_FOUND = '06'
RC_ALREADY_CANCELLED = '94'

###########################
# Invoice Profile, Bit 48 #
###########################
INVOICE_PROFILE = [
    ('Invoice ID', 22, 'N'),
    ('Nama Wajib Pajak', 30, 'A'),
    ('Kecamatan', 30, 'A'),
    ('Alamat Objek Pajak', 45, 'A'),
    ('Tagihan Pokok', 12, 'N'),
    ('Denda', 12, 'N'),
    ('Total Tagihan', 12, 'N'), # Pokok + Denda
    ('NTP', 16, 'N'), # Nomor Transaksi Pemda
    ]

####################
# Response Message #
####################
ERR_INSUFFICIENT_FUND = 'Invoice ID {invoice_id} pembayaran {bayar} '\
    'tidak sama dengan {tagihan}'
ERR_NTP = 'Ada kesalahan saat membuat NTP'
ERR_NOT_AVAILABLE = 'Invoice ID {invoice_id} tidak ada'
ERR_ALREADY_PAID = 'Invoice ID {invoice_id} sudah dibayar'
ERR_ALREADY_PAID_2 = 'Invoice ID {invoice_id} sudah lunas, '\
                     'tagihannya Rp {nominal}'
ERR_AMOUNT = 'Invoice ID {invoice_id} belum lunas tapi nilai tagihannya '\
    '{nominal}'
ERR_INQUIRY_NOT_FOUND = 'Invoice ID {invoice_id} belum di-inquiry'
ERR_PAYMENT_NOT_FOUND = 'Payment request tidak ada'
ERR_PAYMENT_NOT_FOUND_2 = 'Pembayaran invoice ID {invoice_id} tidak melalui '\
    'jalur ini'
ERR_PAYMENT_OWNER = 'Bukan pemilik pembayaran invoice ID {invoice_id}'
ERR_CREATE_PAYMENT = 'Ada masalah saat membuat payment ID'
ERR_REVERSAL_OWNER = 'Invoice ID {invoice_id} bukan dibayar oleh '\
    'Bank ID {bank_id}' 
ERR_INVOICE_OPEN = 'Status invoice ID {invoice_id} memang belum dibayar'
