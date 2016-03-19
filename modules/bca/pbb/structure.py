
#############################################
# Bit 3 to invoice data structure in bit 61 #
#############################################
INVOICE_ID = [
    ('Propinsi', 2, 'N'),
    ('Kabupaten', 2, 'N'),
    ('Kecamatan', 3, 'N'),
    ('Kelurahan', 3, 'N'),
    ('Blok', 3, 'N'),
    ('Urut', 4, 'N'),
    ('Jenis', 1, 'N'),
    ('Tahun Pajak', 4, 'N'),
    ]

#############################################
# Bit 3 to invoice data structure in bit 62 #
#############################################
INVOICE_PROFILE = [ 
    ('Propinsi', 2, 'N'),
    ('Kabupaten', 2, 'N'),
    ('Kecamatan', 3, 'N'),
    ('Kelurahan', 3, 'N'),
    ('Blok', 3, 'N'),
    ('Urut', 4, 'N'),
    ('Jenis', 1, 'N'),
    ('Tahun Pajak', 4, 'N'),
    ('Nama', 35),
    ('Lokasi', 35),
    ('Nama Kelurahan', 35),
    ('Nama Kecamatan', 35),
    ('Nama Propinsi', 35),
    ('Luas Tanah', 12, 'N'),
    ('Luas Bangunan', 12, 'N'),
    ('Jatuh Tempo', 8, 'N'),
    ('Tagihan', 12, 'N'),
    ('Denda', 12, 'N'),
    ('Total Bayar', 12, 'N'),
    ]



