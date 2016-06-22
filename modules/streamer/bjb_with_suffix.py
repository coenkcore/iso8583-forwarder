from streamer.bjb import Streamer as BaseStreamer

# 4 byte pertama adalah raw length
# Karakter terakhir adalah hexa 03
class Streamer(BaseStreamer):
    # Override Stremer.get
    def get(self, raw):
        raw_iso = BaseStreamer.get(self, raw)
        if raw_iso:
            return raw_iso[:-1] # Hapus karakter terakhir hexa 03

    # Override Stremer.set
    def set(self, raw):
        raw += '\x03'
        return BaseStreamer.set(self, raw)
