from sqlalchemy import create_engine
from tools import FixLength
from base_models import (
    Base,
    DBSession,
    )
from structure import INVOICE_ID
from models import Models
from query import (
    Query,
    CalculateInvoice,
    )
from conf import (
    db_url,
    db_schema,
    persen_denda,
    )


engine = create_engine(db_url)
Base.metadata.bind = engine
DBSession.configure(bind=engine)
models = Models(Base, db_schema)
query = Query(models, DBSession)


class AvailableInvoice(object):
    def __init__(self, sample_count=100, **kwargs):
        self.sample_count = sample_count
        self.persen_denda = 'persen_denda' in kwargs and \
            kwargs['persen_denda'] or 0

    def show(self):
        q = DBSession.query(models.Invoice).filter_by(status_pembayaran=0)
        q = q.order_by(models.Invoice.id.desc())
        offset = -1
        count = 0
        while True:
            if count >= self.sample_count:
                break
            offset += 1
            row = q.offset(offset).first()
            if not row:
                break
            invoice_id = FixLength(INVOICE_ID)
            invoice_id['Tahun'] = row.tahun
            invoice_id['Kode'] = row.kode
            invoice_id['SSPD No'] = row.no_sspd
            invoice_id_raw = invoice_id.get_raw()
            calc = CalculateInvoice(models, DBSession, invoice_id_raw,
                    self.persen_denda)
            if calc.total < 1:
                continue
            count += 1
            msg = '#{no}/{count} {id} Rp {total}'.format(no=count,
                    id=invoice_id_raw, total=calc.total,
                    count=self.sample_count)
            print(msg)
