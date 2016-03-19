from tcp import Streamer as BaseStreamer

#Size Nama              Keterangan
# 3   Prefix            ISO
# 2   Product Indicator Kode produk standard paket data yang digunakan. Nilai
#                       yang diperbolehkan adalah 04.
# 2   Release Number    Release number dari produk paket data SPO yang digunakan.
#                       Nilainya adalah 10. 
# 3   Status            Untuk menginformasikan masalah yang timbul pada saat
#                       interpretasi paket data yang diterima. Bilamana sebuah
#                       paket data ditolak oleh Sistem SPO, maka Sistem SPO akan
#                       menuliskan kode bit map dari paket data yang ditolak dan
#                       akan mengirimkan kembali paket data ini ke Host Bank.
#                       Kemudian pada kode pengenal paket data (MTI) pada bit
#                       pertama akan diganti dengan 9.
#                       Contoh : request 0200 -> response 9200
# 1   Originator Code   Kode entity pengirim paket data. Nilainya adalah
#                       1 : Semua paket data (kecuali Network Mgt).
#                       6 : Network Management Message
# 1   Responder Code    Kode entity yang memberikan tanggapan terhadap sebuah
#                       paket data. Nilainya adalah:
#                       7 : Interchange (Sistem SPO).
#
#Contoh saat digabungkan : ISO041000017

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
        header = 'ISO0410000'
        if raw[:2] == '08':
            header += '6'
        else:
            header += '1'
        header += '7'
        return header + raw
