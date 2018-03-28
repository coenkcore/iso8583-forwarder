from datetime import date


def bulan_tunggakan(jatuh_tempo, tgl_hitung):
    x = (tgl_hitung.year - jatuh_tempo.year) * 12
    y = tgl_hitung.month - jatuh_tempo.month
    n = x + y + 1
    if tgl_hitung.day <= jatuh_tempo.day:
        n -= 1
    if n < 1:
        n = 0
    if n > 24:
        n = 24
    return n


def hitung_denda(tagihan, jatuh_tempo, persen_denda, tgl_hitung=None):
    if jatuh_tempo is None:
        return 0, 0
    if tgl_hitung is None:
        tgl_hitung = date.today()
    if type(jatuh_tempo) is not date:
        jatuh_tempo = jatuh_tempo.date()
    if jatuh_tempo >= tgl_hitung or persen_denda <= 0:
        return 0, 0
    bulan = bulan_tunggakan(jatuh_tempo, tgl_hitung)
    denda = bulan * float(persen_denda) / 100 * tagihan
    return bulan, denda
