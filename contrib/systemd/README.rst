Autostart Script untuk SystemD
==============================

SystemD hadir sejak Debian 8. Letakkan file ``iso8583-forwarder.service`` di
direktori ``/lib/systemd/system/`` dan sesuaikan isinya. Lalu jalankan::

  sudo systemctl enable iso8583-forwarder.service
  sudo systemctl start iso8583-forwarder.service

Selanjutnya pantau log file apakah ia bekerja dengan baik.
