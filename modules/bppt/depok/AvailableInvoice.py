from sqlalchemy import create_engine
from tools import FixLength
from base_models import (
    Base,
    DBSession,
    )
from models import OtherModels
from query import CalculateInvoice
from conf import other_db_url


engine = create_engine(other_db_url)
Base.metadata.bind = engine
DBSession.configure(bind=engine)
models = OtherModels(Base)


class AvailableInvoice(object):
    def show(self, option):
        sample_count = int(option.sample_count)
        q = DBSession.query(models.Invoice).filter(models.Invoice.no_bayar != None)
        if option.min:
            n = int(option.min)
            q = q.filter(models.Invoice.nominal >= n)
        if option.max:
            n = int(option.max)
            q = q.filter(models.Invoice.nominal <= n)
        q = q.order_by(models.Invoice.nominal)
        offset = -1
        count = 0
        while True:
            if count >= sample_count:
                break
            offset += 1
            row = q.offset(offset).first()
            if not row:
                break
            calc = CalculateInvoice(models, DBSession, row.no_bayar)
            if calc.invoice and calc.paid:
                continue
            count += 1
            msg = '#{no}/{count} {id} Rp {total}'.format(no=count,
                    id=row.no_bayar, total=calc.tagihan, count=sample_count)
            print(msg)

    def add_option(self, pars):
        pars.add_option('', '--min', help='Tagihan minimum')
        pars.add_option('', '--max', help='Tagihan maksimum')
