from tools import DbTransactionID
from sismiop.tools import sppt2nop
from sismiop.query import Query as SismiopQuery


class NTP(DbTransactionID):
    def is_found(self, trx_id):
        q = self.DBSession.query(self.models.Payment).filter_by(id=trx_id)
        return q.first()


class Query(SismiopQuery):
    def inquiry_id(self):
        return self.models.InquirySeq.next_value()

    def create_inquiry(self, calc, from_iso, persen_denda):
        inv = calc.invoice
        inq_id = self.inquiry_id()
        nop = sppt2nop(inv)
        inq = self.models.Inquiry(id=inq_id, nop=nop, propinsi=inv.kd_propinsi,
                kabupaten=inv.kd_dati2, kecamatan=inv.kd_kecamatan,
                kelurahan=inv.kd_kelurahan, blok=inv.kd_blok, urut=inv.no_urut,
                jenis=inv.kd_jns_op, tahun=inv.thn_pajak_sppt,
                tgl=calc.kini)
        inq.stan = from_iso.get_stan()
        inq.pengirim = from_iso.get_forwarder()
        inq.transmission = from_iso.get_transmission()
        inq.settlement = from_iso.get_settlement()
        inq.tagihan = calc.tagihan
        inq.denda = calc.denda
        inq.persen_denda = persen_denda
        inq.jatuh_tempo = inv.tgl_jatuh_tempo_sppt
        inq.bulan_tunggakan = calc.bln_tunggakan
        self.DBSession.add(inq)
        self.DBSession.flush()
        return inq

    def create_payment(self, inq, total_bayar, urutan_bayar, prefix_ntp,
            bank_fields, from_iso):
        payment_id = self.create_ntp(prefix_ntp)
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
        payment.ke = urutan_bayar 
        payment.channel = from_iso.get_channel()
        payment.ntb = from_iso.get_ntb()
        payment.iso_request = ISO8583.getRawIso(self.from_iso).upper()
        return payment, bayar

    def create_ntp(self, prefix):
        generator = NTP(self.models, self.DBSession)
        return generator.create(prefix)

    def invoice2inquiry(self, sppt):
        q = self.DBSession.query(self.models.Inquiry).filter_by(
                propinsi=sppt.kd_propinsi, kabupaten=sppt.kd_dati2,
                kecamatan=sppt.kd_kecamatan, kelurahan=sppt.kd_kelurahan,
                blok=sppt.kd_blok, urut=sppt.no_urut, jenis=sppt.kd_jns_op,
                tahun=sppt.thn_pajak_sppt)
        q = q.order_by(self.models.Inquiry.id.desc())
        return q.first()
