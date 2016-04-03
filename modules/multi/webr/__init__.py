import sys
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )
sys.path[0:0] = ['/usr/share/opensipkd/modules']
from base_models import Base
sys.path[0:0] = ['/etc/opensipkd']
from multi_conf import (
    webr_db_url,
    db_pool_size,
    db_max_overflow,
    )
    
WebrBase = declarative_base()
session_factory = sessionmaker()
WebrDBSession = scoped_session(session_factory)

engine_webr = create_engine(webr_db_url, pool_size=db_pool_size,
            max_overflow=db_max_overflow, echo=False)
WebrBase.metadata.bind = engine_webr
