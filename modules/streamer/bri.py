from tcp import Streamer as BaseStreamer

# 3 byte pertama ISO 
# 9 byte terakhir numerik 
# Contoh: ISO011000017
# Network header BRI tidak memuat size data, praktis
# setiap request dianggap sebuah transaksi.
class Streamer(BaseStreamer):
    # Override Stremer.get
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
