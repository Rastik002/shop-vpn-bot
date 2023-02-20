from peewee import *
from playhouse.sqliteq import SqliteQueueDatabase

db = SqliteQueueDatabase("misc/by002.db")

class Users(Model):
    user_id = BigIntegerField(default=0)
    username = TextField(default='')
    date = TextField(default='')
    blocked = BooleanField(default=False)
    balance = IntegerField(default=0)
    date = TextField(default='')
    buy = IntegerField(default=0)
    used = BooleanField(default=False)

    class Meta:
        db_table = "Users"
        database = db

class Razdels(Model):
    name = TextField(default='')
    price = TextField(default='')
    description = TextField(default='')

    class Meta:
        db_table = "Razdels"
        database = db

class Tovars(Model):
    name = TextField(default='')
    price = TextField(default='')
    razdel = TextField(default='')
    brony = BooleanField(default=False)
    user_id = BigIntegerField(default=0)

    class Meta:
        db_table = "Tovars"
        database = db

class Promocode(Model):
    name = TextField(default='')
    amount = TextField(default='')
    quantity = BigIntegerField(default=0)
    used = BigIntegerField(default=0)

    class Meta:
        db_table = "Promocode"
        database = db

def connect():
    db.connect()
    db.create_tables([Users, Razdels, Tovars, Promocode])