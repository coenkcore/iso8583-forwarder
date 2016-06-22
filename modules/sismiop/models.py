from base_models import CommonModel


class Models(object):
    def __init__(self, Base, db_schema):
        class Invoice(Base, CommonModel):
            __tablename__ = 'sppt'
            __table_args__ = dict(schema=db_schema, autoload=True)
        self.Invoice = Invoice

        class Pembayaran(Base, CommonModel):
            __tablename__ = 'pembayaran_sppt'
            __table_args__ = dict(schema=db_schema, autoload=True)
        self.Pembayaran = Pembayaran

        class Kelurahan(Base, CommonModel):
            __tablename__ = 'ref_kelurahan'
            __table_args__ = dict(schema=db_schema, autoload=True)
        self.Kelurahan = Kelurahan

        class Kecamatan(Base, CommonModel):
            __tablename__ = 'ref_kecamatan'
            __table_args__ = dict(schema=db_schema, autoload=True)
        self.Kecamatan = Kecamatan

        class Kabupaten(Base, CommonModel):
            __tablename__ = 'ref_dati2'
            __table_args__ = dict(schema=db_schema, autoload=True)
        self.Kabupaten = Kabupaten

        class Propinsi(Base, CommonModel):
            __tablename__ = 'ref_propinsi'
            __table_args__ = dict(schema=db_schema, autoload=True)
        self.Propinsi = Propinsi
