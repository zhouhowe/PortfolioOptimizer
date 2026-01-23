from peewee import *
import datetime
import json

db = SqliteDatabase('strategies.db')

class BaseModel(Model):
    class Meta:
        database = db

class Strategy(BaseModel):
    id = AutoField()
    name = CharField()
    description = TextField(null=True)
    parameters = TextField() # Store JSON as string
    created_at = DateTimeField(default=datetime.datetime.now)

def init_db():
    db.connect()
    db.create_tables([Strategy])
    db.close()
