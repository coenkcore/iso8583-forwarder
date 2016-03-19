import sys
sys.path[0:0] = ['/etc/opensipkd']
from forwarder import module_name
#sys.path[0:0] = ['/usr/share/opensipkd/modules']
#from base_models import (
#    Base,
#    DBSession,
#    CommonModel,
#    )
#from sqlalchemy import (
#    create_engine,
#    MetaData,
#    )
#sys.path[0:0] = ['/usr/share/opensipkd/modules']
#from fixtures import insert
#sys.path[0:0] = ['/usr/share/opensipkd-forwarder/modules']
#from iso8583_models import (
#    JenisLog,
#    Log,
#    LogValues,
#    )
#from iso8583_data import data


#########
# Utama #
#########
#if not db_url:
#    print('Sesuaikan db_url pada /etc/opensipkd/forwarder.py.')
#    print('Kemudian: dpkg-reconfigure opensipkd-forwarder')
#    print('')
#    sys.exit()
#engine = create_engine(db_url)
#metadata = MetaData(engine)
#Base.metadata.bind = engine
#Base.metadata.create_all()
#DBSession.configure(bind=engine)
#insert(engine, data)
if not module_name:
    print('Sesuaikan module_name pada /etc/opensipkd/forwarder.py')
    sys.exit()
# Siapa tahu autoload maka import models diletakkan sesudah bind
print('Module: %s' % module_name)
sys.path[0:0] = ['/usr/share/opensipkd-forwarder/modules']
try:
    module = __import__(module_name)
except ImportError, msg:
    print(msg)
    sys.exit()
module.setup()
