from sqlalchemy import create_engine
from base_models import (
    Base,
    DBSession,
    )
from tools import FixLength
from models import Models
from query import Reversal
from structure import INVOICE_ID
from conf import (
    db_url,
    transaction_schema,
    area_schema,
    )


engine = create_engine(db_url)
Base.metadata.bind = engine
DBSession.configure(bind=engine)
models = Models(Base, transaction_schema, area_schema)


class ReversalByQuery(Reversal):
    def __init__(self, invoice_id_raw):
        invoice_id = FixLength(self.get_invoice_id_structure())
        invoice_id.set_raw(invoice_id_raw)
        Reversal.__init__(self, models, DBSession, invoice_id)

    def set_unpaid(self):
        Reversal.set_unpaid(self)
        self.DBSession.commit()

    def get_invoice_id_structure(self):
        return INVOICE_ID
