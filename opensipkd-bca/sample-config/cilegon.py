module_name = 'cilegon'

#db_url = 'postgresql://pbb:FIXME@localhost/pbb'
db_url = ''

# Tuning
# http://docs.sqlalchemy.org/en/rel_0_9/core/pooling.html
db_pool_size = 50
db_max_overflow = 100

# Ada pemda yang tidak memiliki tabel dat_objek_pajak
dat_objek_pajak = False

# Denda bila lewat jatuh tempo
persen_denda = 2.0

nip_rekam_byr_sppt = '999999999'

host = {
    'bjb_with_suffix': {
        'kd_kanwil': '01',
        'kd_kantor': '01',
        'kd_bank_tunggal': '00',
        'kd_bank_persepsi': '00',
        'kd_tp': {'default': '01'},
        }
    'bri': {
        'kd_kanwil': '22',
        'kd_kantor': '11',
        'kd_bank_tunggal': '01',
        'kd_bank_persepsi': '01',
        # field kd_tp dipengaruhi channel
        'kd_tp': {
            '6010': '16',
            '6011': '15',
            'default': '16'},
        },
    }

# Mapping field karena beberapa lokasi nama field-nya berbeda.
fields  = {
    'kd_kanwil_bank': 'kd_kanwil',
    'kd_kppbb_bank': 'kd_kantor',
}

