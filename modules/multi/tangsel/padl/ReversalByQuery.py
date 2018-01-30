from multi.BogorKota.padl.ReversalByQuery import ReversalByQuery as BaseRBQ


class ReversalByQuery(BaseRBQ):
    def __init__(self, invoice_id_raw):
        short_id = invoice_id_raw[6:]
        BaseRBQ.__init__(self, short_id)
