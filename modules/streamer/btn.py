from tcp import Streamer as BaseStreamer

# 4 byte pertama adalah raw length
class Streamer(BaseStreamer):
    def get_size(self, raw):
        return int(raw[:4])

    # Override Stremer.get
    def get(self, raw):
        if self.size:
            size = self.size - len(self.raw)
        else:
            raw = self.raw + raw
            if len(raw) < 4:
                self.raw = raw
                return
            size = self.size = self.get_size(raw)
            self.raw = ''
            raw = raw[4:]
        self.raw += raw[:size]
        if len(self.raw) == self.size:
            raw_iso = self.raw
            self.size = 0
            self.raw = raw[size:] # Sisa
            return raw_iso
        self.raw += raw[size:]

    # Override Stremer.set
    def set(self, raw):
        size = str(len(raw)).zfill(4)
        return size + raw
