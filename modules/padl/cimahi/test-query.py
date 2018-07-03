import sys
from optparse import OptionParser
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from other_query import Query
from conf import other_db_url


default_bank_id = 110
help_bank_id = 'default {}'.format(default_bank_id)
help_inquiry = 'default, butuh --invoice-id'
help_payment = 'butuh --invoice-id'
help_reversal = 'butuh --ntp'

pars = OptionParser()
pars.add_option('', '--inquiry', action='store_true', help=help_inquiry) 
pars.add_option('', '--payment', action='store_true', help=help_payment) 
pars.add_option('', '--invoice-id')
pars.add_option('', '--reversal', action='store_true', help=help_reversal)
pars.add_option('', '--ntp', help='Nomor Transaksi Pemda')
pars.add_option(
    '', '--bank-id', default=default_bank_id, type='int', help=help_bank_id)
option, remain = pars.parse_args(sys.argv[1:])

bank_id = str(option.bank_id)

engine = create_engine(other_db_url)
session_factory = sessionmaker(bind=engine)
DBSession = session_factory()
query = Query(DBSession, bank_id)

if option.payment:
    result = query.payment(option.invoice_id)
    if result.other_2 == '0':
        print('Pembayaran gagal karena sudah dibayar.')
    elif result.other_2 == '2':
        print('Pembayaran gagal karena Nomor Transaksi Pemda gagal dibuat.')
    else:
        print('Pembayaran berhasil, Nomor Transaksi Pemda {n}'.format(
            n=result.other_2))
elif option.reversal:
    result = query.reversal(option.ntp)
    if result.other_2 == '1':
        print('Pembatalan berhasil.')
    elif result.other_2 == '2':
        print('Pembatalan gagal karena identitas bank berbeda dengan '\
              'transaksi.')
    elif result.other_2 == '0':
        print('Pembatalan gagal karena memang belum dibayar atau data '\
              'tidak ditemukan.')
    else:
        print('other_2 bernilai {}, belum dipahami.'.format(result.other_2))
else:
    result = query.inquiry(option.invoice_id)
    if 'Tagihan' in result:
        print('Tagihan ditemukan.')
    elif result.other_2 == '0':
        print('Data tidak ditemukan.')
    else:
        print('other_2 bernilai {}, belum dipahami.'.format(result.other_2))
