from pbb.test_payment import TestPayment as BaseTest
from .test_inquiry import DbTransaction


class TestPayment(BaseTest):
    def get_iso_cls(self):
        return DbTransaction


def main(argv):
    test = TestPayment(argv)
    test.run()
