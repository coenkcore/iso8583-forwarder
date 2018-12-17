localization = 'id_ID.UTF-8'

module_name = 'SukabumiKota'

db_url = 'postgresql://h2h:FIXME@localhost:5432/h2h'
db_schema = None

# Tuning
# http://docs.sqlalchemy.org/en/rel_0_9/core/pooling.html
db_pool_size = 50
db_max_overflow = 100
    
bphtb = dict(
    db_url = 'mysql://bjb:FIXME@192.168.1.19:3307/bphtb_db', 
    db_schema = None,
    number_of_ext = 3,
    kd_tp = {
        'default': 1,
        '6010': 2,
        }
    )
