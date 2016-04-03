import sys
from sqlalchemy import create_engine
from datetime import datetime
from time import sleep
from common import Test
sys.path[0:0] = ['/usr/share/opensipkd-forwarder/modules/bca']
from bca_structure import INQUIRY_CODE
sys.path[0:0] = ['/etc/opensipkd']
from bca_conf import (
    #module_name,
    db_url,
    )
sys.path[0:0] = ['/usr/share/opensipkd/modules']
from base_models import Base
engine = create_engine(db_url)
Base.metadata.bind = engine
sys.path[0:0] = ['/usr/share/opensipkd-forwarder/modules/bca/']
from log_models import Payment,Reversal

Base.metadata.create_all()
