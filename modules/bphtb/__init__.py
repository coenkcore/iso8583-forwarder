import sys
sys.path.insert(0, '/usr/share/opensipkd/modules')
from base_models import Base
sys.path.insert(0, '/etc/opensipkd')
from bphtb_conf import (
    db_url,
    db_pool_size,
    db_max_overflow,
    )
from sqlalchemy import create_engine


engine = create_engine(db_url, pool_size=db_pool_size,
            max_overflow=db_max_overflow)
Base.metadata.bind = engine
from DbTransaction import DbTransaction
