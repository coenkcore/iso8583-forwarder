from test_payment import (
    Payment,
    PaymentTest,
    BcaDbTransaction,
    )
from bca_structure import RC_OK



class Reversal(Payment):
    def reversal_request(self, pay_req_iso):
        self.copy(from_iso=pay_req_iso)
        self.setMTI('0400')
 

class ReversalTest(PaymentTest):
    def request(self):
        pay_resp_iso, pay_req_iso = PaymentTest.request(self)
        if pay_resp_iso.getBit(39) != RC_OK:
            return
        print('Bank kirim reversal request')
        req_iso = Reversal()
        #pay_req_iso = '0400F23A4401A8E1803E00000000042000001420160319200731541019000000000237031920073120073120073103190319601002103110050011000000000200731000000000000000000000000000000000000000000000000000000NAMA BANK01420160319200731390003PAY00314202232777110020060219020062653277711002006021902006IKIN TINI                          KP GOBANG                          SINGKUP                            PURBARATU                          JAWA BARAT                         0000000002200000000000353108200700000000016000000000007700000000023700000000'
        req_iso.reversal_request(pay_req_iso)
        raw = self.get_raw(req_iso)
        print('Pemda terima reversal request')
        from_iso = BcaDbTransaction()
        from_iso.setIsoContent(raw)
        print('Pemda kirim reversal response')
        resp_iso = BcaDbTransaction(from_iso=from_iso, conf=self.conf)
        func = getattr(resp_iso, from_iso.get_func_name())
        func()
        self.get_raw(resp_iso)



if __name__ == '__main__':
    import sys
    from pprint import pprint
    from optparse import OptionParser
    from bca_conf import host

    invoice_id = '3278009008003035002006'
    streamer_name = 'bjb_with_suffix'

    pars = OptionParser()
    pars.add_option('-i', '--invoice-id', default=invoice_id,
            help='Invoice ID, default: ' + invoice_id)
    pars.add_option('', '--streamer-name', default=streamer_name,
        help='Nama modul streamer, digunakan saat --raw, default: %s' % streamer_name)
    option, remain = pars.parse_args(sys.argv[1:])

    streamer_name = option.streamer_name
    conf = {'ip': '127.0.0.1',
            'name': streamer_name}
    conf.update(host[streamer_name])
    test = ReversalTest(option.invoice_id, conf)
    test.request()
