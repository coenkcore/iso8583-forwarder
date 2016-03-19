import sys
sys.path[0:0] = ['/etc/opensipkd']
from bca_conf import module_names, db_url

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )

    
sys.path[0:0] = ['/usr/share/opensipkd/modules']
from base_models import Base, DBSession

sys.path[0:0] = ['/etc/opensipkd']
from bca_conf import (
    db_url,
    db_pool_size,
    db_max_overflow,
    )
    
engine = create_engine(db_url, pool_size=db_pool_size,
            max_overflow=db_max_overflow)
Base.metadata.bind = engine

#from DbTransaction import DbTransaction    
#for module_name in module_names:
#    print('Module: ' + module_name)
sys.path[0:0] = ['/usr/share/opensipkd-forwarder/modules/bca']
module_name = 'bca_db_transaction'
module = __import__(module_name)
DbTransaction = module.BcaDbTransaction
