#!/bin/sh
dir=$PWD"/.."
log_file="$dir/log/iso8583-forwarder-bppt-tangsel"
tmp_file="$dir/tmp/iso8583-forwarder-bppt-tangsel.pid"
cd "$dir"/iso8583-forwarder
/c/env/Scripts/python iso8583-forwarder.py --pid-file="$tmp_file" --log-dir="$og_file" "$@"
