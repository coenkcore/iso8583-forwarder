from multi.tangsel.conf import (
    kode_pemda,
    kode_padl,
    )
from multi.BogorKota.padl.AvailableInvoice import AvailableInvoice as BaseAvl


class AvailableInvoice(BaseAvl):
    def on_print(self, option, count, invoice_id_raw, row, calc):
        invoice_id_raw = kode_pemda + kode_padl + invoice_id_raw
        BaseAvl.on_print(self, option, count, invoice_id_raw, row, calc)
