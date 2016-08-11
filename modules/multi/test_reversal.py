from datetime import datetime
from test_payment import (
    DbTransaction,
    Payment,
    TestPayment,
    get_option,
    )


class Reversal(Payment):
    def reversal_request(self, pay_req_iso):
        self.copy(from_iso=pay_req_iso)
        self.set_reversal_request()


class TestReversal(TestPayment):
    def run(self):
        pay_resp_iso, pay_req_iso = TestPayment.run(self)
        if not pay_resp_iso.is_ok_response():
            return
        print('Bank kirim reversal request')
        req_iso = Reversal()
        req_iso.reversal_request(pay_req_iso)
        raw = self.get_raw(req_iso)
        print('Pemda terima reversal request')
        from_iso = DbTransaction()
        from_iso.setIsoContent(raw)
        print('Pemda kirim reversal response')
        resp_iso = DbTransaction(from_iso=from_iso, conf=self.conf)
        func = getattr(resp_iso, from_iso.get_func_name())
        func()
        self.get_raw(resp_iso)


def main(argv):
    option = get_option(argv)
    if not option:
        return
    module_name = option.module
    invoice_id = option.invoice_id
    conf = dict(name=option.bank, ip='127.0.0.1')
    test = TestReversal(module_name, invoice_id, conf)
    test.run()
