module_name = 'depok'

db_url = 'postgresql://bphtb:FIXME@localhost:5432/bphtb_fix_pay'

# Tuning
# http://docs.sqlalchemy.org/en/rel_0_9/core/pooling.html
db_pool_size = 50
db_max_overflow = 100

host = {
    'bjb': {
        'kd_kanwil_bank': '22',
        'kd_kppbb_bank': '11',
        'kd_bank_tunggal': '03',
        'kd_bank_persepsi': '02',
        'kd_tp': '06',
        'akhiran_nol_pada_luas': 3,
        },
    'pos': {
        'kd_kanwil_bank': '22',
        'kd_kppbb_bank': '11',
        'kd_bank_tunggal': '03',
        'kd_bank_persepsi': '02',
        'kd_tp': '57',
        'akhiran_nol_pada_luas': 3,
        },
    }
