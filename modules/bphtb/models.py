from sqlalchemy import (
    Column,
    Text,
    Integer,
    ForeignKey,
    )
from base_models import (
    Base,
    IsoModel,
    )


class Iso(Base, IsoModel):
    __tablename__ = 'iso_log'
    raw = Column(Text, nullable=False)
    request_id = Column(Integer, ForeignKey('iso_log.id'))
    payment_id = Column(Integer)
    bit_002 = Column(Text)
    bit_003 = Column(Text)
    bit_004 = Column(Text)
    bit_007 = Column(Text)
    bit_011 = Column(Text)
    bit_012 = Column(Text)
    bit_013 = Column(Text)
    bit_015 = Column(Text)
    bit_018 = Column(Text)
    bit_022 = Column(Text)
    bit_032 = Column(Text)
    bit_033 = Column(Text)
    bit_035 = Column(Text)
    bit_037 = Column(Text)
    bit_038 = Column(Text)
    bit_039 = Column(Text)
    bit_041 = Column(Text)
    bit_042 = Column(Text)
    bit_043 = Column(Text)
    bit_047 = Column(Text)
    bit_048 = Column(Text)
    bit_049 = Column(Text)
    bit_057 = Column(Text)
    bit_058 = Column(Text)
    bit_059 = Column(Text)
    bit_060 = Column(Text)
    bit_061 = Column(Text)
    bit_062 = Column(Text)
    bit_063 = Column(Text)
    bit_102 = Column(Text)
    bit_107 = Column(Text)
