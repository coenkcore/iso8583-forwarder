from datetime import date
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
    def add_option(self, pars):
        help_jenis = 'Jenis pajak, contoh: reklame'
        pars.add_option('-j', '--jenis', help=help_jenis)
        pars.add_option('', '--berdenda', action='store_true')
        pars.add_option('', '--tanpa-denda', action='store_true')

    def show(self, option):
        sample_count = int(option.sample_count)
        q = DBSession.query(models.Invoice.tahun, models.Invoice.sptno,
                models.Rekening.rekeningnm, models.Rekening.rekeningkd)
        q = q.filter(models.Invoice.pajak_id == models.Pajak.id)
        q = q.filter(models.Pajak.rekening_id == models.Rekening.id)
        q = q.filter(models.Invoice.status_pembayaran == 0)
        if option.jenis:
            pola = '%{nama}%'.format(nama=option.jenis)
            q = q.filter(models.Rekening.rekeningnm.ilike(pola))
        if option.berdenda:
            q = q.filter(models.Invoice.jatuhtempotgl < date.today())
        elif option.tanpa_denda:
            q = q.filter(models.Invoice.jatuhtempotgl >= date.today())
        q = q.order_by(models.Invoice.tahun.desc(), models.Invoice.sptno.desc())
        offset = -1
        count = 0
        while True:
            if count >= sample_count:
                break
            offset += 1
            row = q.offset(offset).first()
            if not row:
                break
            invoice_id = FixLength(INVOICE_ID)
            invoice_id['Tahun'] = row.tahun
            invoice_id['SPT No'] = row.sptno
            invoice_id_raw = invoice_id.get_raw()
            calc = CalculateInvoice(models, DBSession, invoice_id_raw,
                    persen_denda)
            if calc.total < 1:
                continue
            count += 1
            if calc.invoice.jatuhtempotgl:
                jatuh_tempo = calc.invoice.jatuhtempotgl.strftime('%d-%m-%Y')
            else:
                jatuh_tempo = 'tidak ada'
            msg = '#{no}/{count} {id} {nama_rek} {kode_rek} Rp {tagihan} + '\
                  'Rp {denda} = Rp {total}, jatuh tempo {jatuh_tempo}'
            msg = msg.format(no=count, id=invoice_id_raw, nama_rek=row.rekeningnm,
                    kode_rek=row.rekeningkd, tagihan=calc.tagihan,
                    denda=calc.denda, total=calc.total, count=sample_count,
                    jatuh_tempo=jatuh_tempo)
            print(msg)
