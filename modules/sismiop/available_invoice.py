from sqlalchemy import create_engine
from base_models import (
    Base,
    DBSession,
    )
from models import Models
from query import (
    Query,
    CalculateInvoice,
    )
from tools import sppt2nop


class AvailableInvoice(object):
    def __init__(self, db_url, db_schema, sample_count=100, **kwargs):
        self.engine = create_engine(db_url)
        Base.metadata.bind = self.engine
        DBSession.configure(bind=self.engine)
        self.models = Models(Base, db_schema)
        self.query = Query(self.models, DBSession)
        self.sample_count = sample_count
        self.persen_denda = 'persen_denda' in kwargs and \
            kwargs['persen_denda'] or 0

    def show(self):
        q = DBSession.query(self.models.Invoice).filter_by(
                status_pembayaran_sppt = '0')
        q = q.filter(self.models.Invoice.pbb_yg_harus_dibayar_sppt >= 100,
                     self.models.Invoice.pbb_yg_harus_dibayar_sppt < 1000)
        q = q.order_by(self.models.Invoice.thn_pajak_sppt.desc(),
                       self.models.Invoice.pbb_yg_harus_dibayar_sppt)
        offset = -1
        count = 0
        while True:
            if count >= self.sample_count:
                break
            offset += 1
            row = q.offset(offset).first()
            if not row:
                break
            calc = CalculateInvoice(self.models, DBSession, self.persen_denda,
                    row.kd_propinsi, row.kd_dati2, row.kd_kecamatan,
                    row.kd_kelurahan, row.kd_blok, row.no_urut, row.kd_jns_op,
                    row.thn_pajak_sppt)
            if calc.total < 1:
                continue
            count += 1
            invoice_id_raw = sppt2nop(calc.invoice) + calc.invoice.thn_pajak_sppt 
            msg = '#{no}/{count} {id} Rp {total}'.format(no=count,
                    id=invoice_id_raw, total=calc.total,
                    count=self.sample_count)
            print(msg)
