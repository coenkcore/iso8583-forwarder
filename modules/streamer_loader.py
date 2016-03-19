import os
MODULES_PATH = os.path.split(__file__)[0]
import imp


def get_streamer_module(name):
    filename = os.path.join(MODULES_PATH, 'streamer', name) + '.py'
    if not os.path.exists(filename):
        raise Exception('Module file %s not found' % filename)
    print('Load streamer module from %s' % filename)
    return imp.load_source(name, filename)
