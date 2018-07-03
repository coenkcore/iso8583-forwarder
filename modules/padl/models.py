from base_models import IsoModel
from sqlalchemy import (
    Column,
    Integer,
    Text,
    ForeignKey,
    )


class Models(object):
    def __init__(self, Base):
        class IsoLog(Base, IsoModel):
            __tablename__ = 'iso_log'
            raw = Column(Text, nullable=False)
            request_id = Column(Integer, ForeignKey('iso_log.id'))
            bit002 = Column(Text)
            bit003 = Column(Text)
            bit004 = Column(Text)
            bit007 = Column(Text)
            bit011 = Column(Text)
            bit012 = Column(Text)
            bit013 = Column(Text)
            bit015 = Column(Text)
            bit018 = Column(Text)
            bit022 = Column(Text)
            bit032 = Column(Text)
            bit033 = Column(Text)
            bit035 = Column(Text)
            bit037 = Column(Text)
            bit038 = Column(Text)
            bit039 = Column(Text)
            bit041 = Column(Text)
            bit042 = Column(Text)
            bit043 = Column(Text)
            bit047 = Column(Text)
            bit048 = Column(Text)
            bit049 = Column(Text)
            bit059 = Column(Text)
            bit060 = Column(Text)
            bit061 = Column(Text)
            bit062 = Column(Text)
            bit063 = Column(Text)
            bit102 = Column(Text)
            bit107 = Column(Text)
 
        self.IsoLog = IsoLog
