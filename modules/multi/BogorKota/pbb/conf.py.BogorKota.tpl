db_url = 'postgresql://user:pass@localhost/db'
db_schema = None 
iso_db_schema = 'pbb'

# Tuning
# http://docs.sqlalchemy.org/en/rel_0_9/core/pooling.html
db_pool_size = 50
db_max_overflow = 100

# Denda bila lewat jatuh tempo
persen_denda = 2

nip_rekam_byr_sppt = '999999999'

host = {
    'bjb': {
        'kd_kanwil': '01',
        'kd_kantor': '01',
        'kd_tp': { # Bit 18 Channel
            '6010': '69', # H2H Teller
            '6011': '71', # H2H ATM
            '6012': '72', # H2H POS
            '6013': '73', # H2H Phone Banking
            '6014': '74', # H2H Internet Banking
            '6015': '75', # H2H Kiosk
            '6016': '76', # H2H Autodebet
            '6017': '77', # H2H Mobile Banking
            'default': '20',
            },
        },
    'pos': {
        'kd_kanwil': '01',
        'kd_kantor': '01',
        'kd_tp': '93',
        },
    'btn': {
        'kd_kanwil': '01',
        'kd_kantor': '01',
        'kd_tp': '41',
        },
    }
