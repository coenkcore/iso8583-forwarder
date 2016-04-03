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
    ['kode', 22, 'N'],
    # ['tahun', 4, 'N'],
    # #['bulan', 2, 'N'],
    # #['usaha_id', 2, 'N'],
    # ['spt_no', 6, 'N'],
     ]


##########
# Bit 62 #
##########
INVOICE_PROFILE = [
    ('npwpd', 22,'ANS'),
    ('nama', 35,'ANS'),
    ('alamat', 40,'ANS'),
    ('alamat2', 40,'ANS'),
    ('tagihan', 12,'N'),
    ('denda', 12,'N'),
    ('jumlah', 12,'N'),
    ('kode_pajak', 20,'ANS'),
    ('nama_pajak', 40,'ANS'),
    ('kode_skpd', 20,'ANS'),
    ('nama_skpd',40,'ANS'),
    ('jth_tempo', 8 ,'N'),
    ('masa_pajak', 25 ,'ANS'),
]
