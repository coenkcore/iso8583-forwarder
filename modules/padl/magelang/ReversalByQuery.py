from tools import FixLength
from .structure import INVOICE_ID
from .query import InvoiceQuery


class ReversalByQuery(InvoiceQuery):
    def __init__(self, invoice_id):
        self.invoice_id = FixLength(INVOICE_ID)
        self.invoice_id.set_raw(invoice_id)
        InvoiceQuery.__init__(
            self, self.invoice_id['Tahun'], self.invoice_id['SPT No'])
        self.payment = self.invoice and self.get_payment()

    def set_unpaid(self):
        InvoiceQuery.set_unpaid(self)
        self.DBSession.commit()
