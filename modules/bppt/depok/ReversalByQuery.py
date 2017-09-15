from sqlalchemy import create_engine
from base_models import (
    Base,
    DBSession,
    )
from models import OtherModels
from query import Reversal
from conf import other_db_url


engine = create_engine(other_db_url)
Base.metadata.bind = engine
DBSession.configure(bind=engine)
models = OtherModels(Base)


class ReversalByQuery(Reversal):
    def __init__(self, invoice_id_raw):
        Reversal.__init__(self, models, DBSession, invoice_id_raw)

    def set_unpaid(self):
        if self.payment:
            Reversal.set_unpaid(self)
            self.DBSession.commit()
