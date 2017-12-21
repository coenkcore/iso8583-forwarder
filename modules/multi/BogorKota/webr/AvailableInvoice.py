from time import time
from datetime import date
from sqlalchemy import create_engine
from base_models import (
    Base,
    DBSession,
    )
from multi.BogorKota.webr.models import Models
from .query import (
    Query,
    CalculateInvoice,
    )
from .conf import (
    db_url,
    db_schema,
    persen_denda,
    )


engine = create_engine(db_url)
Base.metadata.bind = engine
DBSession.configure(bind=engine)
models = Models(Base, db_schema)
query = Query(models, DBSession)


TIMEOUT = 10 # detik

class AvailableInvoice(object):
    def show(self, option):
        sample_count = int(option.sample_count)
        q = DBSession.query(models.Invoice).filter(models.Invoice.status == 0)
        q = q.order_by(models.Invoice.id)
        offset = -1
        count = 0
        awal = time()
        while True:
            if time() - awal > TIMEOUT:
                break
            if count >= sample_count:
                break
            offset += 1
            row = q.offset(offset).first()
            if not row:
                break
            calc = CalculateInvoice(models, DBSession, row.kode, persen_denda)
            if calc.total < 1:
                continue
            count += 1
            if calc.invoice.jatuh_tempo:
                jatuh_tempo = calc.invoice.jatuh_tempo.strftime('%d-%m-%Y')
            else:
                jatuh_tempo = 'tidak ada'
            msg = '#{no}/{count} {id} Rp {tagihan} + '\
                  'Rp {denda} = Rp {total}, jatuh tempo {jatuh_tempo}'
            msg = msg.format(no=count, id=row.kode, tagihan=calc.tagihan,
                    denda=calc.denda, total=calc.total, count=sample_count,
                    jatuh_tempo=jatuh_tempo)
            print(msg)
