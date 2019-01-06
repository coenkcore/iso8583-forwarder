# class Models(object):
#     def __init__(self, Base, db_schema):
#         class Invoice(Base):
#             __tablename__ = 'ar_invoice'
#             __table_args__ = dict(autoload=True, schema=db_schema)
#
#         self.Invoice = Invoice
#
#         class Payment(Base):
#             __tablename__ = 'ar_payment'
#             __table_args__ = dict(autoload=True, schema=db_schema)
#
#         self.Payment = Payment
