from datetime import datetime
import hmac
import hashlib
import base64
from random import choice
import requests
import json
from string import (
    ascii_uppercase,
    ascii_lowercase,
    digits,
)
LIMIT = 1000
CODE_OK = 0
MSG_OK = 'Data Submitted'

begin_unix_time = datetime(1970, 1, 1)


# http://stackoverflow.com/questions/2257441/random-string-generation-with-upper-case-letters-and-digits-in-python
def get_random_string(width=6):
    return ''.join(choice(ascii_uppercase + ascii_lowercase + digits) \
                   for _ in range(width))


def get_random_number(width=12):
    return ''.join(choice(digits) \
                   for _ in range(width))

def get_seconds():
    durasi = datetime.utcnow() - begin_unix_time
    return int(durasi.total_seconds())


# fungsi ini digunakan untuk membuat header dan authentikasi pada rpc client
def json_rpc_header(userid, password, time_stamp=None):
    if not time_stamp:
        time_stamp = str(get_seconds())
    value = '&'.join([str(userid), str(time_stamp)])
    password = str(password)
    signature = hmac.new(password, msg=value, digestmod=hashlib.sha256).digest()
    encoded_signature = base64.encodestring(signature).replace('\n', '')
    return dict(userid=userid, signature=encoded_signature, key=time_stamp)


# fungsi ini digunakan untuk membuat data yang akan dikirim ke server
def get_jsonrpc(method, params):
    return dict(jsonrpc='2.0', method=method, params=params, id=get_random_number(6))


def send_rpc(userid, password, url, method, message):
    headers = json_rpc_header(userid, password)
    params = dict(data=message)
    data = get_jsonrpc(method, params)
    jsondata = json.dumps(data, ensure_ascii=False)
    results = requests.post(url, data=jsondata, headers=headers)
    rows = json.loads(results.text)
    return rows

    