import sys
sys.path[0:0] = ['/usr/share/opensipkd/modules']
from tools import FixLength
from base_models import (
    Base,
    DBSession,
    )
sys.path[0:0] = ['/etc/opensipkd']
from pbb_conf import module_name
sys.path[0:0] = ['/usr/share/opensipkd-forwarder/modules/pbb']
from pbb_structure import INVOICE_ID
module = __import__(module_name)
engine = module.engine
Base.metadata.bind = engine
sys.path[0:0] = ['/usr/share/opensipkd-forwarder/modules/pbb/' + module_name]
from CalculateInvoice import query_sppt
from DbTransaction import query_pembayaran
from PaymentReversal import ReversalByQuery 


print('Database ke {host}'.format(host=engine.url.host))

invoice_id_raw = sys.argv[1:] and sys.argv[1] or '3278003011017029502012'
print('Mencoba membatalkan Invoice ID {invoice_id} ...'.format(
    invoice_id=invoice_id_raw))

invoice_id = FixLength(INVOICE_ID)
invoice_id.set_raw(invoice_id_raw)
rbq = ReversalByQuery(invoice_id)
if not rbq.invoice:
    print('SPPT tidak ada.')
    sys.exit()
if not rbq.is_paid():
    print('Statusnya memang belum dibayar, tidak perlu dilanjutkan.')
    sys.exit()
if not rbq.bayar:    
    print('Belum ada pembayaran.')
    sys.exit()
rbq.set_unpaid()
DBSession.add(rbq.invoice)
DBSession.add(rbq.bayar)
DBSession.flush()
DBSession.commit()
print('Berhasil dibatalkan.')
