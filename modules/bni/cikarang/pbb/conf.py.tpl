db_url = 'postgresql://sugiana:a@localhost/majalengka_pbb'
db_schema = None 
iso_db_schema = None 

# Tuning
# http://docs.sqlalchemy.org/en/rel_0_9/core/pooling.html
db_pool_size = 50
db_max_overflow = 100

# Denda bila lewat jatuh tempo
persen_denda = 2

nip_rekam_byr_sppt = '999999999'

host = {
    'bjb': {
        'kd_kanwil': '22',
        'kd_kantor': '14',
        'kd_tp': '01',
        },
    'bni': {
        'kd_kanwil': '22',
        'kd_kantor': '14',
        'kd_tp': '06',
        },
    }
