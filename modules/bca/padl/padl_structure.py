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
    ['tahun', 4, 'N'],
    #['bulan', 2, 'N'],
    #['usaha_id', 2, 'N'],
    ['spt_no', 6, 'N'],
    ]


##########
# Bit 62 #
##########
INVOICE_PROFILE = [
    ('npwpd', 22,'N'),
    ('nama', 35,'ANS'),
    ('alamat', 35,'ANS'),
    ('kode_pajak', 15,'ANS'),
    ('nama_pajak', 35,'ANS'),
    ('jth_tempo', 8 ,'N'),
    ('tagihan', 12,'N'),
    ('denda', 12,'N'),
    ('jumlah', 12,'N'),
    ('masa_pajak', 20 ,'ANS'),
]
