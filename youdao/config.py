# coding: utf-8

import os
import errno
import pickle
from peewee import SqliteDatabase


VERSION = '0.2.2'
HOME = os.path.expanduser("~")
BASE_DIR = os.path.join(HOME, '.dict_youdao')   # 用户数据根目录
VOICE_DIR = os.path.join(BASE_DIR, 'voice')     # 音频文件

DATABASE = 'youdao.db'
PK_FILE = 'youdao.pk'
DB_DIR = os.path.join(BASE_DIR, DATABASE)
PK_DIR = os.path.join(BASE_DIR, PK_FILE)


def update(config):
    # 从0.2.0开始更改了数据库
    # 重新设置数据库
    if config.get('version', '0') < '0.2.0':
        # silent_remove(DB_DIR)
        from model import db, Word
        db.drop_table(Word, fail_silently=True)
        Word.create_table()


def silent_remove(filename):
    try:
        os.remove(filename)
    except OSError, e:
        if e.errno != errno.ENOENT:
            raise


def prepare():
    if not os.path.exists(BASE_DIR):
        os.mkdir(BASE_DIR)
    if not os.path.exists(VOICE_DIR):
        os.mkdir(VOICE_DIR)

    config = {'version': '0'}
    if os.path.isfile(PK_DIR):
        with open(PK_DIR, 'rb') as f:
            config = pickle.load(f)
    # update
    update(config)
    if config.get('version', '0') < VERSION:
        with open(PK_DIR, 'wb') as f:
            config['version'] = VERSION
            pickle.dump(config, f)
