# Penerjemahan file PDF Iso Spesification Pajak Daerah-BJB Ver 1.7

#################
# Redefine bits #
#################
NETWORK_BITS = {
     7: ['Transmission', 'Transmission Datetime', 'N', 10, 'n'],
    11: ['STAN', 'System Trace Audit Number', 'N', 6, 'n'],
    39: ['Response', 'Response Code', 'N', 2, 'n'],
    # 001: sign on, 002: sign off, 301: echo test
    70: ['Function', 'System Function Code', 'N', 3, 'n'],
    }

#########################
# Response Code, Bit 39 #
#########################
RC_OK = '00'
RC_OTHER_ERROR = '76'
