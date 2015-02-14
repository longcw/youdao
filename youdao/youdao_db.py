# coding: utf-8

from peewee import *
import json

db = SqliteDatabase('youdao.db')


class BaseModel(Model):
    class Meta:
        database = db


class Word(BaseModel):
    word = CharField(index=True, unique=True)
    json_data = TextField()


class youdao_db:
    def __init__(self):
        db.create_table(Word, safe=True)

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

    def __del__(self):
        db.close()