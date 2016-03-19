import json
from models import (
    DBSession,
    Log,
    LogValues,
    )
from tools import create_now


def save_iso_log(ip, iso, kirim, ref_id=None):
    def void(self):
        pass
    iso.log_info = void # Agar tidak tulis log lagi saat getRawIso()
    raw = iso.getRawIso()
    log = Log()
    log.jenis_id = 1
    log.tgl = create_now() 
    log.method = iso.getMTI()
    log.ip = ip 
    log.raw = raw
    log.kirim = kirim
    log.ref_id = ref_id
    DBSession.add(log)
    DBSession.flush()
    values = iso.get_values()
    for bit in values:
        log_val = LogValues()
        log_val.ref_id = log.id
        log_val.key = bit
        log_val.value = values[bit]
        DBSession.add(log_val)
    DBSession.flush()
    DBSession.commit()
    return log.id

def save_rpc_log(ip, method, values, kirim, ref_id=None):
    log = Log()
    log.jenis_id = 2
    log.tgl = create_now() 
    log.method = method 
    log.ip = ip 
    log.raw = json.dumps(values) 
    log.kirim = kirim
    log.ref_id = ref_id
    DBSession.add(log)
    DBSession.flush()
    for key in values: 
        log_val = LogValues()
        log_val.ref_id = log.id
        log_val.key = key 
        log_val.value = values[key]
        DBSession.add(log_val)
    DBSession.flush()
    DBSession.commit()
    return log.id
