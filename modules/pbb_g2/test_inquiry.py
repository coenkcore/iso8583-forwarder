from pbb.test_inquiry import TestInquiry as BaseTest
from .conf import module_name


name = '.'.join(['pbb_g2', module_name])
module = __import__(name)
area_module = getattr(module, module_name)
DbTransaction = area_module.DbTransaction


class TestInquiry(BaseTest):
    def get_iso_cls(self):
        return DbTransaction


def main(argv):
    test = TestInquiry(argv)
    test.run()
