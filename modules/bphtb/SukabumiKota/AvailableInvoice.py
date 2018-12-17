from tools import FixLength
from .models import Invoice
from .query import (
    session_factory,
    CalculateInvoice,
    )


class AvailableInvoice:
    def show(self, option):
        sample_count = int(option.sample_count)
        session = session_factory()
        q = session.query(Invoice).filter_by(status_pembayaran=0)
        q = q.order_by(Invoice.bphtb_hrs_bayar)
        offset = -1
        count = 0
        while True:
            if count >= sample_count:
                break
            offset += 1
            row = q.offset(offset).first()
            if not row:
                break
            invoice_id = row.no_tagihan
            calc = CalculateInvoice(invoice_id)
            if calc.total < 1:
                continue
            count += 1
            msg = '#{no}/{count} {id} {nop} Rp {total}'.format(
                    no=count, id=invoice_id, total=calc.total, nop=row.nop,
                    count=sample_count)
            print(msg)
