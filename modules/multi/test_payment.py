from datetime import datetime
from structure import (
    PBB_PAYMENT_CODE,
    BPHTB_PAYMENT_CODE,
    PADL_PAYMENT_CODE,
    WEBR_PAYMENT_CODE,
    )
from test_inquiry import (
    DbTransaction,
    TestInquiry,
    test_not_found,
    area_module,
    )


PAYMENT_CODES = dict(
    pbb=PBB_PAYMENT_CODE,
    bphtb=BPHTB_PAYMENT_CODE,
    padl=PADL_PAYMENT_CODE,
    webr=WEBR_PAYMENT_CODE)


def default_payment_request(iso, module_name, inq_resp_iso, bank_id):
    payment_code = PAYMENT_CODES[module_name]
    iso.set_transaction_code(payment_code)
    iso.set_amount(inq_resp_iso.get_amount())
    ntb = datetime.now().strftime('%Y%m%d%H%M%S')
    iso.set_ntb(ntb)
    iso.copy([4, 12, 13, 15, 18, 37, 47, 49, 59, 60, 61, 62, 63, 102, 107],
        inq_resp_iso)


if test_not_found:
    payment_request = default_payment_request
else:
    payment_request = area_module.test.payment_request


class TestPayment(TestInquiry):
    def run(self):
        resp_iso = TestInquiry.run(self)
        if not resp_iso.is_ok_response():
            return resp_iso, None
        print('Bank kirim payment request')
        req_iso = DbTransaction()
        req_iso.set_transaction_request()
        payment_request(req_iso, self.module_name, resp_iso, self.conf['bank_id'])
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
