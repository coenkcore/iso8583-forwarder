from padl.structure import (
    INQUIRY_CODE,
    PAYMENT_CODE,
    )
from .DbTransaction import (
    models,
    session_factory,
    other_session_factory,
    )
from .other_query import Query 
from .conf import (
    db_url,
    other_db_url,
    )


class ReversalByQuery(object):
    def __init__(self, invoice_id):
        self.invoice_id = invoice_id
        IsoLog = models.IsoLog
        DBSession = session_factory()
        q_base = DBSession.query(IsoLog).filter_by(
                mti='0210', bit061=invoice_id).order_by(IsoLog.id.desc())
        q = q_base.filter_by(bit003=INQUIRY_CODE, bit039='00')
        self.invoice = q.first()
        q = q_base.filter_by(bit003=PAYMENT_CODE).filter(IsoLog.bit047 != None)
        self.payment = q.first()
        if not self.payment:
            return
        self.bank_id = self.payment.bit033.lstrip('0')
        self.OtherDBSession = other_session_factory()
        self.query = Query(self.OtherDBSession, self.bank_id)

    def is_paid(self):
        return self.payment

    def set_unpaid(self):
        ntp = self.payment.bit047
        return self.query.reversal(ntp)
