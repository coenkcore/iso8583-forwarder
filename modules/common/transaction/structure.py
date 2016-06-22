# Penerjemahan file PDF Iso Spesification Pajak Daerah-BJB Ver 1.7

from network.structure import NETWORK_BITS

#################
# Redefine bits #
#################
BASE_TRANSACTION_BITS = NETWORK_BITS.copy()
BASE_TRANSACTION_BITS.update({
     2: ['PAN', 'Primary Account Number', 'LL', 2+97, 'n'],
     3: ['Processing', 'Processing Code', 'N', 6, 'n'], # '341019'
     4: ['Amount', 'Amount Transaction', 'N', 12, 'n'],
     7: ['Transmission', 'Transmission Datetime', 'N', 10, 'n'],
    11: ['STAN', 'System Trace Audit Number', 'N', 6, 'n'],
    12: ['Time', 'Time Local Transaction', 'N', 6, 'n'],
    13: ['Date', 'Date Local Transaction', 'N', 4, 'n'],
    15: ['Settlement', 'Settlement Date', 'N', 4, 'n'],
    18: ['Merchant', 'Merchant Type', 'N', 4, 'n'],
    22: ['POS', 'POS Entry Mode Code', 'N', 3, 'n'], # '021'
    32: ['Acquiring', 'Acquiring Institution Code', 'LL', 2+97, 'n'], # '110'
    33: ['Forwarding', 'Forwarding Institution ID Code', 'LL', 2+97, 'n'], # '00110'
    35: ['Track', 'Track 2 Data', 'LL', 2+97, 'n'],
    37: ['Sequence', 'Sequence Number', 'N', 12, 'n'],
    39: ['Response', 'Response Code', 'N', 2, 'n'],
    41: ['Terminal', 'Terminal Identification Number', 'N', 8, 'ans'],
    42: ['User', 'Terminal Name / User Identification', 'N', 15, 'ans'],
    43: ['Card', 'Card Acceptor Name / Location', 'ANS', 40, 'ans'],
    })

ERR_SETTLEMENT_DATE = 'Settlement date {raw} tidak benar'
ERR_TRANSACTION_DATETIME = 'Transaction datetime {raw} tidak benar'
ERR_TRANSACTION_DATE = 'Transaction date {raw} tidak benar'
ERR_TRANSACTION_TIME = 'Transaction time {raw} tidak benar'
