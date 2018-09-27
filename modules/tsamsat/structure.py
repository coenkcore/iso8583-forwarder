from network.structure import NETWORK_BITS


TRANSACTION_BITS = NETWORK_BITS.copy()

#################
# Redefine bits #
#################
TRANSACTION_BITS = NETWORK_BITS.copy()
TRANSACTION_BITS.update({
    2: ['PAN', 'Primary Account Number', 'LL', 99, 'n'],
    3: ['Processing', 'Processing Code', 'N', 6, 'n'], # 301099 / 501099
    4: ['Amount', 'Amount Transaction', 'N', 12, 'n'],
    12: ['Time', 'Time Local Transaction', 'N', 6, 'n'],
    13: ['Date', 'Date Local Transaction', 'N', 4, 'n'],
    15: ['Settlement', 'Settlement Date', 'N', 4, 'n'],
    18: ['Merchant', 'Merchant Type', 'N', 4, 'n'],  # 6010 Teller, 6011 ATM
    22: ['POS', 'POS Entry Mode Code', 'N', 3, 'n'], # '021'
    32: ['Acquiring', 'Acquiring Institution Code', 'LL', 99, 'n'], # '110'
    33: ['Forwarding', 'Forwarding Institution ID Code', 'LL', 99, 'n'], # '00110'
    35: ['Track', 'Track 2 Data', 'LL', 99, 'n'],
    37: ['Sequence', 'Sequence Number', 'N', 12, 'n'],
    39: ['Response Code', 'Response Code', 'N', 2, 'n'],
    41: ['Terminal', 'Terminal Identification Number', 'ANS', 8, 'ans'],
    43: ['Card', 'Card Acceptor Name / Location', 'ANS', 40, 'ans'],
    47: ['NTPD', 'Nomor Transaksi Pendapatan Daerah', 'LLL', 999, 'n'],
    49: ['Currency', 'Transaction Currency Code', 'N', 3, 'n'],
    60: ['Additional Data', 'Additional Data', 'LLL', 999, 'ans'],
    61: ['Invoice ID', 'Invoice ID', 'LLL', 999, 'ans'],
    62: ['Error', 'Error Message', 'LLL', 999, 'ans'],
    })

    
##########################
# Bit 3 to name function #
##########################
INQUIRY_CODE = '301098'
PAYMENT_CODE = '501098'
