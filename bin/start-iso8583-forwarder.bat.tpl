set folder="c:\pydata\apps"
set log_file="%folder%\log\iso8583-forwarder-bppt-tangsel"
set tmp_file="%folder%\tmp\iso8583-forwarder-bppt-tangsel.pid"
cd %folder%\iso8583-forwarder-github
python iso8583-forwarder.py --pid-file=%tmp_file% --log-dir=%og_file% %*
