from common.transaction.structure import BASE_TRANSACTION_BITS


TRANSACTION_BITS = BASE_TRANSACTION_BITS.copy()
TRANSACTION_BITS.update({
    47: ['NTPD', 'Nomor Transaksi Pendapatan Daerah', 'LLL', 999, 'n'],
    49: ['Currency', 'Transaction Currency Code', 'N', 3, 'n'],
    61: ['Invoice ID', 'Invoice ID', 'LLL', 999, 'ans'],
    62: ['Error', 'Error Message', 'LLL', 999, 'ans'],
    })
