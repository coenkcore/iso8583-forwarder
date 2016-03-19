from tcp import Streamer as BaseStreamer

# 4 byte pertama adalah raw length
# Karakter terakhir adalah hexa 03
# Dalam 1 request bisa saja ada 2 transaksi, bahkan
# bisa saja string transaksi yang belum lengkap
class Streamer(BaseStreamer):
    # Override Stremer.get
    def get(self, raw):
        if self.size:
            size = self.size - len(self.raw)
        else:
            raw = self.raw + raw
            if len(raw) < 4:
                self.raw = raw
                return
            size = self.size = int(raw[:4])
            self.raw = ''
            raw = raw[4:]
        self.raw += raw[:size]
        if len(self.raw) == self.size:
            raw_iso = self.raw
            self.size = 0
            self.raw = raw[size:] # Sisa
            return raw_iso[:-1] # Hapus karakter terakhir hexa 03
        self.raw += raw[size:]

    # Override Stremer.set
    def set(self, raw):
        raw += '\x03'
        size = str(len(raw)).zfill(4)
        return size + raw
