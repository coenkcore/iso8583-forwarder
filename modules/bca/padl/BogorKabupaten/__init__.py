from sqlalchemy import create_engine
import sys
sys.path[0:0] = ['/usr/share/opensipkd/modules']
from base_models import Base
sys.path[0:0] = ['/etc/opensipkd']
from padl_fix_conf import db_url


engine = create_engine(db_url)
Base.metadata.bind = engine
from DbTransaction import DbTransaction
