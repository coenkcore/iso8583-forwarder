import os
from ..transaction import Transaction
import pbb


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
    def pbb_reversal_request_handler(self):
        try:
            pbb.reversal(self)
        except:
            self.ack_unknown()
