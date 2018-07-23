db_url = 'postgresql://user:pass@localhost/dbname'

# Daftar modul yang akan dibuatkan view.
from pbb.structure import TRANSACTION_BITS as PBB_BITS
from pkb.structure import TRANSACTION_BITS as PKB_BITS

views = [
    (PBB_BITS, 1, 'v_pbb'),
    (PKB_BITS, 6, 'v_pkb'),
    ]

#duplicate_key_message = 'duplicate key'
duplicate_key_message = 'nilai kunci ganda'
