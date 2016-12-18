from common.transaction.structure import BASE_TRANSACTION_BITS


TRANSACTION_BITS = BASE_TRANSACTION_BITS.copy()
TRANSACTION_BITS.update({
    47: ['NTP', 'Nomor Transaksi Pemda', 'LLL', 3+996, 'ans'], # Payment
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
INQUIRY_CODE = '341019'
PAYMENT_CODE = '541019'

#########################
# Response Code, Bit 39 #
#########################
RC_OK = '00'
RC_ALREADY_PAID = '54'
RC_NOT_AVAILABLE = '55'
RC_INSUFFICIENT_FUND = '51'
RC_OTHER_ERROR = '76'
RC_LINK_DOWN = '91'

####################
# Response Message #
####################
ERR_NOT_AVAILABLE = 'Invoice ID {invoice_id} tidak ada di SPPT'
ERR_NOT_AVAILABLE_2 = 'Invoice ID {invoice_id} tidak diperkenankan dibayar '\
                      'melalui jalur ini'
ERR_ALREADY_PAID = 'Invoice ID {invoice_id} sudah dibayar'
ERR_ALREADY_PAID_2 = 'Invoice ID {invoice_id} sudah lunas, '\
                     'tagihannya Rp {nominal}'
ERR_AMOUNT = 'Invoice ID {invoice_id} belum lunas tapi nilai tagihannya '\
             '{nominal}'
ERR_INSUFFICIENT_FUND = 'Invoice ID {invoice_id} pembayaran {bayar} '\
                        'tidak sama dengan {tagihan}'
ERR_INQUIRY_NOT_FOUND = 'Invoice ID {invoice_id} belum di-inquiry'
ERR_PAYMENT_NOT_FOUND = 'Payment request tidak ada'
ERR_PAYMENT_NOT_FOUND_2 = 'Pembayaran invoice ID {invoice_id} ke {ke} '\
                          'tidak ada'
ERR_CREATE_PAYMENT = 'Ada masalah saat membuat payment ID'
ERR_PAYMENT_OWNER = 'Invoice ID {invoice_id} bukan dibayar oleh '\
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
