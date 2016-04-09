import os
import sys
import imp
from sqlalchemy import create_engine
sys.path[0:0] = ['/etc/opensipkd']
from multi_conf import db_url
sys.path[0:0] = ['/usr/share/opensipkd/modules']
from fixtures import insert
from base_models import Base
data_dir = os.path.split(__file__)[0]
data_file = os.path.join(data_dir, 'data.py')
data_module = imp.load_source('data', data_file)
data = data_module.data

print db_url
def init():
    if not db_url:
        print('Sesuaikan db_url pada /etc/opensipkd/multi_conf.py')
        return
    data_dir = os.path.split(__file__)[0]
    data_file = os.path.join(data_dir, 'data.py')
    data_module = imp.load_source('data', data_file)
    data = data_module.data
    engine = create_engine(db_url)
    Base.metadata.bind = engine
    sys.path[0:0] = ['/usr/share/opensipkd-forwarder/modules/multi']
    from log_models import (
        Payment,
        Reversal,
        )
    Base.metadata.create_all()
    #insert(engine, data)
init()
