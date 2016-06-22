from ..transaction import Transaction
import pbb
import bphtb


class DbTransaction(Transaction):
    # Override
    def pbb_inquiry_request_handler(self):
        try:
            pbb.inquiry(self)
        except:
            self.ack_unknown()

    # Override
    def pbb_payment_request_handler(self):
        try:
            pbb.payment(self)
        except:
            self.ack_unknown()

    # Override
    def bphtb_inquiry_request_handler(self):
        try:
            bphtb.inquiry(self)
        except:
            self.ack_unknown()

    # Override
    def bphtb_payment_request_handler(self):
        try:
            bphtb.payment(self)
        except:
            self.ack_unknown()
