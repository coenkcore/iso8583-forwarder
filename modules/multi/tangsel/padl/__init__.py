from multi.BogorKota.padl import (
    Base,
    DBSession,
    db_schema,
    CalculateInvoice as BaseCalc,
    InquiryResponse as BaseInqResp,
    PaymentResponse as BasePayResp,
    ReversalResponse as BaseRevResp,
    BaseResponse,
    )
from .query import Reversal
from .models import IsoModels


iso_models = IsoModels(Base)


class CalculateInvoice(BaseCalc):
    def __init__(self, models, DBSession, invoice_id_raw, persen_denda):
        short_id = invoice_id_raw[6:]
        BaseCalc.__init__(
                self, models, iso_models, DBSession, short_id, persen_denda)


class InquiryResponse(BaseInqResp):
    def get_calc_cls(self):
        return CalculateInvoice

    def get_nama_wp(self, op, wp):
        return wp.customernm


class PaymentResponse(BasePayResp, InquiryResponse):
    # Overrides
    def get_iso_models(self):
        return iso_models

    # Overrides
    def before_save(self, pay):
        pay.enabled = 1

    # Override
    def create_iso_payment(self, pay):
        from_iso = self.parent.from_iso
        ntp = self.create_ntp()
        iso_pay = iso_models.IsoPayment()
        iso_pay.sspd_id = pay.id
        iso_pay.invoice_no = self.calc.invoice_id_raw
        iso_pay.iso_request = from_iso.raw
        iso_pay.transmission = from_iso.get_transmission()
        iso_pay.settlement = from_iso.get_settlement()
        iso_pay.stan = from_iso.get_stan()
        iso_pay.ntb = from_iso.get_ntb()
        iso_pay.ntp = ntp
        iso_pay.bank_id = self.parent.get_bank_id()
        iso_pay.channel_id = from_iso.get_channel()
        iso_pay.bank_ip = self.parent.get_bank_ip()
        DBSession.add(iso_pay)
        DBSession.flush()
        self.parent.set_ntp(ntp)


class ReversalResponse(BaseRevResp):
    def __init__(self, parent):
        BaseResponse.__init__(self, parent)
        short_id = self.invoice_id_raw[6:]
        self.rev = Reversal(self.models, self.iso_models, DBSession, short_id)

    def get_iso_models(self):
        return iso_models


def inquiry(parent):
    r = InquiryResponse(parent)
    r.response()


def payment(parent):
    r = PaymentResponse(parent)
    r.response()


def reversal(parent):
    r = ReversalResponse(parent)
    r.response()
