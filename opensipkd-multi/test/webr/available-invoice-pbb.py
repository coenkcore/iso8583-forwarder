from optparse import OptionParser
from sqlalchemy import create_engine
import sys
sys.path[0:0] = ['/usr/share/opensipkd/modules']
from base_models import (
    DBSession,
    Base,
    )
sys.path[0:0] = ['/etc/opensipkd']
from multi_conf import (
    pbb_db_url as db_url, 
    )
engine = create_engine(db_url)
Base.metadata.bind = engine
DBSession.configure(bind=engine)
sys.path[0:0] = ['/usr/share/doc/opensipkd-multi/test/padl']
from available_invoice import AvailableInvoice


sample_count = 10
pars = OptionParser()
help_msg = 'default {count}'.format(count=sample_count)
pars.add_option('', '--sample-count', default=sample_count, help=help_msg)
pars.add_option('', '--jenis', help='Jenis pajak, contoh: reklame')
option, remain = pars.parse_args(sys.argv[1:])

sample_count = int(option.sample_count)

ai = AvailableInvoice(int(option.sample_count), option.jenis)
ai.show()
