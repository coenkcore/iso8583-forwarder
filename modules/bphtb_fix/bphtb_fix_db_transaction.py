import traceback
from StringIO import StringIO
from random import randrange
from datetime import datetime
from ISO8583.ISO8583 import ISO8583
import sys
sys.path[0:0] = ['/usr/share/opensipkd/modules']
from base_models import DBSession
from tools import FixLength
sys.path[0:0] = ['/etc/opensipkd']
from bphtb_fix_conf import host
sys.path[0:0] = ['/usr/share/opensipkd-forwarder/modules/bphtb_fix']
from bphtb_fix_transaction import Transaction
from bphtb_fix_structure import (
    RC_NOT_AVAILABLE,
    RC_ALREADY_PAID,
    RC_INSUFFICIENT_FUND,
    RC_OTHER_ERROR,
    ERR_NOT_AVAILABLE,
    ERR_ALREADY_PAID,
    ERR_INSUFFICIENT_FUND,
    ERR_PAYMENT_NOT_FOUND,
    ERR_INVOICE_OPEN,
    INVOICE_PROFILE2,
    get_invoice_profile,
    )
from types import DictType


def luas(n, jumlah_nol=0):
    f = '%%.%df' % jumlah_nol
    s = f % n
    return s.replace('.', '')


class BaseDbTransaction(Transaction):
    def get_calc_cls(self):
        raise OverridePlease

    def get_invoice(self):
        bank_name = self.conf['name']
        self.conf.update(host[bank_name])
        akhiran_nol = self.get_jml_akhiran_nol()
        profile = get_invoice_profile(akhiran_nol)
        self.invoice_profile = FixLength(profile)
        self.invoice_profile2 = FixLength(INVOICE_PROFILE2)
        self.invoice_id_raw = self.from_iso.get_invoice_id()
        cls = self.get_calc_cls()
        self.calc = cls(self.invoice_id_raw)
        if self.calc.invoice:
            return self.calc.invoice
        return self.ack_not_available()

    def get_jml_akhiran_nol(self):
        return 'akhiran_nol_pada_luas' in self.conf and \
            self.conf['akhiran_nol_pada_luas'] or 0

    def luas(self, nilai):
        return luas(nilai, self.get_jml_akhiran_nol())

    def _set_invoice_profile(self):
        ok = self.set_invoice_profile()
        self.setBit(47, self.invoice_profile.get_raw())
        self.setBit(48, self.invoice_profile2.get_raw())
        self.setBit(61, self.calc.get_nop())
        return ok

    def set_ntp(self, ntp=''): # Nomor Transaksi Pemda
        self.setBit(57, ntp)

    def get_dates(self):
        return self.get_transaction_datetime(), \
               self.get_transmission_datetime(), \
               self.get_settlement_date()

    def save_inquiry(self):
        self.ack()

    def _inquiry_response(self):
        inv = self.get_invoice()
        if not inv:
            return
        self.setBit(4, self.calc.total)
        if self.calc.paid:
            return self.ack_already_paid()
        if not self._set_invoice_profile():
            return
        self.save_inquiry()

    def inquiry_response(self):
        try:
            self._inquiry_response()
        except:
            f = StringIO()
            traceback.print_exc(file=f)
            self.log_error(f.getvalue())
            f.close()
            self.ack_other('other error')

    ###########
    # Payment #
    ###########
    def _payment_response(self):
        self.copy([4, 58]) # belum di-copy oleh set_transaction_response()
        self.set_ntp()
        inv = self.get_invoice()
        if not inv:
            return
        if self.calc.paid:
            return self.ack_already_paid()
        total_bayar = self.get_amount()
        if total_bayar != self.calc.total:
            return self.ack_insufficient_fund(total_bayar)
        self.calc.set_paid()
        ntp = self.create_payment()
        self.commit()
        self.set_ntp(ntp)

    def payment_response(self):
        try:
            self._payment_response()
        except:
            f = StringIO()
            traceback.print_exc(file=f)
            self.log_error(f.getvalue())
            f.close()
            self.ack_other('other error')

    def create_payment_id(self):
        prefix = self.get_prefix_code()
        max_loop = 10
        loop = 0
        while True:
            acak = randrange(11111111, 99999999)
            acak = str(acak)
            trx_id = ''.join([prefix, acak])
            if not self.is_payment_id_found(trx_id):
                return trx_id
            loop += 1
            if loop == max_loop:
                raise Exception('*** Max loop for create payment ID. ' + \
                        'Call your programmer please.')

    def is_payment_id_found(self, trx_id):
        raise OverridePlease

    def create_payment(self):
        raise OverridePlease

    def get_real_value(self, value):
        if type(value) is not DictType:
            return value
        if self.from_iso.get_channel_id() in value:
            return value[self.channel_id]
        if 'default' in value:
            return value['default']
        return '00'

    def get_prefix_code(self):
        return ''

    ############
    # Reversal #
    ############
    def _reversal_response(self):
        transaction_datetime, transmission_datetime, settlement_date = \
            self.from_iso.get_dates()
        if not transaction_datetime or not transmission_datetime or \
           not settlement_date:
            return
        cls = self.get_reversal_cls()
        rev = cls(self.from_iso)
        if not rev.is_reversal_ready():
            return self.ack_invoice_open(self.from_iso.get_invoice_id())
        rev.set_unpaid()
        self.commit()

    def reversal_response(self):
        try:
            self._reversal_response()
        except:
            f = StringIO()
            traceback.print_exc(file=f)
            self.log_error(f.getvalue())
            f.close()
            self.ack_other('other error')

    def get_reversal_cls(self):
        raise OverridePlease

    ###################
    # Acknowledgement #
    ###################
    def ack_not_available(self):
        self.ack_not_available_2(self.invoice_id_raw)

    def ack_not_available_2(self, invoice_id):
        msg = ERR_NOT_AVAILABLE.format(invoice_id=invoice_id)
        self.ack(RC_NOT_AVAILABLE, msg)

    def ack_already_paid(self):
        ntp = self.calc.get_ntp()
        if ntp:
            self.set_ntp(ntp)
        msg = ERR_ALREADY_PAID.format(invoice_id=self.invoice_id_raw)
        self.ack(RC_ALREADY_PAID, msg)

    def ack_insufficient_fund(self, total_bayar):
        msg = ERR_INSUFFICIENT_FUND.format(invoice_id=self.invoice_id_raw,
                bayar=total_bayar,
                tagihan=self.calc.total)
        self.ack(RC_INSUFFICIENT_FUND, msg)

    def ack_payment_not_found(self):
        self.ack(RC_NOT_AVAILABLE, ERR_PAYMENT_NOT_FOUND)

    def ack_invoice_open(self, invoice_id):
        msg = ERR_INVOICE_OPEN.format(invoice_id=invoice_id)
        self.ack(RC_ALREADY_PAID, msg)

    def ack_other(self, msg):
        self.ack(RC_OTHER_ERROR, msg)

    def commit(self):
        DBSession.flush()
        DBSession.commit()
        self.ack()

############
# Reversal #
############
class BaseIsoReversal(object):
    def __init__(self, from_iso):
        self.from_iso = from_iso
        self.reversal_iso_request = ISO8583.getRawIso(from_iso).upper()
