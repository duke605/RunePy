import peewee_async
from peewee import Model, BigIntegerField, IntegerField, CharField, DateTimeField
from secret import DB_PASSWORD

db = peewee_async.MySQLDatabase('skillbot', user='root', password=DB_PASSWORD)
objects = peewee_async.Manager(db)

db.allow_sync = False


class Item(Model):
    id = BigIntegerField(primary_key=True, db_column='Id')
    name = CharField(45, db_column='Name')
    price = IntegerField(db_column='Price')
    updated_at = DateTimeField(db_column='UpdatedAt')
    updated_at_rd = IntegerField(db_column='UpdatedAtRd')

    class Meta:
        database = db
        db_table = 'items'
