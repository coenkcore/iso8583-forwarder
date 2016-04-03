import sys
from common import Test
sys.path[0:0] = ['/usr/share/opensipkd-forwarder/modules/multi']
from multi_network import Network


class NetworkTest(Test):
    def echo_test(self):
        print('Pemda kirim echo test request')
        req_iso = Network()
        req_iso.echo_test_request()
        raw = self.get_raw(req_iso)
        print('Bank terima echo test request')
        from_iso = Network()
        from_iso.setIsoContent(raw)
        print('Bank kirim echo test response')
        resp_iso = Network(from_iso=from_iso)
        resp_iso.echo_test_response()
        func = getattr(resp_iso, from_iso.get_func_name())
        func()
        self.get_raw(resp_iso)

    def sign_on(self):
        print('Pemda kirim sign on request')
        req_iso = Network()
        req_iso.sign_on_request()
        raw = self.get_raw(req_iso)
        print('Bank terima sign on request')
        from_iso = Network()
        from_iso.setIsoContent(raw)
        print('Bank kirim sign on response')
        resp_iso = Network(from_iso=from_iso)
        resp_iso.sign_on_response()
        func = getattr(resp_iso, from_iso.get_func_name())
        func()
        self.get_raw(resp_iso)

    def sign_off(self):
        print('Pemda kirim sign off request')
        req_iso = Network()
        req_iso.sign_off_request()
        raw = self.get_raw(req_iso)
        print('Bank terima sign off request')
        from_iso = Network()
        from_iso.setIsoContent(raw)
        print('Bank kirim sign off response')
        resp_iso = Network(from_iso=from_iso)
        resp_iso.sign_off_response()
        func = getattr(resp_iso, from_iso.get_func_name())
        func()
        self.get_raw(resp_iso)


if __name__ == '__main__':
    test = NetworkTest()
    test.echo_test()
    test.sign_on()
    test.sign_off()
