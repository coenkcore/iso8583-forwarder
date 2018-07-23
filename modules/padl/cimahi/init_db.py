from base_models import Base
from DbTransaction import (
    engine,
    models,
    )


def setup():
    engine.echo = True
    Base.metadata.create_all()
