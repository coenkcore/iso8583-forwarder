import os
from tools import FromCSV
from base_models import (
    Base,
    DBSession,
    )
from DbTransaction import (
    engine,
    models,
    )


def realpath(filename):
    this_file = os.path.realpath(__file__)
    t = os.path.split(this_file)
    dir_name = t[0]
    return os.path.join(dir_name, filename)

def setup():
    engine.echo = True
    Base.metadata.create_all()
    from_csv = FromCSV(Base, DBSession)
    from_csv.restore(realpath('izin.csv'), models.Izin)
    from_csv.restore(realpath('channel.csv'), models.Channel)
    from DbTransaction import OtherBase
    OtherBase.metadata.create_all()
