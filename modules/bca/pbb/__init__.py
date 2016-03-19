import sys
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
#from datetime import datetime
# from sqlalchemy import (
    # create_engine,
    # MetaData,
    # Table,
    # select,
    # func,
    # Column,
    # Integer,
    # DateTime
    # )
from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )
# #from sqlalchemy.schema import CreateSchema
# from tools import (
    # extract_db_url,
    # eng_profile,
    # as_timezone,
    # create_now,
    # )

    
sys.path[0:0] = ['/usr/share/opensipkd/modules']
from base_models import Base
sys.path[0:0] = ['/etc/opensipkd']
from pbb_conf import (
    db_url,
    db_pool_size,
    db_max_overflow,
    )
    
PbbBase = declarative_base()
session_factory = sessionmaker()
PbbDBSession = scoped_session(session_factory)
print db_url
engine_pbb = create_engine(db_url, pool_size=db_pool_size,
            max_overflow=db_max_overflow)
PbbBase.metadata.bind = engine_pbb
from DbTransaction import DbTransaction
