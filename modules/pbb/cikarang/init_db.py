import os
from base_models import (
    Base,
    DBSession,
    )


def realpath(filename):
    this_file = os.path.realpath(__file__)
    t = os.path.split(this_file)
    dir_name = t[0]
    return os.path.join(dir_name, filename)


def setup():
    Base.metadata.bind.echo = True
    Base.metadata.create_all()
