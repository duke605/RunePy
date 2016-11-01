import peewee_async
from peewee import Model, FloatField, IntegerField, CharField, DateTimeField
from secret import DB_PASSWORD

db = peewee_async.MySQLDatabase('runepy', user='root', password=DB_PASSWORD)
objects = peewee_async.Manager(db)

db.allow_sync = False


class Item(Model):
    id = IntegerField(primary_key=True)
    name = CharField(45)
    price = IntegerField()
    updated_at = DateTimeField()

    class Meta:
        database = db
        db_table = 'items'


class Method(Model):
    id = IntegerField(primary_key=True)
    skill = CharField(32)
    level = IntegerField()
    name = CharField(64)
    exp = FloatField()

    class Meta:
        database = db
        db_table = 'methods'


class Configuration(Model):
    server_id = CharField(18, primary_key=True)
    prefix = CharField(3, null=True)

    class Meta:
        database = db
        db_table = 'configurations'
