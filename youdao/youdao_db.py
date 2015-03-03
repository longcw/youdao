# coding: utf-8

from peewee import *
import json
import os

HOME = os.path.expanduser("~")
db_dir = HOME + '/.dict_youdao'
if not os.path.exists(db_dir):
    os.mkdir(db_dir)
db = SqliteDatabase(db_dir+'/youdao.db')


class BaseModel(Model):
    class Meta:
        database = db


class Word(BaseModel):
    word = CharField(index=True, unique=True)
    json_data = TextField()


class youdao_db:
    def __init__(self):
        db.create_tables([Word], safe=True)

    def save_word(self, aword, dict_data):
        wid = self.get_word_id(aword)

        word = Word()
        word.id = wid
        word.word = aword
        word.json_data = json.dumps(dict_data)
        word.save()

    def get_word(self, word):
        try:
            word = Word.select(Word.json_data).where(Word.word == word).get()
            return word.json_data
        except Word.DoesNotExist:
            return None

    def get_word_id(self, word):
        try:
            word = Word.select(Word.id).where(Word.word == word).get()
            return word.id
        except Word.DoesNotExist:
            return None

    def get_all_word(self):
        return [row.word for row in Word.select(Word.word)]

    def del_word(self, word=None):
        if word:
            Word.delete().where(Word.word == word).execute()
        else:
            Word.delete().execute()

    def __del__(self):
        db.close()