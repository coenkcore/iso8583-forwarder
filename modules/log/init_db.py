import sys
import os
from sqlalchemy import (
    create_engine,
    Table,
    )
from sqlalchemy.sql import text
from sqlalchemy_views import CreateView
from tools import FromCSV
from base_models import (
    Base,
    DBSession,
    )
from pbb.structure import TRANSACTION_BITS
from .models import (
    Kategori,
    Jenis,
    Log,
    Iso,
    Conf,
    )
from .conf import db_url


BASE_VIEW = "SELECT log_iso.id, log.tgl, forwarder, ip, mti, is_send, {bits} "\
        "FROM log_iso, log "\
        "WHERE log_iso.id = log.id AND log.jenis_id = {jenis}"
PBB_BITS = list(TRANSACTION_BITS.keys())
PBB_BITS.sort()
bit_fields = []
for bit in PBB_BITS:
    field = 'bit_' + str(bit).zfill(3)
    bit_fields.append(field)
PBB_VIEW = BASE_VIEW.format(bits=', '.join(bit_fields), jenis=1)


def realpath(filename):
    this_file = os.path.realpath(__file__)
    t = os.path.split(this_file)
    dir_name = t[0]
    return os.path.join(dir_name, filename)


def main(argv):
    engine = create_engine(db_url)
    engine.echo = True
    Base.metadata.bind = engine
    Base.metadata.create_all()
    from_csv = FromCSV(Base, DBSession)
    from_csv.restore(realpath('kategori.csv'), Kategori)
    from_csv.restore(realpath('jenis.csv'), Jenis)
    from_csv.restore(realpath('conf.csv'), Conf)
    view = Table('v_pbb', Base.metadata)
    definition = text(PBB_VIEW)
    create_view = CreateView(view, definition, or_replace=True)
    engine.execute(create_view)
