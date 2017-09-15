from datetime import datetime
from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
    select,
    func,
    Column,
    Integer,
    DateTime,
    String,
    Boolean,
    Text,
    )
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )
from tools import (
    extract_db_url,
    eng_profile,
    as_timezone,
    create_now,
    )


Base = declarative_base()
session_factory = sessionmaker()
DBSession = scoped_session(session_factory) 


class DBProfile(object):
    def __init__(self, db_url):
        self.engine = create_engine(db_url)
        self.metadata = MetaData(self.engine)
        base_session = sessionmaker(bind=self.engine)
        self.session = base_session()
        url_info = extract_db_url(db_url)
        self.driver = url_info['driver']
        self.description = eng_profile(db_url)
 
    def query(self, *args):
        return self.session.query(*args)
        
    def commit(self, row):
        self.session.add(row)
        self.session.commit()

    def execute(self, sql):
        return self.engine.execute(sql)

    def get_table(self, tablename, schema=None):
        return Table(tablename, self.metadata, autoload=True, schema=schema)

    def get_count(self, table):
        sql = select([func.count()]).select_from(table)
        q = self.execute(sql)
        return q.scalar()


class CommonModel(object):
    def to_dict(self):
        values = {}
        for column in self.__table__.columns:
            values[column.name] = getattr(self, column.name)
        return values
        
    def from_dict(self, values):
        for column in self.__table__.columns:
            if column.name in values:
                setattr(self, column.name, values[column.name])

    def as_timezone(self, fieldname):
        date_ = getattr(self, fieldname)
        return date_ and as_timezone(date_) or None
 

class BaseModel(CommonModel):
    id = Column(Integer, nullable=False, primary_key=True)


class LogModel(BaseModel):
    created = Column(DateTime(timezone=True),
                     nullable=False,
                     default=create_now)


class IsoModel(LogModel):
    # Nama bank (bjb, btn) atau forwarder (mitracomm)
    forwarder = Column(String(16), nullable=False, default='bjb')
    ip = Column(String(15), nullable=False, default='10.31.224.200')
    mti = Column(String(4), nullable=False, default='0200')
    is_request = Column(Boolean, nullable=False, default=True)
    raw = Column(Text, nullable=False)
    request_id = Column(Integer) # foreign key ke diri sendiri
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

            
class HistoryModel(LogModel):
    updated = Column(DateTime(timezone=True),
                     nullable=False,
                     default=create_now)

    def save(self):
        self.updated = create_now()
        if not self.id:
            self.created = self.updated



            
def create_schema(engine, schema):
    from sqlalchemy.schema import CreateSchema
    sql = select([('schema_name')]).\
            select_from('information_schema.schemata').\
            where("schema_name = '%s'" % schema)
    q = engine.execute(sql)
    if not q.fetchone():
        engine.execute(CreateSchema(schema))
