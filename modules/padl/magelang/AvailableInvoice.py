from time import time
from sqlalchemy import (
    exists,
    and_,
    )
from tools import FixLength
from .models import (
    Invoice,
    Payment,
    Rekening,
    Pajak,
    )
from .query import (
    session_factory,
    CalculateInvoice,
    )


class AvailableInvoice:
    def show(self, option):
        sample_count = int(option.sample_count)
        session = session_factory()
        q = session.query(Invoice.sptno, Invoice.tahun,
                Rekening.rekeningkd, Rekening.rekeningnm).\
                filter(Invoice.pajak_id == Pajak.id).\
                filter(Pajak.rekening_id == Rekening.id)
        q = q.filter(~exists().where(and_(Invoice.id == Payment.spt_id,
                Payment.enabled != 1)))
        if option.jenis:
            pola = '%{}%'.format(option.jenis)
            q = q.filter(Rekening.rekeningnm.ilike(pola))
        q = q.order_by(Invoice.tahun.desc(), Invoice.sptno.desc())
        invoice_id_tpl = '71{tahun}{sptno}'
        count = 0
        awal = time()
        max_seconds = 15
        max_msg = 'Sudah lebih dari {} detik, akhiri saja.'.format(max_seconds)
        while True:
            if time() - awal > max_seconds:
                print(max_msg)
                break
            if count >= sample_count:
                break
            qry = q.offset(count)
            row = qry.first()
            if not row:
                break
            count += 1
            calc = CalculateInvoice(row.tahun, row.sptno)
            if calc.is_paid():
                continue
            sptno = str(row.sptno).zfill(6)
            invoice_id_raw = invoice_id_tpl.format(tahun=row.tahun, sptno=sptno)
            msg = '#{no}/{count} {id} {nama_rek} {kode_rek} Rp {total}'.format(
                    no=count, id=invoice_id_raw, nama_rek=row.rekeningnm,
                    kode_rek=row.rekeningkd,
                    total=calc.total, count=sample_count)
            print(msg)
