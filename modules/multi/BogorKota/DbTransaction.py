import os
from ..transaction import Transaction


def is_conf_exists(name):
    filename = os.path.join(
                os.getcwd(), 'modules', 'multi', 'BogorKota', name, 'conf.py')
    return os.path.exists(filename)

if is_conf_exists('pbb'):
    import pbb
if is_conf_exists('bphtb'):
    import bphtb
if is_conf_exists('padl'):
    import padl
if is_conf_exists('webr'):
    from .webr import (
        inquiry as webr_inquiry,
        payment as webr_payment,
        reversal as webr_reversal,
        )


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
    def bphtb_reversal_request_handler(self):
        try:
            bphtb.reversal(self)
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

    # Override
    def padl_reversal_request_handler(self):
        try:
            padl.reversal(self)
        except:
            self.ack_unknown()

    # Override
    def webr_inquiry_request_handler(self):
        try:
            webr_inquiry(self)
        except Exception:
            self.ack_unknown()

    # Override
    def webr_payment_request_handler(self):
        try:
            webr_payment(self)
        except Exception:
            self.ack_unknown()

    # Override
    def webr_reversal_request_handler(self):
        try:
            webr_reversal(self)
        except Exception:
            self.ack_unknown()
