import re
from multi.BogorKota.padl import (
    DBSession,
    models,
    InquiryResponse as BaseInquiryResponse,
    payment,
    reversal,
    )


class InquiryResponse(BaseInquiryResponse):
    def init_invoice_profile(self):
        self.invoice_profile = self.parent.invoice_profile
        self.invoice_profile['Jenis Pajak'] = \
            'PENDAPATAN ASLI DAERAH LAINNYA'

    def set_invoice_profile(self):
        invoice = self.calc.invoice
        op = self.calc.get_op()
        wp = self.calc.get_wp(op)
        q = DBSession.query(models.Pajak).filter_by(id=invoice.pajak_id)
        pajak = q.first()
        q = DBSession.query(models.Rekening).filter_by(id=pajak.rekening_id)
        rek = q.first()
        self.parent.invoice_profile.from_dict({
            'NPWPD': wp.npwpd,
            'Nama OP': wp.customernm,
            'Bulan': invoice.masadari.strftime('%m'),
            'Tahun': invoice.masadari.strftime('%Y'),
            'Tanggal Penetapan': invoice.terimatgl.strftime('%d-%m-%Y'),
            'Tanggal Jatuh Tempo': invoice.jatuhtempotgl.strftime('%d-%m-%Y'),
            'Jenis Pajak': ' '.join([re.sub('[^0-9]', '', rek.rekeningkd),
                rek.rekeningnm]),
            'Masa Pajak': ' s.d '.join([invoice.masadari.strftime('%d-%m-%Y'),
                invoice.masasd.strftime('%d-%m-%Y')]),
            'Tagihan Pokok': self.calc.tagihan,
            'Denda': self.calc.denda,
            })
        self.parent.set_invoice_profile()
 

def inquiry(parent):
    req = InquiryResponse(parent)
    req.response()
