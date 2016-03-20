import sys
from pprint import pprint
from time import sleep


class Test(object):
    def get_raw(self, iso):
        msg = 'MTI {mti}'.format(mti=iso.getMTI())
        print(msg)
        pprint(iso.getBitsAndValues())
        raw = iso.getRawIso()
        sleep(1)
        print([raw])
        return raw


def get_streamer_module(name):
    modules_path = '/usr/share/opensipkd-forwarder/modules/streamer'
    sys.path[0:0] = [modules_path]
    return __import__(name)
