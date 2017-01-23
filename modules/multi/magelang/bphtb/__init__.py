from multi.BogorKota.bphtb import (
    InquiryResponse as BaseInquiryResponse,
    PaymentResponse as BasePaymentResponse,
    ReversalResponse as BaseReversalResponse,
    )
from structure import INVOICE_ID
from multi.BogorKota.bphtb import payment


class InquiryResponse(BaseInquiryResponse):
    def init_invoice_profile(self):
        self.parent.invoice_profile['Jenis Pajak'] = \
            'BEA PEROLEHAN HAK ATAS TANAH DAN BANGUNAN'

    def set_invoice_profile(self):
        invoice = self.calc.invoice
        self.parent.invoice_profile.from_dict({
            'NPWPD': self.calc.get_nop(),
            'Nama OP': invoice.wp_nama,
            'Bulan': invoice.tgl_transaksi.strftime('%m'),
            'Tahun': invoice.tgl_transaksi.strftime('%Y'),
            'Tanggal Penetapan': invoice.tgl_transaksi.strftime('%d-%m-%Y'),
            'Tanggal Jatuh Tempo': invoice.tgl_jatuh_tempo.strftime('%d-%m-%Y'),
            'Tagihan Pokok': self.calc.tagihan,
            'Denda': self.calc.denda})
        self.parent.set_invoice_profile()

    # Override
    def get_invoice_id_structure(self):
        return INVOICE_ID


def inquiry(parent):
    req = InquiryResponse(parent)
    req.response()


class PaymentResponse(BasePaymentResponse):
    # Override
    def get_invoice_id_structure(self):
        return INVOICE_ID

def payment(parent):
    req = PaymentResponse(parent)
    req.response()


class ReversalResponse(BaseReversalResponse):
    # Override
    def get_invoice_id_structure(self):
        return INVOICE_ID


def reversal(parent):
    req = ReversalResponse(parent)
    req.response()
