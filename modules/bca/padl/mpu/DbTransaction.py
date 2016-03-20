import traceback
from StringIO import StringIO
from datetime import datetime
from random import randrange
from padl_fix_structure import INVOICE_PROFILE
from padl_fix_transaction import Transaction
from CalculateInvoice import CalculateInvoice
import sys
sys.path.insert(0, '/usr/share/opensipkd/modules')
from tools import FixLength
from base_models import (
    Base,
    DBSession,
    )
from models import (
    IsoPayment,
    IsoReversal,
    Payment,
    PaymentDetail,
    Invoice,
    )


KET_DENDA = '{bln} bulan x {persen} % x {tagihan}'

ERR_NTP = Exception('*** Max loop for create payment ID. Call your '\
                    'programmer please.')

def get_ntp(prefix):
    max_loop = 10
    loop = 0
    while True:
        acak = randrange(111111, 999999)
        ntp = prefix + str(acak)
        q = DBSession.query(IsoPayment).filter_by(ntp=ntp)
        if not q.first():
            return ntp
        loop += 1
        if loop == max_loop:
            raise ERR_NTP

def db_flush(orm):
    DBSession.add(orm)
    DBSession.flush()


class DbTransaction(Transaction):
    def transaction_init(self):
        self.invoice_id_raw = None # Cache
        self.invoice_profile = FixLength(INVOICE_PROFILE)

    def _get_invoice(self):
        self.invoice_id_raw = self.from_iso.get_invoice_id()
        self.calc = CalculateInvoice(self.invoice_id_raw)
        if self.calc.invoice:
            return True
        return self.ack_invoice_not_available()

    def get_invoice(self):
        if self._get_invoice():
            self.calc.hitung()
            return True

    def set_invoice_profile(self):
        inv = self.calc.invoice
        self.invoice_profile.from_dict({
            'NPWPD': inv.npwpd,
            'Nama': inv.nama_wajibpajak, 
            'Alamat 1': '',
            'Alamat 2': '',
            'Kode Rekening': inv.kode_rekening.replace('.', ''),
            'Nama Rekening': inv.nama_rekening,
            'Tagihan': self.calc.tagihan,
            'Denda': self.calc.denda,
            'Total': self.calc.total,
            'Masa 1': inv.spt_periode_jual1.strftime('%Y%m%d'),
            'Masa 2': inv.spt_periode_jual2.strftime('%Y%m%d'),
            })
        Transaction.set_invoice_profile(self)

    def _inquiry(self):
        if not self.get_invoice():
            return
        if self.calc.total > 0:
            self.set_amount(self.calc.total)
        self.set_invoice_profile()
        if self.calc.paid:
            return self.ack_already_paid()
        if self.calc.total < 0:
            return self.ack_invalid_amount()
        return True

    # Override
    def inquiry_response(self):
        try:
            self.inquiry_response_()
        except:
            self.ack_other_error('Ada kesalahan saat yang belum dipahami.')
            f = StringIO()
            traceback.print_exc(file=f)
            self.log_error(f.getvalue())
            f.close()

    def inquiry_response_(self):
        self.transaction_init()
        if not self._inquiry():
            return self.set_amount(0)
        self.set_amount(self.calc.total)
        self.ack()

    # Override
    def payment_response(self):
        try:
            self.payment_response_()
        except:
            self.ack_other_error('Ada kesalahan yang belum dipahami.')
            f = StringIO()
            traceback.print_exc(file=f)
            self.log_error(f.getvalue())
            f.close()

    def payment_response_(self):
        Transaction.payment_response(self)
        self.transaction_init()
        if not self._inquiry():
            return
        if self.calc.total != self.from_iso.get_amount():
            return self.ack_insufficient_fund()
        pay = self.save_payment()
        iso_pay = self.save_iso_payment(pay)
        self.set_ntp(iso_pay.ntp)
        self.commit()

    def save_payment(self):
        tgl_bayar = self.from_iso.get_transaction_time()
        pay = Payment.create(self.calc.invoice, tgl_bayar, self.calc.tagihan)
        db_flush(pay)
        if self.calc.invoice.spt_status == 8:
            pay_detail = PaymentDetail.create(pay, self.calc.invoice,
                            self.calc.invoice.korek_id)
            db_flush(pay_detail)
        if self.calc.denda:
            self.save_denda(pay)
        return pay

    def save_denda(self, pay):
        inv_denda = Invoice.create_denda(self.calc.invoice, pay)
        inv_denda.netapajrek_besaran = self.calc.denda
        inv_denda.netapajrek_keterangan = KET_DENDA.format(
            bln=self.calc.bln_tunggakan, persen=self.calc.persen_denda,
            tagihan=self.calc.tagihan)
        db_flush(inv_denda)
        pay_denda = Payment.create_denda(pay, inv_denda)
        db_flush(pay_denda)
        if self.calc.invoice.spt_status == 8:
            pay_detail = PaymentDetail.create(pay_denda, self.calc.invoice,
                            inv_denda.netapajrek_kode_rek)
            db_flush(pay_detail)

    def save_iso_payment(self, pay):
        no_bukti = str(pay.setorpajret_no_bukti).zfill(6)
        ntp = get_ntp(no_bukti)
        iso_pay = IsoPayment()
        iso_pay.id = pay.setorpajret_id
        iso_pay.iso_request = self.from_iso.raw.upper()
        iso_pay.transaction_time = self.from_iso.get_transaction_time()
        iso_pay.spt_id = self.calc.invoice.spt_id
        iso_pay.tahun_bayar = pay.setorpajret_time.year
        iso_pay.nomor_bukti = pay.setorpajret_no_bukti
        iso_pay.tagihan = self.calc.tagihan
        iso_pay.denda = self.calc.denda
        iso_pay.total_bayar = self.calc.total
        iso_pay.ntb = self.from_iso.get_ntb()
        iso_pay.ntp = ntp
        iso_pay.bank_id = self.get_bank_id()
        iso_pay.channel_id = self.from_iso.get_channel_id()
        iso_pay.bank_ip = self.get_bank_ip()
        DBSession.add(iso_pay)
        DBSession.flush()
        return iso_pay 

    # Override
    def reversal_response(self):
        try:
            self.reversal_response_()
        except:
            self.ack_other_error('Ada kesalahan yang belum dipahami.')
            f = StringIO()
            traceback.print_exc(file=f)
            self.log_error(f.getvalue())
            f.close()

    def reversal_response_(self):
        if not self._get_invoice():
            return
        if not self.calc.paid:
            return self.ack_already_canceled()
        q_iso_pay = DBSession.query(IsoPayment).\
                        filter_by(bank_id=self.get_bank_id(),
                                  ntb=self.from_iso.get_ntb(),
                                  spt_id=self.calc.invoice.spt_id).\
                        order_by(IsoPayment.id.desc())
        iso_pay = q_iso_pay.first()
        if not iso_pay:
            return self.ack_payment_not_found()
        self.save_iso_reversal(iso_pay)

    def save_iso_reversal(self, iso_pay):
        iso_pay.total_bayar = 0
        DBSession.add(iso_pay)
        q = DBSession.query(IsoReversal).filter_by(id=iso_pay.id)
        if not q.first():
            iso_rev = IsoReversal()
            iso_rev.id = iso_pay.id
            iso_rev.iso_request = self.from_iso.raw.upper()
            DBSession.add(iso_rev)
        DBSession.flush()
        if iso_pay.denda:
            q_inv_denda = DBSession.query(Invoice).\
                filter_by(netapajrek_setoran_sebelumnya=iso_pay.id)
            inv_denda = q_inv_denda.first()
            q_pay_denda = DBSession.query(Payment).filter_by(
                setorpajret_id_penetapan=inv_denda.netapajrek_id)
            pay_denda = q_pay_denda.first()
            DBSession.query(PaymentDetail).\
                filter_by(sprsd_id_setor=pay_denda.setorpajret_id).delete()
            q_pay_denda.delete()
            q_inv_denda.delete()
        DBSession.query(PaymentDetail).\
            filter_by(sprsd_id_setor=iso_pay.id).delete()
        DBSession.query(Payment).filter_by(setorpajret_id=iso_pay.id).\
            delete()
        self.commit()

    def commit(self):
        DBSession.commit()
        self.ack()

        

