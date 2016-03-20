import sys
sys.path[0:0] = ['/usr/share/opensipkd/modules']
from base_models import DBSession
from models import Payment
 

def query_pembayaran(payment_id):
    return DBSession.query(Payment).filter_by(id=payment_id)
