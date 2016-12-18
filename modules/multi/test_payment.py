from datetime import datetime
from structure import (
    PBB_PAYMENT_CODE,
    BPHTB_PAYMENT_CODE,
    PADL_PAYMENT_CODE,
    )
from test_inquiry import (
    Inquiry,
    DbTransaction,
    TestInquiry,
    )


PAYMENT_CODES = dict(
    pbb=PBB_PAYMENT_CODE,
    bphtb=BPHTB_PAYMENT_CODE,
    padl=PADL_PAYMENT_CODE)


class Payment(Inquiry):
    def payment_request(self, module_name, inq_resp_iso, bank_id):
        payment_code = PAYMENT_CODES[module_name]
        self.inquiry_request(module_name, inq_resp_iso.get_invoice_id(),
            bank_id)
        self.set_transaction_code(payment_code)
        self.set_amount(inq_resp_iso.get_amount())
        ntb = datetime.now().strftime('%Y%m%d%H%M%S')
        self.set_ntb(ntb)
        self.copy([62], inq_resp_iso)


class TestPayment(TestInquiry):
    def run(self):
        resp_iso = TestInquiry.run(self)
        if not resp_iso.is_ok_response():
            return resp_iso, None
        print('Bank kirim payment request')
        req_iso = Payment()
        req_iso.payment_request(self.module_name, resp_iso, self.conf['bank_id'])
        raw = self.get_raw(req_iso)
        print('Pemda terima payment request')
        from_iso = DbTransaction()
        from_iso.setIsoContent(raw)
        print('Pemda kirim payment response')
        resp_iso = DbTransaction(from_iso=from_iso, conf=self.conf)
        func = getattr(resp_iso, from_iso.get_func_name())
        func()
        self.get_raw(resp_iso)
        return resp_iso, req_iso # Untuk test_reversal.py


def main(argv):
    test = TestPayment(argv)
    test.run()
