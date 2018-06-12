from sqlalchemy import (
    Column,
    String,
    DateTime,
    BigInteger,
    Integer,
    Text,
    Float,
    Boolean,
    ForeignKey,
    UniqueConstraint,
    )
from base_models import (
    Base,
    BaseModel,
    LogModel,
    IsoModel,
    HistoryModel,
    )


# h2h pbb / h2h bphtb / h2h padl / h2h webr
class Jenis(BaseModel, Base):
    __tablename__ = 'log_jenis'
    nama = Column(String(16), nullable=False, unique=True)


# INFO / ERROR / WARNING
class Kategori(BaseModel, Base):
    __tablename__ = 'log_kategori'
    nama = Column(String(7), nullable=False, unique=True)


class Log(LogModel, Base):
    __tablename__ = 'log'
    jenis_id = Column(Integer, ForeignKey('log_jenis.id'), nullable=False)
    line = Column(Text, nullable=False)
    # line_id berisi md5 dari line
    line_id = Column(String(32), nullable=False)
    tgl = Column(DateTime(timezone=True), nullable=False)
    kategori_id = Column(
            Integer, ForeignKey('log_kategori.id'), nullable=False)
    __table_args__ = (UniqueConstraint('jenis_id', 'line_id'),)


class Iso(IsoModel, Base):
    __tablename__ = 'log_iso'
    id = Column(Integer, ForeignKey('log.id'), primary_key=True)
    bit_002 = Column(Text)
    bit_003 = Column(Text)
    bit_004 = Column(Text)
    bit_005 = Column(Text)
    bit_006 = Column(Text)
    bit_007 = Column(Text)
    bit_008 = Column(Text)
    bit_009 = Column(Text)
    bit_010 = Column(Text)
    bit_011 = Column(Text)
    bit_012 = Column(Text)
    bit_013 = Column(Text)
    bit_014 = Column(Text)
    bit_015 = Column(Text)
    bit_016 = Column(Text)
    bit_017 = Column(Text)
    bit_018 = Column(Text)
    bit_019 = Column(Text)
    bit_020 = Column(Text)
    bit_021 = Column(Text)
    bit_022 = Column(Text)
    bit_023 = Column(Text)
    bit_024 = Column(Text)
    bit_025 = Column(Text)
    bit_026 = Column(Text)
    bit_027 = Column(Text)
    bit_028 = Column(Text)
    bit_029 = Column(Text)
    bit_030 = Column(Text)
    bit_031 = Column(Text)
    bit_032 = Column(Text)
    bit_033 = Column(Text)
    bit_034 = Column(Text)
    bit_035 = Column(Text)
    bit_036 = Column(Text)
    bit_037 = Column(Text)
    bit_038 = Column(Text)
    bit_039 = Column(Text)
    bit_040 = Column(Text)
    bit_041 = Column(Text)
    bit_042 = Column(Text)
    bit_043 = Column(Text)
    bit_044 = Column(Text)
    bit_045 = Column(Text)
    bit_046 = Column(Text)
    bit_047 = Column(Text)
    bit_048 = Column(Text)
    bit_049 = Column(Text)
    bit_050 = Column(Text)
    bit_051 = Column(Text)
    bit_052 = Column(Text)
    bit_053 = Column(Text)
    bit_054 = Column(Text)
    bit_055 = Column(Text)
    bit_056 = Column(Text)
    bit_057 = Column(Text)
    bit_058 = Column(Text)
    bit_059 = Column(Text)
    bit_060 = Column(Text)
    bit_061 = Column(Text)
    bit_062 = Column(Text)
    bit_063 = Column(Text)
    bit_064 = Column(Text)
    bit_065 = Column(Text)
    bit_066 = Column(Text)
    bit_067 = Column(Text)
    bit_068 = Column(Text)
    bit_069 = Column(Text)
    bit_070 = Column(Text)
    bit_071 = Column(Text)
    bit_072 = Column(Text)
    bit_073 = Column(Text)
    bit_074 = Column(Text)
    bit_075 = Column(Text)
    bit_076 = Column(Text)
    bit_077 = Column(Text)
    bit_078 = Column(Text)
    bit_079 = Column(Text)
    bit_080 = Column(Text)
    bit_081 = Column(Text)
    bit_082 = Column(Text)
    bit_083 = Column(Text)
    bit_084 = Column(Text)
    bit_085 = Column(Text)
    bit_086 = Column(Text)
    bit_087 = Column(Text)
    bit_088 = Column(Text)
    bit_089 = Column(Text)
    bit_090 = Column(Text)
    bit_091 = Column(Text)
    bit_092 = Column(Text)
    bit_093 = Column(Text)
    bit_094 = Column(Text)
    bit_095 = Column(Text)
    bit_096 = Column(Text)
    bit_097 = Column(Text)
    bit_098 = Column(Text)
    bit_099 = Column(Text)
    bit_100 = Column(Text)
    bit_101 = Column(Text)
    bit_102 = Column(Text)
    bit_103 = Column(Text)
    bit_104 = Column(Text)
    bit_105 = Column(Text)
    bit_106 = Column(Text)
    bit_107 = Column(Text)
    bit_108 = Column(Text)
    bit_109 = Column(Text)
    bit_110 = Column(Text)
    bit_111 = Column(Text)
    bit_112 = Column(Text)
    bit_113 = Column(Text)
    bit_114 = Column(Text)
    bit_115 = Column(Text)
    bit_116 = Column(Text)
    bit_117 = Column(Text)
    bit_118 = Column(Text)
    bit_119 = Column(Text)
    bit_120 = Column(Text)
    bit_121 = Column(Text)
    bit_122 = Column(Text)
    bit_123 = Column(Text)
    bit_124 = Column(Text)
    bit_125 = Column(Text)
    bit_126 = Column(Text)
    bit_127 = Column(Text)
    bit_128 = Column(Text)


class Conf(HistoryModel, Base):
    __tablename__ = 'log_conf'
    nama = Column(String(64), nullable=False, unique=True)
    nilai = Column(Text)
    nilai_int = Column(Integer)
    nilai_float = Column(Float)
    nilai_bool = Column(Boolean)
