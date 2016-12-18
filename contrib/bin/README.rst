Shell Script
============

Tujuan pembuatan shell script ini adalah memudahkan user root menjalankan
``iso8583-forwarder.py`` sebagai user biasa.

Letakkan ``iso8583-forwarder.sh`` di direktori ``/home/sugiana/bin``.
Sesuaikanlah nama direktorinya. Lalu letakkan ``iso8583-forwarder`` di
``/usr/local/bin/`` dan lakukan ``chmod 755`` agar *executable*. Sesuaikan
juga isinya.

Lalu jalankan::

  sudo iso8583-forwarder

Pastikan tidak ada pesan kesalahan. Setelah ini lanjut baca
``systemd/README.rst`` jika memang systemd terpasang sebagaimana yang ada di
Debian 8.
