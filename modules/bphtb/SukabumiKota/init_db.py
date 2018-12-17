from sqlalchemy import create_engine
from base_models import Base
from config import db_url
from ..models import Iso


def setup():
    engine = create_engine(db_url)
    engine.echo = True
    Base.metadata.create_all(engine)
