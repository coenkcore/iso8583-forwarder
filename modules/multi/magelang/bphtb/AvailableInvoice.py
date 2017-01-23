from multi.BogorKota.bphtb.AvailableInvoice import AvailableInvoice \
        as BaseAvailableInvoice
from structure import INVOICE_ID


class AvailableInvoice(BaseAvailableInvoice):
    # Override
    def get_invoice_id_structure(self):
        return INVOICE_ID
