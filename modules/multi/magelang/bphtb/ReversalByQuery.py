from multi.BogorKota.bphtb.ReversalByQuery import ReversalByQuery \
        as BaseReversal
from structure import INVOICE_ID


class ReversalByQuery(BaseReversal):
    def get_invoice_id_structure(self):
        return INVOICE_ID
