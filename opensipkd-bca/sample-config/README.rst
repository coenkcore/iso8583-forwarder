Konfigurasi
===========

Salin salah satu file konfigurasi ke direktori ``/etc/opensipkd`` dan namai dengan
``pbb_conf.py``, sesuaikan dengan wilayahnya, contoh::

  cp /usr/share/doc/opensipkd-pbb/sample-config/pbb_conf.py.depok /etc/opensipkd/pbb_conf.py

Sesuaikan ``db_url`` dan lakukan konfigurasi::

  dpkg-reconfigure opensipkd-pbb

Lalu restart daemon-nya::

  service iso8583-forwarder restart

dan pantau log-nya::

  tail -f /var/log/iso8583-forwarder/main.log

Jika ada daerah yang belum ada file konfigurasinya silahkan email ke
``cs@opensipkd.com``.
