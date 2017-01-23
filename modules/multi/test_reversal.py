from datetime import datetime
from test_payment import (
    DbTransaction,
    TestPayment,
    )


def reversal_request(iso, pay_req_iso):
    iso.copy(from_iso=pay_req_iso)
    iso.set_reversal_request()


class TestReversal(TestPayment):
    def run(self):
        pay_resp_iso, pay_req_iso = TestPayment.run(self)
        if not pay_resp_iso.is_ok_response():
            return
        print('Bank kirim reversal request')
        req_iso = DbTransaction()
        reversal_request(req_iso, pay_req_iso)
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
    test = TestReversal(argv)
    test.run()
