from datetime import datetime
from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
    select,
    func,
    Column,
    Integer,
    DateTime
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


class HistoryModel(BaseModel):
    created = Column(DateTime(timezone=True),
                     nullable=False,
                     default=datetime.utcnow)
    updated = Column(DateTime(timezone=True),
                     nullable=False,
                     default=datetime.utcnow)

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
