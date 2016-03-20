class PadlReversal():
    # Override
    def reversal_response(self):
        self.invoice_id_raw = self.from_iso.get_invoice_id()
        self.invoice_id = decode_invoice_id_raw(self.invoice_id_raw)
        if not self.invoice_id.set_raw(self.invoice_id_raw):
            return self.ack_invalid_invoice_id()
        self.calc = CalculateInvoice(self.invoice_id['Tahun'],
                        self.invoice_id['SPT No'])
        if not self.calc.invoice:
            return self.ack_invoice_not_available()
        ntb = self.from_iso.get_ntb()
        q = PadlDBSession.query(IsoPayment).filter_by(
                invoice_id=self.calc.invoice.id, ntb=ntb) 
        iso_pay = q.first()
        if not iso_pay:
            return self.ack_invoice_not_available()
        q = PadlDBSession.query(IsoReversal).filter_by(id=iso_pay.id)
        iso_rev = q.first()
        if iso_rev:
            return self.ack_already_canceled()
        self.save_reversal(iso_pay)

    def save_reversal(self, iso_pay):
        q = PadlDBSession.query(Payment).filter_by(id=iso_pay.id)
        pay = q.first()
        if not pay:
            return self.ack_payment_not_found()
        iso_request = self.from_iso.raw.upper()
        iso_request = '0400' + iso_request[4:]
        pay.denda = pay.bunga = pay.jml_bayar = 0
        PadlDBSession.add(pay)
        self.calc.set_unpaid()
        iso_rev = IsoReversal()
        iso_rev.id = iso_pay.id
        iso_rev.iso_request = iso_request
        PadlDBSession.add(iso_rev)
        self.commit()

