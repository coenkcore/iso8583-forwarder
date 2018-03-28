db_url = 'postgresql://sugiana:a@localhost/padl_bogor_kota'
db_schema = 'pad'

# True jika multi/conf.py module_name = 'BogorKota' atau
# tepatnya jika modul lain menggunakan struktur tabel ISO
# yang sama.
load_iso_models = True

# Tuning
# http://docs.sqlalchemy.org/en/rel_0_9/core/pooling.html
db_pool_size = 50
db_max_overflow = 100

persen_denda = 0

host = {
    'btn': {
        'id': 200,
        },
    'mitracomm': {
        'ids': [8, 14],  # Mandiri, BCA
        }
    }
