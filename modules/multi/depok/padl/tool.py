def decode_invoice_id_raw(raw):
    tahun = raw[:4]
    sptno = raw[4:]
    return tahun, sptno.strip()
