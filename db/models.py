import peewee_async
from peewee import Model, FloatField, IntegerField, CharField, DateTimeField, BooleanField, ForeignKeyField
from secret import DB_PASSWORD
import util

db = peewee_async.MySQLDatabase('runepy', user='root', password=DB_PASSWORD)
objects = peewee_async.Manager(db)


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


class Item(Model):
    id = IntegerField(primary_key=True)
    name = CharField(255)
    description = CharField(255)
    category = CharField(45)
    price = IntegerField()
    high_alch = IntegerField()
    low_alch = IntegerField()
    runeday = IntegerField()
    members = BooleanField()
    last_updated = DateTimeField()

    @property
    def type_url(self):
        return 'https://cdn.rawgit.com/duke605/RunePy/master/assets/img/%s.png' % ('members' if self.members else 'f2p')

    @property
    def icon_url(self):
        return 'http://services.runescape.com/m=itemdb_rs/obj_big.gif?id=%s' % self.id

    @property
    def grand_exchange_url(self):
        return 'http://services.runescape.com/m=itemdb_rs/viewitem?obj=%s' % self.id

    async def get_history(self):
        return await util.get_price_history(self)

    class Meta:
        database = db
        db_table = '_items'


class Alias(Model):
    alias = CharField(255, primary_key=True)
    item = ForeignKeyField(Item, related_name='aliases', db_column='item_id')

    class Meta:
        database = db
        db_table = 'aliases'
