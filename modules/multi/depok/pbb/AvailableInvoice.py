from sismiop.available_invoice import AvailableInvoice as SismiopAvailableInvoice
from . import (
    models,
    query,
    )
from .conf import persen_denda


class AvailableInvoice(SismiopAvailableInvoice):
    def __init__(self):
        SismiopAvailableInvoice.__init__(
            self, models, query, persen_denda=persen_denda)
