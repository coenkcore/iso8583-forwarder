from sismiop.query import Query
from sismiop.available_invoice import \
        AvailableInvoice as SismiopAvailableInvoice
from .DbTransaction import (
    DBSession,
    models,
    )
from .conf import persen_denda


class AvailableInvoice(SismiopAvailableInvoice):
    def __init__(self):
        query = Query(models, DBSession)
        SismiopAvailableInvoice.__init__(
                self, models, query, persen_denda=persen_denda)
