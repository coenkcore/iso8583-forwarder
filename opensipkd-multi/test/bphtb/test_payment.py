from datetime import datetime
from test_inquiry import (
    Inquiry,
    InquiryTest,
    BcaDbTransaction,
    )
from bca_structure import (
    PAYMENT_CODE,
    RC_OK,
    )


class Payment(Inquiry):
    def payment_request(self, invoice_id, inq_resp_iso):
        self.inquiry_request(invoice_id)
        self.setBit(3, PAYMENT_CODE[1])
        jml_bayar = inq_resp_iso.getBit(4)
        self.setBit(4, jml_bayar)
        ntb = datetime.now().strftime('%Y%m%d%H%M%S')
        self.setBit(48, ntb)
        self.copy([62], inq_resp_iso)


class PaymentTest(InquiryTest):
    def request(self):
        resp_iso = InquiryTest.request(self)
        if resp_iso.getBit(39) != RC_OK:
            return resp_iso, None
        print('Bank kirim payment request')
        amount = resp_iso.getBit(4)
        req_iso = Payment()
        req_iso.payment_request(self.invoice_id, resp_iso)
        raw = self.get_raw(req_iso)
        print('Pemda terima payment request')
        from_iso = BcaDbTransaction()
        from_iso.setIsoContent(raw)
        print('Pemda kirim payment response')
        resp_iso = BcaDbTransaction(from_iso=from_iso, conf=self.conf)
        func = getattr(resp_iso, from_iso.get_func_name())
        func()
        self.get_raw(resp_iso)
        return resp_iso, req_iso # Buat test_reversal



if __name__ == '__main__':
    import sys
    from pprint import pprint
    from optparse import OptionParser

    invoice_id = '3278009008003035002006'
    streamer_name = 'bjb_with_suffix'

    pars = OptionParser()
    pars.add_option('-i', '--invoice-id', default=invoice_id,
            help='Invoice ID, default: ' + invoice_id)
    pars.add_option('', '--streamer-name', default=streamer_name,
        help='Nama modul streamer, digunakan saat --raw, default: %s' % streamer_name)
    option, remain = pars.parse_args(sys.argv[1:])

    streamer_name = option.streamer_name
    conf = {'ip': '127.0.0.1',
            'name': streamer_name}
    test = PaymentTest(option.invoice_id, conf)
    test.request()
