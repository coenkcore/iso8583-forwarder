import sys
from random import randrange
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    Sequence,
    UniqueConstraint,
    )
from sqlalchemy.sql.expression import func
from types import DictType
sys.path[0:0] = ['/usr/share/opensipkd/modules']
from tools import FixLength
from base_models import DBSession
sys.path[0:0] = ['/etc/opensipkd']
from pbb_conf import (
    persen_denda,
    nip_rekam_byr_sppt,
    host,
    )
sys.path[0:0] = ['/usr/share/opensipkd-forwarder/modules/pbb']
from pbb_transaction import Transaction
from pbb_structure import (
    INVOICE_ID,
    INVOICE_PROFILE,
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
    )
from models import (
    Invoice,
    Pembayaran,
    Kelurahan,
    Kecamatan,
    Kabupaten,
    Propinsi,
    Inquiry,
    Payment,
    Reversal,
    INQUIRY_SEQ,
    )
from CalculateInvoice import (
    CalculateInvoice,
    query_sppt,
    )

class MyFixLength(FixLength):
    def get(self, name):
        return self.fields[name]['value'] or None


def cari_kelurahan(propinsi, kabupaten, kecamatan, kelurahan):
    q = DBSession.query(Kelurahan).filter_by(
            kd_propinsi=propinsi,
            kd_dati2=kabupaten,
            kd_kecamatan=kecamatan,
            kd_kelurahan=kelurahan)
    r = q.first()
    return r and r.nm_kelurahan or ''

def cari_kecamatan(propinsi, kabupaten, kecamatan):
    q = DBSession.query(Kecamatan).filter_by(
            kd_propinsi=propinsi,
            kd_dati2=kabupaten,
            kd_kecamatan=kecamatan)
    r = q.first()
    return r and r.nm_kecamatan or ''

def cari_propinsi(propinsi):
    q = DBSession.query(Propinsi).filter_by(kd_propinsi=propinsi)
    r = q.first()
    return r and r.nm_propinsi or ''

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

def sppt2nop(sppt):
    return sppt.kd_propinsi + sppt.kd_dati2 + sppt.kd_kecamatan + \
           sppt.kd_kelurahan + sppt.kd_blok + sppt.no_urut + sppt.kd_jns_op

def nama_jalan_op(sppt):
    return sppt.jln_wp_sppt


def create_inquiry(calc):
    sppt = calc.invoice
    bumi = int(sppt.luas_bumi_sppt)
    bangunan = int(sppt.luas_bng_sppt)
    njop = sppt.njop_bumi_sppt + sppt.njop_bng_sppt
    nop = sppt2nop(sppt)
    inq = Inquiry(nop=nop, propinsi=sppt.kd_propinsi, kabupaten=sppt.kd_dati2,
                  kecamatan=sppt.kd_kecamatan, kelurahan=sppt.kd_kelurahan,
                  blok=sppt.kd_blok, urut=sppt.no_urut, jenis=sppt.kd_jns_op,
                  tahun=sppt.thn_pajak_sppt, tgl=calc.kini)
    inq.id = inquiry_id()
    inq.tagihan = calc.tagihan
    inq.denda = calc.denda 
    inq.persen_denda = persen_denda
    inq.jatuh_tempo = sppt.tgl_jatuh_tempo_sppt
    inq.bulan_tunggakan = calc.bln_tunggakan
    return inq

def invoice2inquiry(sppt):
    q = DBSession.query(Inquiry).filter_by(
            propinsi=sppt.kd_propinsi,
            kabupaten=sppt.kd_dati2,
            kecamatan=sppt.kd_kecamatan,
            kelurahan=sppt.kd_kelurahan,
            blok=sppt.kd_blok,
            urut=sppt.no_urut,
            jenis=sppt.kd_jns_op,
            tahun=sppt.thn_pajak_sppt)
    return q.order_by('id DESC').first()

def invoice2payment(sppt):
    q = DBSession.query(Payment).filter_by(
            propinsi=sppt.kd_propinsi,
            kabupaten=sppt.kd_dati2,
            kecamatan=sppt.kd_kecamatan,
            kelurahan=sppt.kd_kelurahan,
            blok=sppt.kd_blok,
            urut=sppt.no_urut,
            jenis=sppt.kd_jns_op,
            tahun=sppt.thn_pajak_sppt)
    return q.order_by('ke DESC').first()

def query_pembayaran(propinsi, kabupaten, kecamatan, kelurahan, blok, urut,
        jenis, tahun):
    return DBSession.query(Pembayaran).filter_by(
                kd_propinsi=propinsi,
                kd_dati2=kabupaten,
                kd_kecamatan=kecamatan,
                kd_kelurahan=kelurahan,
                kd_blok=blok,
                no_urut=urut,
                kd_jns_op=jenis,
                thn_pajak_sppt=tahun)

def inq2bayar(inq):
    q = query_pembayaran(inq.propinsi, inq.kabupaten, inq.kecamatan,
            inq.kelurahan, inq.blok, inq.urut, inq.jenis, str(inq.tahun))
    q = q.order_by('pembayaran_sppt_ke DESC')
    return q.first()

def pay2invoice_id(pay):
    return ''.join([pay.propinsi, pay.kabupaten, pay.kecamatan,
        pay.kelurahan, pay.blok, pay.urut, pay.jenis, str(pay.tahun)])

def pay2bayar(pay):
    q = query_pembayaran(pay.propinsi, pay.kabupaten, pay.kecamatan,
            pay.kelurahan, pay.blok, pay.urut, pay.jenis, str(pay.tahun))
    q = q.filter_by(pembayaran_sppt_ke=pay.ke)
    return q.first()

def pay2sppt(pay):
    q = query_sppt(pay.propinsi, pay.kabupaten, pay.kecamatan, pay.kelurahan,
            pay.blok, pay.urut, str(pay.tahun))
    return q.first() 


FIELD_BANK = ['kd_kanwil', 'kd_kantor', 'kd_bank_tunggal',
              'kd_bank_persepsi', 'kd_tp']
FIELD_BANK_NON_TP = FIELD_BANK[:-1]

class DbTransaction(Transaction):
    def __init__(self, *args, **kwargs):
        self.invoice_id = MyFixLength(INVOICE_ID)
        self.invoice_id_raw = None # Cache
        self.invoice_profile = MyFixLength(INVOICE_PROFILE)
        Transaction.__init__(self, *args, **kwargs)

    def get_invoice(self):
        self.invoice_id_raw = self.from_iso.get_value(61).strip()
        if not self.invoice_id.set_raw(self.invoice_id_raw):
            return self.ack_invalid_number()
        self.invoice_id2profile()
        self.calc = CalculateInvoice(
            self.invoice_id['Propinsi'],
            self.invoice_id['Kabupaten'],
            self.invoice_id['Kecamatan'],
            self.invoice_id['Kelurahan'],
            self.invoice_id['Blok'],
            self.invoice_id['Urut'],
            self.invoice_id['Jenis'],
            self.invoice_id['Tahun Pajak'])
        if not self.calc.invoice:
            return self.ack_not_available()
        self.sppt2profile()
        self.channel = self.get_channel()
        return self.calc.invoice 

    def invoice_id2profile(self):
        nama_kelurahan = self.nama_kelurahan()
        nama_kecamatan = self.nama_kecamatan()
        nama_propinsi = self.nama_propinsi()
        self.invoice_profile.from_dict({
            'Propinsi': self.invoice_id['Propinsi'],
            'Kabupaten': self.invoice_id['Kabupaten'],
            'Kecamatan': self.invoice_id['Kecamatan'],
            'Kelurahan': self.invoice_id['Kelurahan'],
            'Blok': self.invoice_id['Blok'],
            'Urut': self.invoice_id['Urut'],
            'Jenis': self.invoice_id['Jenis'],
            'Tahun Pajak': self.invoice_id['Tahun Pajak'],
            'Nama Kelurahan': nama_kelurahan,
            'Nama Kecamatan': nama_kecamatan,
            'Nama Propinsi': nama_propinsi})

    def sppt2profile(self):
        inv = self.calc.invoice
        self.invoice_profile.from_dict({
            'Nama': inv.nm_wp_sppt,
            'Luas Tanah': int(inv.luas_bumi_sppt),
            'Luas Bangunan': int(inv.luas_bng_sppt),
            'Lokasi': nama_jalan_op(inv)})

    def invoice2sppt(self):
        q = query_sppt(self.invoice_id['Propinsi'],
                self.invoice_id['Kabupaten'],
                self.invoice_id['Kecamatan'],
                self.invoice_id['Kelurahan'],
                self.invoice_id['Blok'],
                self.invoice_id['Urut'],
                self.invoice_id['Jenis'],
                self.invoice_id['Tahun Pajak'])
        return q.first()

    def set_invoice_profile(self):
        v = self.invoice_profile.get_raw()
        self.setBit(62, v) 

    def inquiry_response(self):
        inv = self.get_invoice()
        if not inv:
            return
        if self.calc.paid:
            return self.ack_already_paid()
        if self.calc.total <= 0:
            return self.ack_already_paid_2()
        inq = create_inquiry(self.calc)
        inq.stan = self.from_iso.get_value(11)
        inq.pengirim = self.from_iso.get_value(33)
        self.setBit(4, self.calc.total)
        self.invoice_profile.from_dict({
            'Jatuh Tempo': inq.jatuh_tempo.strftime('%Y%m%d'),
            'Tagihan': self.calc.tagihan,
            'Denda': self.calc.denda,
            'Total Bayar': self.calc.total})
        self.transmission.set_raw(self.from_iso.get_value(7))
        inq.transmission = self.transmission.get_value()
        self.settlement.set_raw(self.from_iso.get_value(13))
        try:
            inq.settlement = self.settlement.get_value()
        except ValueError:
            raw = ''.join([self.settlement.values[2], self.settlement.values[4]])
            msg = 'Settlement date {raw} tidak benar.'.format(raw=[raw])
            self.error_func('Settlement date %s tidak benar.' % [raw])
            return
        self.set_invoice_profile()
        DBSession.add(inq)
        self.commit()

    def payment_response(self):
        self.copy([4, 48, 62]) # belum di-copy oleh set_transaction_response()
        self.setBit(47, '') # default payment ID
        inv = self.get_invoice()
        if not inv:
            return
        invoice_id = self.from_iso.get_value(61).strip()
        if self.calc.paid:
            p = invoice2payment(inv)
            self.setBit(47, p and str(p.id) or '')
            return self.ack_already_paid()
        if self.calc.total <= 0:
            return self.ack_already_paid_2()
        inq = invoice2inquiry(inv)
        if not inq:
            return self.ack_inquiry_not_found()
        total_bayar = int(self.from_iso.get_value(4))
        total_tagihan = self.calc.total
        if total_bayar != total_tagihan:
            return self.ack_insufficient_fund(total_bayar, total_tagihan)
        inv.status_pembayaran_sppt = '1' # Lunas
        payment, bayar = self.create_payment(inq, total_bayar)
        if not payment:
            return self.ack_create_payment_failed()
        DBSession.add(inv)
        DBSession.add(bayar)
        DBSession.add(payment)
        self.setBit(47, str(payment.id))
        self.commit()

    def get_channel(self):
        return self.from_iso.get_value(18) # Merchant / Channel 

    def get_real_value(self, value):
        if type(value) is not DictType:
            return value
        if self.channel in value:
            return value[self.channel]
        if 'default' in value:
            return value['default']
        return '00'

    def bayar(self, inq, total_bayar):
        bayar = inq2bayar(inq)
        if bayar:
            ke = bayar.pembayaran_sppt_ke + 1
        else:
            ke = 1
        bayar = Pembayaran()
        bayar.kd_propinsi = inq.propinsi
        bayar.kd_dati2 = inq.kabupaten
        bayar.kd_kecamatan = inq.kecamatan
        bayar.kd_kelurahan = inq.kelurahan
        bayar.kd_blok = inq.blok
        bayar.no_urut = inq.urut
        bayar.kd_jns_op = inq.jenis
        bayar.thn_pajak_sppt = inq.tahun
        bayar.pembayaran_sppt_ke = ke
        bayar.tgl_rekam_byr_sppt = datetime.now()
        #bayar.tgl_pembayaran_sppt = inq.settlement
        bayar.tgl_pembayaran_sppt = self.from_iso.get_transaction_date() 
        bayar.jml_sppt_yg_dibayar = total_bayar 
        bayar.denda_sppt = inq.denda
        bayar.nip_rekam_byr_sppt = nip_rekam_byr_sppt
        bank_name = self.conf['name']
        conf = host[bank_name]
        for fieldname in FIELD_BANK:
            value = conf[fieldname]
            value = self.get_real_value(value)
            bayar.from_dict({fieldname: value})
        return bayar

    def create_payment(self, inq, total_bayar):
        bayar = self.bayar(inq, total_bayar)
        tp = ''
        d = bayar.to_dict()
        for fieldname in FIELD_BANK_NON_TP:
            tp += d[fieldname] or '00'
        payment_id = create_payment_id(tp)
        if not payment_id:
            return None, None
        payment = Payment(id=payment_id)
        payment.inquiry_id = inq.id
        payment.propinsi = inq.propinsi
        payment.kabupaten = inq.kabupaten
        payment.kecamatan = inq.kecamatan
        payment.kelurahan = inq.kelurahan
        payment.blok = inq.blok
        payment.urut = inq.urut
        payment.jenis = inq.jenis
        payment.tahun = inq.tahun
        payment.ke = bayar.pembayaran_sppt_ke
        for fieldname in FIELD_BANK:
            value = d[fieldname] or '00'
            payment.from_dict({fieldname: value})
        payment.kd_kanwil_bank = d['kd_kanwil']
        payment.kd_kppbb_bank = d['kd_kantor']
        payment.channel = self.channel
        payment.ntb = self.from_iso.get_value(48) # Nomor Transaksi Bank
        payment.iso_request = self.from_iso.getRawIso().upper()
        return payment, bayar

    ############
    # Reversal #
    ############
    def reversal_response(self):
        reversal_iso_request = self.from_iso.getRawIso().upper()
        pay_iso_request = '0200' + reversal_iso_request[4:]
        q = DBSession.query(Payment).filter_by(iso_request=pay_iso_request)
        pay = q.first()
        if not pay:
            return self.ack_payment_not_found()
        invoice_id = pay2invoice_id(pay)
        bayar = pay2bayar(pay)
        if not bayar:
            return self.ack_payment_not_found_2(invoice_id, pay.ke)
        sppt = pay2sppt(pay)
        if not sppt:
            return self.ack_not_available_2(invoice_id)
        if sppt.status_pembayaran_sppt != '1':
            return self.ack_invoice_open(invoice_id)
        sppt.status_pembayaran_sppt = '0'
        bayar.jml_sppt_yg_dibayar = 0
        bayar.denda_sppt = 0
        reversal = Reversal(payment=pay) # Catatan tambahan
        reversal.iso_request = self.from_iso.getRawIso().upper()
        self.settlement.set_raw(self.from_iso.get_value(13))
        DBSession.add(reversal)
        DBSession.add(bayar)
        DBSession.add(sppt)
        self.commit()

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
    def nama_kelurahan(self):
        return cari_kelurahan(
            self.invoice_id['Propinsi'],
            self.invoice_id['Kabupaten'],
            self.invoice_id['Kecamatan'],
            self.invoice_id['Kelurahan'])

    def nama_kecamatan(self):
        return cari_kecamatan(
            self.invoice_id['Propinsi'],
            self.invoice_id['Kabupaten'],
            self.invoice_id['Kecamatan'])

    def nama_propinsi(self):
        return cari_propinsi(self.invoice_id['Propinsi'])

    def commit(self):
        DBSession.flush()
        DBSession.commit()
        self.ack()

