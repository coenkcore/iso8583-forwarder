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
from .db_tools import sppt2nop


class AvailableInvoice(object):
    def __init__(self, models, query, **kwargs):
        self.models = models
        self.query = query
        self.persen_denda = 'persen_denda' in kwargs and \
            kwargs['persen_denda'] or 0

    def add_option(self, pars):
        pars.add_option('', '--min', help='Tagihan minimum')
        pars.add_option('', '--max', help='Tagihan maksimum')
        pars.add_option('-t', '--tahun', help='Tahun pajak')

    def show(self, option):
        sample_count = int(option.sample_count)
        q = DBSession.query(self.models.Invoice).filter_by(
                status_pembayaran_sppt='0')
        if option.min:
            n = int(option.min)
            q = q.filter(self.models.Invoice.pbb_yg_harus_dibayar_sppt >= n)
        if option.max:
            n = int(option.max)
            q = q.filter(self.models.Invoice.pbb_yg_harus_dibayar_sppt <= n)
        if option.tahun:
            q = q.filter(self.models.Invoice.thn_pajak_sppt == option.tahun)
        offset = -1
        count = 0
        while True:
            if count >= sample_count:
                break
            offset += 1
            row = q.offset(offset).first()
            if not row:
                break
            calc = CalculateInvoice(
                    self.models, DBSession, self.persen_denda, row.kd_propinsi,
                    row.kd_dati2, row.kd_kecamatan, row.kd_kelurahan,
                    row.kd_blok, row.no_urut, row.kd_jns_op,
                    row.thn_pajak_sppt)
            if calc.total < 1:
                continue
            count += 1
            invoice_id_raw = sppt2nop(calc.invoice) + \
                calc.invoice.thn_pajak_sppt
            msg = '#{no}/{count} {id} Rp {total}'.format(
                    no=count, id=invoice_id_raw, total=calc.total,
                    count=sample_count)
            print(msg)
