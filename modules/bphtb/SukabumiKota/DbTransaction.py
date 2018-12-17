from bphtb.transaction import Transaction
from bphtb.query import (
    Log,
    Reversal as IsoReversal,
    )
from .query import (
    CalculateInvoice,
    Reversal,
    )


class DbTransaction(Transaction):
    def set_invoice_profile(self):  # Override
        inv = self.calc.invoice
        self.invoice_profile.from_dict({
            'Luas Tanah': inv.luas_tanah,
            'Luas Bangunan': inv.luas_bangunan,
            'NPOP': inv.npop,
            'Jenis Perolehan Hak': inv.jns_perolehan_hak,
            'Nama Notaris': inv.nama_notaris,
            'Nama Wajib Pajak': inv.nama_wp,
            'NPWP': inv.npwp_wp,
            'Alamat WP': inv.alamat_wp,
            'Alamat OP': inv.alamat_op,
            'Kota OP': 'Sukabumi',
            'Kelurahan WP': inv.kelurahan_wp,
            'Kecamatan WP': inv.kecamatan_wp,
            'Jumlah Bayar': self.calc.total,
            'Jumlah Denda': self.calc.denda})
        self.invoice_profile2.from_dict({
            'RT WP': inv.rt_wp,
            'RW WP': inv.rw_wp, 
            'Kode Pos WP': inv.kode_pos_wp.strip(),
            'Kelurahan OP': inv.kelurahan_op,
            'Kecamatan OP': inv.kecamatan_op,
            'Tahun Pajak': inv.tahun_pajak,
            })
        Transaction.set_invoice_profile(self)

    def inquiry(self):
        invoice_id = self.get_invoice_id()
        self.calc = CalculateInvoice(invoice_id)
        if not self.calc.invoice:
            return self.ack_not_available()
        self.set_amount(self.calc.total)
        self.set_invoice_profile()
        if self.calc.is_paid():
            return self.ack_already_paid()
        return True
 
    def create_log(self):
        log = Log(self.conf['name'], self.get_bank_ip())
        log.save_request(self.from_iso)
        return log

    def inquiry_request_handler(self):
        log = self.create_log()
        if self.inquiry():
            self.ack()
        log.save_response(self)

    def payment_request_handler(self):
        payment_id = None
        log = self.create_log()
        if self.inquiry():
            if self.from_iso.get_amount() == self.calc.total:
                tgl = self.from_iso.get_transaction_datetime()
                pay = self.calc.set_paid(tgl_bayar=tgl.date())
                payment_id = pay.id
                self.ack()
            else:
                self.ack_insufficient_fund(self.calc.total)
        log.save_payment_response(self, payment_id)

    def reversal(self):
        invoice_id = self.from_iso.get_invoice_id()
        rev = Reversal(invoice_id)
        if not rev.invoice:
            return self.ack_not_available()
        if not rev.is_paid():
            return self.ack_invoice_open()
        ntb = self.from_iso.get_ntb()
        amount = self.from_iso.get_amount()
        iso_rev = IsoReversal(invoice_id, amount, ntb)
        if iso_rev.payment:
            return rev
        return self.ack_iso_payment_not_found()
 
    def reversal_request_handler(self):
        log = self.create_log()
        rev = self.reversal()
        if rev:
            amount = self.from_iso.get_amount()
            rev.set_unpaid(amount)
            self.ack()
        log.save_response(self)
