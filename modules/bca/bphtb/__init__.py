from sqlalchemy import create_engine
import sys
sys.path[0:0] = ['/usr/share/opensipkd/modules']
from base_models import Base
sys.path[0:0] = ['/etc/opensipkd']
from pbb_conf import (
    db_url,
    db_pool_size,
    db_max_overflow,
    )


engine_bphtb = create_engine(db_url, pool_size=db_pool_size,
            max_overflow=db_max_overflow)
BphtbBase.metadata.bind = engine
from DbTransaction import DbTransaction
