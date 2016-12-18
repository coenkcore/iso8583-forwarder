from sqlalchemy import create_engine
from tools import FixLength
from base_models import (
    Base,
    DBSession,
    )
from sismiop.query import Reversal
from common.pbb.models import Models
from common.pbb.structure import INVOICE_ID
from conf import (
    db_url,
    db_schema,
    )


engine = create_engine(db_url)
Base.metadata.bind = engine
DBSession.configure(bind=engine)
models = Models(Base, db_schema)


class ReversalByQuery(Reversal):
    def __init__(self, invoice_id_raw):
        self.invoice_id = FixLength(INVOICE_ID)
        self.invoice_id.set_raw(invoice_id_raw)
        Reversal.__init__(self, models, DBSession, self.invoice_id['Propinsi'],
            self.invoice_id['Kabupaten'], self.invoice_id['Kecamatan'],
            self.invoice_id['Kelurahan'], self.invoice_id['Blok'],
            self.invoice_id['Urut'], self.invoice_id['Jenis'],
            self.invoice_id['Tahun Pajak'])

    def set_unpaid(self):
        pay = Reversal.set_unpaid(self)
        if not pay:
            q = DBSession.query(self.models.Payment).filter_by(
                propinsi=self.invoice.kd_propinsi,
                kabupaten=self.invoice.kd_dati2,
                kecamatan=self.invoice.kd_kecamatan,
                kelurahan=self.invoice.kd_kelurahan,
                blok=self.invoice.kd_blok,
                urut=self.invoice.no_urut,
                jenis=self.invoice.kd_jns_op,
                tahun=self.invoice.thn_pajak_sppt)
            q.delete()
        DBSession.commit()
