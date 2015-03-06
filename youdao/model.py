# coding: utf-8

import datetime
from peewee import *
from config import DB_DIR


db = SqliteDatabase(DB_DIR)


class BaseModel(Model):
    class Meta:
        database = db


class Word(BaseModel):
    keyword = CharField(index=True, unique=True)
    json_data = TextField()
    add_time = DateTimeField(default=datetime.datetime.now())
    query_time = DateTimeField(default=datetime.datetime.now())
    count = IntegerField(default=1)

    @classmethod
    def get_word(cls, keyword):
        try:
            word = cls.select().where(Word.keyword == keyword).get()
            word.query_time = datetime.datetime.now()
            word.count += 1
            word.save()
            return word
        except Word.DoesNotExist:
            return None

    @classmethod
    def get_last_word(cls):
        try:
            word = cls.select().order_by(cls.query_time.desc()).get()
            return word
        except cls.DoesNotExist:
            return None