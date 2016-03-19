iso8583_listen_address = ('0.0.0.0', 8586)

# Nama modul sesuai file atau direktori yang berada di
# /usr/share/opensipkd-forwarder/modules.
module_name = 'bca'
db_url      = 'postgresql://aagusti:a@localhost/forwarder'
host = {
    'bjb': {
        'ip': '10.31.224.133', # devel
        #'ip': '10.31.224.200', # production 
        'port': 10002,
        'timeout': 60, # seconds
        'active':False,
        },
    'bjb_with_suffix': { # Pakai akhiran hexa 03
        'ip': '10.31.224.133', # devel
        #'ip': '10.31.224.200', # production 
        'port': 10002,
        'timeout': 60, # seconds
        'active':False,
        },
    'bri': {
        'ip': '172.21.49.32',
        'timeout': 200,
        'active':False,
                
        },
    'btn': {
        'ip': '172.18.3.42', # devel
        #'ip': '10.255.0.83', # production 
        'timeout': 200,
        'need echo': False,
        'active':False,
                
        },
    'bca': {
        'ip': '202.169.43.53',
        'timeout': 200,
        'need echo': False,
        'active':False,
                
        },
    'pos': {
        'ip': '202.159.90.190',
        'timeout': 200,
        'need echo': False,
        'active':False,
        },
    'bank_kaltim': {
        'ip': '85.25.217.213',
        'timeout': 200,
        'need echo': False,
        'active':False,
        },
    'local': {
        'ip': '192.168.56.1',
        'timeout': 200,
        'need echo': False,
        },

    }
