cd /home/h2h/iso8583-forwarder
/home/h2h/env/bin/python iso8583-forwarder.py \
    -p /home/h2h/tmp/iso8583-forwarder.pid \
    -c conf/forwarder.py \
    -l /home/h2h/log \
    $@
