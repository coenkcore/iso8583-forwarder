from ..transaction import Transaction
import pbb
import bphtb
import padl


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

    # Override
    def padl_inquiry_request_handler(self):
        try:
            padl.inquiry(self)
        except:
            self.ack_unknown()

    # Override
    def padl_payment_request_handler(self):
        try:
            padl.payment(self)
        except:
            self.ack_unknown()
