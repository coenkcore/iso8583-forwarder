from pbb.test_reversal import TestReversal as BaseTest
from .test_inquiry import DbTransaction


class TestReversal(BaseTest):
    def get_iso_cls(self):
        return DbTransaction


def main(argv):
    test = TestReversal(argv)
    test.run()
