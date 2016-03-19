import sys
import traceback
from StringIO import StringIO
from random import randrange
from types import DictType
from ISO8583.ISO8583 import ISO8583
sys.path[0:0] = ['/usr/share/opensipkd/modules']
from tools import FixLength
from base_models import DBSession
sys.path[0:0] = ['/etc/opensipkd']
from pbb_conf import (
    host,
    is_update_sppt,
    )
from bca_transaction import Transaction
from bca_structure import (
    RC_INVALID_NUMBER,
    RC_ALREADY_PAID,
    RC_NOT_AVAILABLE,
    RC_INSUFFICIENT_FUND,
    RC_OTHER_ERROR,
    ERR_INVALID_NUMBER,
    ERR_NOT_AVAILABLE,
    ERR_ALREADY_PAID,
    ERR_ALREADY_PAID_2,
    ERR_INQUIRY_NOT_FOUND,
    ERR_INSUFFICIENT_FUND,
    ERR_PAYMENT_NOT_FOUND,
    ERR_PAYMENT_NOT_FOUND_2,
    ERR_CREATE_PAYMENT,
    ERR_INVOICE_OPEN,
    ERR_SETTLEMENT_DATE,
    )
sys.path[0:0] = ['/usr/share/opensipkd-forwarder/modules/bca/pbb']
from pbb_db_transaction import PbbDbTransaction
#from pbb_models import (
#    INQUIRY_SEQ,
#    Payment,
#    Reversal,
#    )


class MyFixLength(FixLength):
    def get(self, name):
        return self.fields[name]['value'] or None


def inquiry_id():
    return INQUIRY_SEQ.execute(DBSession.bind)

def create_payment_id(prefix):
    max_loop = 10
    loop = 0
    while True:
        acak = randrange(11111111, 99999999)
        acak = str(acak)
        trx_id = ''.join([prefix, acak])
        print('Check Trx ID %s' % trx_id)
        q = DBSession.query(Payment).filter_by(id=trx_id)
        found = q.first()
        if not found:
            return trx_id
        loop += 1
        if loop == max_loop:
            print('*** Max loop for create payment ID. Call your programmer please.')
            return

def pay2invoice_id(pay):
    return ''.join([pay.propinsi, pay.kabupaten, pay.kecamatan,
        pay.kelurahan, pay.blok, pay.urut, pay.jenis, str(pay.tahun)])



# Abstract class
class BcaDbTransaction(Transaction):
    def __init__(self, *args, **kwargs):
        Transaction.__init__(self, *args, **kwargs)
    def is_pbb(self):
        code = self.from_iso.get_value(3).strip()
        return code in ['341019','541019']
    
    def is_non_pbb(self):
        code = self.from_iso.get_value(3).strip()
        return code in ['300801','500801']
        
    def is_bphtb(self):
        code = self.from_iso.get_value(3).strip()
        return code in ['341066','541066']
    
    def is_padl(self):
        code = self.from_iso.get_value(3).strip()
        return code in ['300001','500001']
        
    # def get_calc_cls(self): # override
        # return

    # def invoice_id2profile(self):
        # pass
    # def sppt2profile(self): # override
        # pass

    def set_invoice_profile(self):
        v = self.calc.invoice_profile.get_raw()
        self.setBit(62, v) 

    def _inquiry_response(self):
        self.invoice_id_raw = self.from_iso.get_value(61).strip()
        if self.is_pbb():
            inv = PbbDbTransaction(invoice_id=self.invoice_id_raw, conf=self.conf,
                   channel=self.get_channel())
            self.calc = inv.get_invoice()
        else:
            return self.ack_other('other error')
        if not self.calc.invoice:
            return self.ack_not_available()    
            
        if self.calc.paid:
            return self.ack_already_paid()
            
        if self.calc.total <= 0:
            return self.ack_already_paid_2()
        
        settlement_date = self.from_iso.get_settlement()
        if not settlement_date:
            return self.ack_other('other error')
        
        self.setBit(4, self.calc.total)
        self.set_invoice_profile()
        
        #self.ack_ok
          
        #LOG DATABASE
        # inq = self.create_inquiry()
        # inq.stan = self.from_iso.get_value(11)
        # inq.pengirim = self.from_iso.get_value(33)
        # inq.transmission = self.from_iso.get_transmission()
        # inq.settlement = settlement_date
        
        # DBSession.add(inq)
        # self.commit()
        #LOG DATABASE END
        
    def inquiry_response(self):
        self.setBit(39, '00')
        try:
            self._inquiry_response()
        except:
            f = StringIO()
            traceback.print_exc(file=f)
            self.log_error(f.getvalue())
            f.close()
            self.ack_other('other error')

    def create_inquiry(self): # override
        inv = self.calc.invoice
        bumi = int(inv.luas_bumi_sppt)
        bangunan = int(inv.luas_bng_sppt)
        njop = inv.njop_bumi_sppt + inv.njop_bng_sppt
        nop = sppt2nop(inv)
        inq = Inquiry(nop=nop, propinsi=inv.kd_propinsi, kabupaten=inv.kd_dati2,
                  kecamatan=inv.kd_kecamatan, kelurahan=inv.kd_kelurahan,
                  blok=inv.kd_blok, urut=inv.no_urut, jenis=inv.kd_jns_op,
                  tahun=inv.thn_pajak_sppt, tgl=self.calc.kini)
        inq.id = inquiry_id()
        inq.tagihan = self.calc.tagihan
        inq.denda = self.calc.denda
        inq.persen_denda = persen_denda
        inq.jatuh_tempo = inv.tgl_jatuh_tempo_sppt
        inq.bulan_tunggakan = self.calc.bln_tunggakan
        return inq

    def _payment_response(self):
        bank_name = self.conf['name']
        self.conf.update(host[bank_name])
        
        # self.copy([4, 48, 62]) # belum di-copy oleh set_transaction_response()
        #self.setBit(47, '') # default payment ID
        self.invoice_id_raw = self.from_iso.get_value(61).strip()
        if self.is_pbb():
            inv = PbbDbTransaction(invoice_id=self.invoice_id_raw, conf=self.conf,
                   channel=self.get_channel())
            self.calc = inv.get_invoice()
        else:
            return self.ack_other('other error')
            
        if self.calc.paid:
            return self.ack_already_paid()
            
        if self.calc.total <= 0:
            return self.ack_already_paid_2()
        ##todo: dibypass dulu lognya belum ada
        # inq = self.invoice2inquiry()
        # if not inq:
            # return self.ack_inquiry_not_found()
        inq = None    
        total_bayar = int(self.from_iso.get_value(4))
        total_tagihan = self.calc.total
        if total_bayar != total_tagihan:
            return self.ack_insufficient_fund(total_bayar, total_tagihan)
            
        bayar = inv.create_payment(total_bayar, self.from_iso.get_transaction_date())
        #todo
        #payment = log_payment(total_bayar, self.from_iso.get_transaction_date()) 
        
        #if not payment:
        #    return self.ack_create_payment_failed()
        # is_update_sppt and self.calc.set_paid()
        # DBSession.add(inv)
        # DBSession.add(bayar)
        # DBSession.add(payment)
        # self.setBit(47, str(payment.id))
        #self.commit()
        inv.commit()

    def log_payment():
        # tp = ''
        # d = bayar.to_dict()
        # for fieldname in self.get_field_bank_non_tp():
            # tp += d[fieldname] or '00'
        #payment_id = create_payment_id(tp)
        # if not payment_id:
            # return None, None
        # payment = Payment(id=payment_id)
        # payment.inquiry_id = inq.id
        # payment.propinsi = inq.propinsi
        # payment.kabupaten = inq.kabupaten
        # payment.kecamatan = inq.kecamatan
        # payment.kelurahan = inq.kelurahan
        # payment.blok = inq.blok
        # payment.urut = inq.urut
        # payment.jenis = inq.jenis
        # payment.tahun = inq.tahun
        # payment.ke = urutan_bayar 
        # for fieldname in self.get_field_bank():
            # value = d[fieldname] or '00'
            # payment.from_dict({fieldname: value})
        # payment.channel = self.channel
        # payment.ntb = self.from_iso.get_value(48) # Nomor Transaksi Bank
        # payment.iso_request = ISO8583.getRawIso(self.from_iso).upper()
        return payment
        
    def payment_response(self):
        self.setBit(39, '00')
        #try:
        self._payment_response()
        # except:
            # f = StringIO()
            # traceback.print_exc(file=f)
            # self.log_error(f.getvalue())
            # f.close()
            # self.ack_other('other error')

    # def invoice2payment(self): # override
        # return

    def get_channel(self):
        return self.from_iso.get_value(18) # Merchant / Channel 

    # def get_real_value(self, value):
        # if type(value) is not DictType:
            # return value
        # if self.channel in value:
            # return value[self.channel]
        # if 'default' in value:
            # return value['default']
        # return '00'

    # def bayar(self, inq, total_bayar): # override
        # return

    # def get_field_bank(self): # override
        # return

    # def get_field_bank_non_tp(self): # override
        # return

    ############
    # Reversal #
    ############
    # def _reversal_response(self):
        # reversal_iso_request = ISO8583.getRawIso(self.from_iso).upper()
        # pay_iso_request = '0200' + reversal_iso_request[4:]
        # q = DBSession.query(Payment).filter_by(iso_request=pay_iso_request)
        # pay = q.first()
        # if not pay:
            # return self.ack_payment_not_found()
        # invoice_id = pay2invoice_id(pay)
        # cls = self.get_reversal_cls()
        # rev = cls(pay) 
        # if not rev.bayar:
            # return self.ack_payment_not_found_2(invoice_id, pay.ke)
        # if not rev.invoice:
            # return self.ack_not_available_2(invoice_id)
        # if not rev.is_paid():
            # return self.ack_invoice_open(invoice_id)
        # rev.set_unpaid()
        # reversal = Reversal(payment_id=pay.id) # Catatan tambahan
        # reversal.iso_request = reversal_iso_request
        # DBSession.add(rev.bayar)
        # DBSession.add(rev.invoice)
        # DBSession.add(reversal)
        # self.commit()
        #self.settlement.set_raw(self.from_iso.get_value(13))
        # return
    # def reversal_response(self):
        # try:
            # self._reversal_response()
        # except:
            # f = StringIO()
            # traceback.print_exc(file=f)
            # self.log_error(f.getvalue())
            # f.close()
            # self.ack_other('other error')
        # return
    # def get_reversal_cls(self): # override
        # return

    ##################
    # Aknowledgement #
    ##################
    def ack_invalid_number(self):
        msg = ERR_INVALID_NUMBER.format(invoice_id=self.invoice_id_raw)
        self.ack(RC_INVALID_NUMBER, msg)

    def ack_not_available(self):
        msg = ERR_NOT_AVAILABLE.format(invoice_id=self.invoice_id_raw)
        self.ack(RC_NOT_AVAILABLE, msg)

    def ack_not_available_2(self, invoice_id):
        msg = ERR_NOT_AVAILABLE.format(invoice_id=invoice_id)
        self.ack(RC_NOT_AVAILABLE, msg)

    def ack_already_paid(self):
        p = self.invoice2payment()
        self.setBit(47, p and str(p.id) or '')
        msg = ERR_ALREADY_PAID.format(invoice_id=self.invoice_id_raw)
        self.ack(RC_ALREADY_PAID, msg)

    def ack_already_paid_2(self):
        msg = ERR_ALREADY_PAID_2.format(invoice_id=self.invoice_id_raw,
                nominal=self.calc.total)
        self.ack(RC_ALREADY_PAID, msg)

    def ack_other(self, msg):
        self.ack(RC_OTHER_ERROR, msg)

    def ack_create_payment_failed(self):
        self.ack_other(ERR_CREATE_PAYMENT)

    def ack_inquiry_not_found(self):
        msg = ERR_INQUIRY_NOT_FOUND.format(invoice_id=self.invoice_id_raw)
        self.ack_other(msg)

    def ack_insufficient_fund(self, total_bayar, total_tagihan):
        msg = ERR_INSUFFICIENT_FUND.format(invoice_id=self.invoice_id_raw,
                bayar=total_bayar,
                tagihan=total_tagihan)
        self.ack(RC_INSUFFICIENT_FUND, msg)

    def ack_payment_not_found(self):
        self.ack(RC_NOT_AVAILABLE, ERR_PAYMENT_NOT_FOUND)

    def ack_payment_not_found_2(self, invoice_id, ke):
        msg = ERR_PAYMENT_NOT_FOUND_2.format(invoice_id=invoice_id, ke=ke)
        self.ack(RC_NOT_AVAILABLE, msg)

    def ack_invoice_open(self, invoice_id):
        msg = ERR_INVOICE_OPEN.format(invoice_id=invoice_id)
        self.ack(RC_ALREADY_PAID, msg)

    ###########
    # Profile #
    ###########
    def commit(self):
        DBSession.flush()
        DBSession.commit()
        self.ack()
# def invoice2inquiry(sppt):
#    q = DBSession.query(Inquiry).filter_by(
            # propinsi=sppt.kd_propinsi,
            # kabupaten=sppt.kd_dati2,
            # kecamatan=sppt.kd_kecamatan,
            # kelurahan=sppt.kd_kelurahan,
            # blok=sppt.kd_blok,
            # urut=sppt.no_urut,
            # jenis=sppt.kd_jns_op,
            # tahun=sppt.thn_pajak_sppt)
    # return q.order_by('id DESC').first()

# def invoice2payment(sppt):
    # q = PbbDbSession.query(Payment).filter_by(
            # propinsi=sppt.kd_propinsi,
            # kabupaten=sppt.kd_dati2,
            # kecamatan=sppt.kd_kecamatan,
            # kelurahan=sppt.kd_kelurahan,
            # blok=sppt.kd_blok,
            # urut=sppt.no_urut,
            # jenis=sppt.kd_jns_op,
            # tahun=sppt.thn_pajak_sppt)
    # return q.order_by('ke DESC').first()
