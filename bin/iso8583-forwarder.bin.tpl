#!/bin/sh
home="/home/$user"
su - "$user" -c "sh $home/bin/start-iso8583-forwarder"
log_file="$dir/log/iso8583-forwarder-bppt-tangsel"
tmp_file="$dir/tmp/iso8583-forwarder-bppt-tangsel.pid"
cd "$dir"/iso8583-forwarder
/c/env/Scripts/python iso8583-forwarder.py --pid-file="$tmp_file" --log-dir="$og_file" "$@"
