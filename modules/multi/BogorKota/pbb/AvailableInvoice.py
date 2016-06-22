from sismiop.available_invoice import AvailableInvoice as SismiopAvailableInvoice
from conf import (
    db_url,
    db_schema,
    persen_denda,
    )


class AvailableInvoice(SismiopAvailableInvoice):
    def __init__(self, sample_count):
        SismiopAvailableInvoice.__init__(self, db_url, db_schema, sample_count,
            persen_denda=persen_denda)
