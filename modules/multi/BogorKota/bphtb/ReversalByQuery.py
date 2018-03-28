from sqlalchemy import create_engine
from base_models import (
    Base,
    DBSession,
    )
from models import Models
from query import Reversal
from .conf import (
    db_url,
    transaction_schema,
    area_schema,
    iso_schema,
    )


engine = create_engine(db_url)
Base.metadata.bind = engine
DBSession.configure(bind=engine)
models = Models(Base, transaction_schema, area_schema, iso_schema)


class ReversalByQuery(Reversal):
    def __init__(self, invoice_id_raw):
        Reversal.__init__(self, models, DBSession, invoice_id_raw)

    def set_unpaid(self):
        Reversal.set_unpaid(self)
        self.DBSession.commit()
