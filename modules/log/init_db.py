import sys
import os
from sqlalchemy import create_engine
from tools import FromCSV
from base_models import (
    Base,
    DBSession,
    )
from .models import (
    Kategori,
    Jenis,
    Log,
    Iso,
    Conf,
    )
from .conf import db_url


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
