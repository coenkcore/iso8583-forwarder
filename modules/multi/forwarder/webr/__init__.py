import sys
from datetime import datetime
# from sqlalchemy import create_engine
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import (
#     scoped_session,
#     sessionmaker,
# )
from tools import FixLength
from ws_tools import send_rpc
from multi.webr.structure import INVOICE_PROFILE
# from .models import Models
# from .query import (
#     Query,
#     CalculateInvoice,
#     NTP,
#     Reversal,
# )
from .conf import (
    rpc_url,
    rpc_user,
    rpc_key,
    kd_pemda,
    kd_produk,
    host,
    persen_denda,
    pesan1,
    pesan2,
)

DEBUG = '--debug' in sys.argv


def print_debug(label, s):
    if DEBUG:
        print('*** DEBUG {l}: {s}'.format(l=label, s=s))


class BaseResponse(object):
    def __init__(self, parent):
        self.parent = parent
        self.invoice_id_raw = parent.from_iso.get_invoice_id()
        self.conf = host[self.parent.conf['name']]
        self.data = None
        self.invoice_profile = None

    def is_transaction_owner(self, iso_pay):
        conf = host[self.parent.conf['name']]
        return iso_pay.bank_id == conf['id']


class InquiryResponse(BaseResponse):
    def __init__(self, parent, method='inquiry'):
        BaseResponse.__init__(self, parent)
        self.parent = parent
        module_conf = host[self.parent.conf['name']]
        self.parent.conf.update(module_conf)
        self.conf = host[self.parent.conf['name']]
        data = self.get_data()
        self.invoice = send_rpc(rpc_user, rpc_key, rpc_url, method, data)

    def get_data(self):
        return dict(kd_bank=str(self.conf['id']).rjust(3,'0'),
                    kd_pemda=kd_pemda,
                    kd_channel=self.parent.from_iso.get_channel(),
                    invoice_no=self.invoice_id_raw,
                    kd_produk=kd_produk
                    )

    def init_invoice_profile(self):
        self.invoice_profile = FixLength(INVOICE_PROFILE)

    def set_invoice_profile(self):
        invoice = self.data
        # print(invoice)
        self.invoice_profile.from_dict({
            'Kode': invoice['invoice_no'],
            'Nama Penyetor': invoice['nm_wp'],
            'Alamat 1': invoice['jln_wp'],
            'Alamat 2': invoice['jln_wp_2'],
            'Tagihan': invoice['pokok'],
            'Denda': invoice['denda'],
            'Total': invoice['jumlah'],
            'Kode Rekening': 'kd_sub_produk' in invoice and
                             invoice['kd_sub_produk'] or '',
            'Nama Rekening': 'nm_sub_produk' in invoice and
                             invoice['nm_sub_produk'] or '',
            'Kode SKPD': 'kd_departemen' in invoice and
                         invoice['kd_departemen'] or '',
            'Nama SKPD': 'kd_departemen' in invoice and
                         invoice['nm_departemen'] or '000000',
            'Additional 1': pesan1,
            'Additional 2': pesan2, })
        self.set_invoice_profile_to_parent()
        print_debug('Invoice Profile', self.invoice_profile.to_dict())

    def is_valid(self, is_need_invoice_profile=True):
        if not self.invoice:
            is_need_invoice_profile and self.set_invoice_profile_to_parent()
            return self.parent.ack_not_available()

        if 'error' in self.invoice:
            error = int(self.invoice['error']['code'])
            if error == -52001:
                return self.parent.ack_not_available()
            elif error == -52002:
                return self.ack_already_paid()
            else:
                return self.parent.ack_other(self.invoice['error']['message'])

        self.data = self.invoice['result']['data']
        is_need_invoice_profile and self.set_invoice_profile()
        if self.data['jumlah'] <= 0:
            return self.parent.ack_already_paid_2(self.data['jumlah'])

        return True

    def response(self):
        self.init_invoice_profile()

        if not self.is_valid():
            return self.parent.set_amount(0)

        self.parent.set_amount(self.data['jumlah'])
        self.parent.ack()

    def set_invoice_profile_(self, key, value):
        if value:
            self.invoice_profile.from_dict({key: value})

    def set_invoice_profile_to_parent(self):
        self.parent.set_invoice_profile(self.invoice_profile.get_raw())

    def ack_already_paid(self):
        # pay = self.calc.get_payment()
        if 'result' in self.invoice:
            ntp = self.invoice['result']['ntp']
        else:
            ntp = ''

        self.parent.set_ntp(ntp)
        return self.parent.ack_already_paid()


def inquiry(parent):
    inq = InquiryResponse(parent)
    inq.response()


###########
# Payment #
###########
class PaymentResponse(InquiryResponse):
    def __init__(self, parent, method='payment'):
        InquiryResponse.__init__(self, parent, method)

    def get_data(self):
        tanggal = self.parent.from_iso.get_transaction_datetime()
        return dict(kd_bank=str(self.conf['id']).rjust(3, '0'),
                    kd_pemda=kd_pemda,
                    kd_channel=self.parent.from_iso.get_channel(),
                    invoice_no=self.invoice_id_raw,
                    kd_produk=kd_produk,
                    jumlah=self.parent.from_iso.get_amount(),
                    ntb=self.parent.from_iso.get_ntb(),
                    tgl_transaksi=tanggal.strftime('%Y-%m-%d'),
                    jam_transaksi=tanggal.strftime('%H:%M:%S'),
                    )

    def response(self):
        self.init_invoice_profile()
        if not self.is_valid():
            return
            
        self.parent.set_ntp(self.data['ntp'])
        self.parent.ack()


def payment(parent):
    pay = PaymentResponse(parent)
    pay.response()


############
# Reversal #
############
class ReversalResponse(PaymentResponse):
    def __init__(self, parent):
        method = 'reversal'
        PaymentResponse.__init__(self, parent, method)

    def response(self):
        self.init_invoice_profile()
        if not self.invoice:
            return self.parent.ack_payment_not_found()
        if 'error' in self.invoice:
            error = int(self.invoice['error']['code'])
            if error == -52001:
                return self.parent.ack_not_available()
            elif error == -52002:
                return self.ack_already_paid()
            elif error == -54001:
                return self.parent.ack_payment_not_found()
            elif error == -54002:
                return self.parent.ack_payment_owner()
            elif error == -54003:
                return self.parent.ack_invoice_open()
            else:
                return self.parent.ack_other(self.invoice['error']['message'])
        return self.parent.ack()


def reversal(parent):
    rev = ReversalResponse(parent)
    rev.response()