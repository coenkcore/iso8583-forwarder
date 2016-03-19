from tcp import Streamer as BaseStreamer

# 2 byte pertama size
# Dalam 1 request bisa saja ada 2 transaksi, bahkan
# bisa saja string transaksi yang belum lengkap
class Streamer(BaseStreamer):
    def __init__(self, *args, **kwargs):
        BaseStreamer.__init__(self, *args, **kwargs)
        self.header = None

    def get(self, raw):
        self.header = raw[:12]
        self.raw = raw[12:]
        return self.raw

    def set(self, raw):
        header = self.header or 'ISO'.ljust(12, '0')
        return header + raw