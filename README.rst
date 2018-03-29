ISO8583 Forwarder
=================
ISO8583 adalah format transaksi perbankan. Aplikasi ini merupakan `daemon`-nya
dengan fitur:

- Multi client, dapat membuka koneksi ke beberapa server.
- Multi server, dapat listen di beberapa port.
- Multi streamer, dapat menangani berbagai network header.
- Multi modul, contoh: pbb, bphtb, padl, dan multi.


Jika OS belum mendukung systemd tambahkan parameter --service

Buatlah file konfigurasinya terlebih dahulu, misalnya
``conf/forwarder-bogor-kota.py``::

    host = {
        'btn': {
            'module': 'multi',
            'streamer': 'btn',
            'ip': '127.0.0.1',
            'port': 8593',
            'listen': True,
            'need echo': False,
            },
        }

Key ``module`` di atas mengacu ke modul Python yang berada di direktori
``modules``. Sedangkan key ``streamer`` mengacu ke direktori
``modules/streamer``. Bila ``listen`` bernilai ``True`` berarti sebuah
`thread` server akan dihidupkan sesuai nilai ``port``. Bila ``False``
maka `thread` client akan dihidupkan sesuai nilai ``ip`` dan ``port``.

Modul multi
-----------
Ini merupakan modul yang dapat melakukan transaksi untuk berbagai jenis pajak
seperti PBB dan BPHTB. Ia memiliki konfigurasi utama pada
``modules/multi/conf.py`` yang hanya berisi satu baris::

    module_name = 'BogorKota'

Konfigurasi selanjutnya berada di:

- modules/multi/BogorKota/pbb/conf.py
- modules/multi/BogorKota/bphtb/conf.py
- modules/multi/BogorKota/padl/conf.py

Sesuaikanlah.

Pengujian
---------
Sebelum daemon dijalankan sebaiknya dicoba terlebih dahulu. Dapatkanlah tagihan
yang belum dibayar::

    python available-invoice multi pbb

Kemudian lakukan inquiry (cek tagihan)::

    python test-inquiry.py multi -m pbb -i 3271010005010005302016

Pastikan bit 39 bernilai ``00``. Kemudian lakukan payment (pembayaran)::

    python test-payment.py multi -m pbb -i 3271010005010005302016

Sebenarnya uji payment sekaligus menguji inquiry.

Daemon
------
Sebaiknya jalankan daemon sebagai user biasa, tidak harus root::

    python iso8583-forwarder.py -c conf/forwarder-bogor-kota.py \
        -p bogor-kota.pid -l logs

Opsi ``-l`` berisi direktori logs. Jika belum ada maka otomatis akan dibuat.
Saat `foreground mode` seperti contoh di atas maka isi `log file` akan
terlihat. Jika nanti Anda menjalankannya dengan `background mode` maka gunakan
``tail`` untuk memantau::

    tail -f logs/main.log

Instalasi
===================
Jalan file install.py
Masuk ke folder iso8583-forwarder
#python install.py -m module_name -s sub_module -u user 

Selamat mencoba.