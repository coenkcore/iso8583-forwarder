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
# from pbb_conf import (
    # host,
    # is_update_sppt,
    # )
from multi_conf import host, pbb_db_url, bphtb_db_url, padl_db_url, webr_db_url

from multi_transaction import Transaction
from multi_structure import (
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
#sys.path[0:0] = ['/usr/share/opensipkd-forwarder/modules/multi/pbb']
from pbb.pbb_db_transaction import PbbDbTransaction
from pbb.pbb_reversal import PbbReversal
#sys.path[0:0] = ['/usr/share/opensipkd-forwarder/modules/bca/bphtb']
from bphtb.bphtb_fix_db_transaction import BphtbDbTransaction
from bphtb.bphtb_reversal import BphtbReversal

from padl.padl_transaction import PadlDbTransaction
from padl.padl_reversal import PadlReversal

from webr.webr_transaction import WebrDbTransaction
from webr.webr_reversal import WebrReversal

from log_models import (
#    INQUIRY_SEQ,
    Payment,
    Reversal,
    MyFixLength
    )

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
class MultiDbTransaction(Transaction):
    def __init__(self, *args, **kwargs):
        Transaction.__init__(self, *args, **kwargs)
    def is_pbb(self):
        code = self.from_iso.get_value(3).strip()
        return pbb_db_url and code in ['341019','541019']
    
    # def is_non_pbb(self):
        # code = self.from_iso.get_value(3).strip()
        # return padl_db_url and code in ['300801','500801']
        
    def is_bphtb(self):
        code = self.from_iso.get_value(3).strip()
        print code
        return bphtb_db_url and code in ['341066','541066']
    
    def is_padl(self):
        code = self.from_iso.get_value(3).strip()
        return padl_db_url and code in ['300001','500001']
        
    def is_bca(self):
        code = self.from_iso.get_value(3).strip()
        return code in ['300801','500801']
    
    def is_webr(self):
        code = self.from_iso.get_value(3).strip()
        return webr_db_url and code in ['300020','500020']
        
    def set_invoice_profile(self):
        v = self.calc.invoice_profile.get_raw()
        self.setBit(62, v) 

    def _inquiry_response(self):
        self.init_id()
        
        inv = self.get_module()
        if inv:
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
        #print self.calc.invoice_profile.get_raw()
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
        #try:
        self._inquiry_response()
        # except:
            # f = StringIO()
            # traceback.print_exc(file=f)
            # self.log_error(f.getvalue())
            # f.close()
            # self.ack_other('other error')

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
        
        
    def get_module(self):
        if self.is_pbb():
            inv = PbbDbTransaction(invoice_id=self.invoice_id_raw, conf=self.conf,
                   channel=self.get_channel())
        elif self.is_bphtb():
            inv = BphtbDbTransaction(invoice_id=self.invoice_id_raw, conf=self.conf,
                   channel=self.get_channel())
        elif self.is_padl():
            inv = PadlDbTransaction(invoice_id=self.invoice_id_raw, conf=self.conf,
                   channel=self.get_channel())
        elif self.is_bca():
            print '**** DEBUG BCA'
            if self.invoice_id_raw[4:2]=='01':
                inv = BphtbDbTransaction(invoice_id=self.invoice_id_raw, conf=self.conf,
                       channel=self.get_channel())
            else:
                inv = PadlDbTransaction(invoice_id=self.invoice_id_raw, conf=self.conf,
                       channel=self.get_channel())
        elif self.is_webr():
            inv = WebrDbTransaction(invoice_id=self.invoice_id_raw, conf=self.conf,
                   channel=self.get_channel())
        else:
            return None
        return inv
    
    #########
    #PAYMENT#
    #########
    def _payment_response(self):
        self.init_id()
        self.init_id_pay()
        bank_name = self.conf['name']
        self.conf.update(host[bank_name])
        self.setBit(47, '') # default payment ID
        inv = self.get_module()
        if inv:
            self.calc = inv.get_invoice()
        else:
            return self.ack_other('other error')
            
        if self.calc.paid:
            print "debug", self.invoice_id_raw, self.get_channel(), self.bank_id, self.get_value(48)
            q = DBSession.query(Payment).\
                          filter_by(invoice_id=self.invoice_id_raw,
                                    channel=self.get_channel(),
                                    bank_id=self.bank_id,
                                    ntb = self.ntb,)
            pay = q.first()
            if pay:
               self.setBit(47, pay.ntp)
               return 
            else:
               return self.ack_already_paid()
            
        if self.calc.total <= 0:
            return self.ack_already_paid_2()
            
        total_tagihan = self.calc.total
        if self.total_bayar != total_tagihan:
            return self.ack_insufficient_fund(total_bayar, total_tagihan)
            
        tp = "".join([self.tgl_bayar.strftime('%Y'),self.bank_id])
        payment_id = create_payment_id(tp)
        if not payment_id:
            return self.ack_create_payment_failed()
        
        bayar, urutan_ke = inv.create_payment(total_bayar=self.total_bayar, 
                                              tgl_bayar=self.tgl_bayar,
                                              seq = self.ntb, #bit 37
                                              ntb = self.get_value(48),
                                              bank_id=self.bank_id,
                                              ntp = payment_id,
                                              channel_id = self.get_channel(),
                                              )
        payment = self.log_payment(urutan_ke,payment_id) 
        if not payment:
            return self.ack_create_payment_failed()
            
        DBSession.add(payment)
        inv.commit()
        self.commit()
        self.setBit(47, str(payment.id))

    def log_payment(self, urutan_ke, payment_id):
        payment = Payment(id=payment_id)
        payment.invoice_id   = self.invoice_id_raw
        payment.bank_id      = self.bank_id
        payment.forwarder_id = self.forwarder_id
        payment.amount       = self.total_bayar
        payment.transaction_date = self.tgl_bayar
        payment.ntp          = payment_id
        payment.ntb          = self.ntb
        payment.ke           = urutan_ke
        payment.channel      = self.get_channel()
        payment.status       = 1
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

    def init_id(self):
        self.invoice_id_raw = self.from_iso.get_value(61).strip()
        self.bank_id       = self.from_iso.get_value(32).strip()
        self.forwarder_id  = self.from_iso.get_value(33).strip()
        return 
        
    def init_id_pay(self):
        self.total_bayar   = int(self.from_iso.get_value(4))
        self.tgl_bayar     = self.from_iso.get_transaction_datetime()
        self.ntb           = self.from_iso.get_value(37).strip()
            
    ############
    # Reversal #
    ############
    def _reversal_response(self):
        self.init_id()
        self.init_id_pay()

        q = DBSession.query(Payment).filter_by(
               invoice_id = self.invoice_id_raw,
               bank_id=self.bank_id,
               forwarder_id = self.forwarder_id,
               ntb = self.ntb
               )
               
        pay = q.first()
        if not pay:
            return self.ack_payment_not_found()

        if pay.status==0:
            self.setBit('39','54')
            return 
        
        reversal_iso_request = ISO8583.getRawIso(self.from_iso).upper()
        if self.is_pbb():
            rev = PbbReversal(pay) 
        elif self.is_bphtb():
            rev = BphtbReversal(pay) 
        elif self.is_padl():
            rev = PadlReversal(pay) 
        elif self.is_webr():
            rev = WebrReversal(pay) 
        elif self.is_bca():
            print '**** DEBUG BCA'
            if self.invoice_id_raw[4,2]=='01':
                rev = BphtbReversal(pay) 
            else:
                rev = PadlReversal(pay) 
        else:
            return self.ack_other('other error')

        if not rev.bayar:
            return self.ack_payment_not_found_2(self.invoice_id_raw, pay.ke)
        if not rev.invoice:
            return self.ack_not_available_2(self.invoice_id_raw)
        # if not rev.is_paid():
            # return self.ack_invoice_open(self.invoice_id_raw)
        rev.set_unpaid()
        
        reversal = Reversal(payment_id=pay.id) # Catatan tambahan
        reversal.iso_request = reversal_iso_request
        pay.status = 0
        DBSession.add(reversal)
        DBSession.add(pay)
        rev.commit()
        self.commit()
        self.settlement.set_raw(self.from_iso.get_value(13))
        return
        
    def reversal_response(self):
        #try:
        self._reversal_response()
        # except:
            # f = StringIO()
            # traceback.print_exc(file=f)
            # self.log_error(f.getvalue())
            # f.close()
            # self.ack_other('other error')
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
        p = self.invoice2payment(self.calc.invoice)
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

    def invoice2payment(self, sppt):
        q = DBSession.query(Payment).filter_by(
                invoice_id=self.invoice_id_raw)
        return q.order_by('ke DESC').first()
