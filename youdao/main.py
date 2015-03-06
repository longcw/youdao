# coding:utf-8

import sys
import os
import shutil
import getopt
import requests
import json
from termcolor import colored
from spider import YoudaoSpider
from model import Word
import config


def query(keyword, use_db=True, use_api=False, play_voice=False):
    word = Word.get_word(keyword)
    if use_db and word:
        YoudaoSpider.show_result(json.loads(word.json_data))
    else:
        if not word:
            word = Word()
        spider = YoudaoSpider(keyword)
        try:
            result = spider.get_result(use_api)
            spider.show_result()
            word.keyword = keyword
            word.json_data = json.dumps(result)
            word.save()
        except requests.HTTPError, e:
            print colored(u'网络错误: %s' % e.message, 'red')
            sys.exit()

    if play_voice:
        YoudaoSpider.get_voice(keyword)


def show_db_list():
    print colored(u'保存在数据库中的单词及查询次数:', 'blue')
    for word in Word.select():
        print colored(word.keyword, 'cyan'), colored(str(word.count), 'green')


def del_word(keyword):
    if keyword:
        try:
            word = Word.select().where(Word.keyword == keyword).get()
            word.delete_instance()
            print(colored(u'已删除{0}'.format(keyword), 'blue'))
        except Word.DoesNotExist:
            print(colored(u'没有找到{0}'.format(keyword), 'red'))
        config.silent_remove(os.path.join(config.VOICE_DIR, keyword+'.mp3'))
    else:
        count = Word.delete().execute()
        shutil.rmtree(config.VOICE_DIR, ignore_errors=True)
        print(colored(u'共删除{0}个单词'.format(count), 'blue'))


def show_help():
    print(u"""
    控制台下的有道词典 版本{ver}
    默认通过解析有道网页版获取查询结果, 没有词典结果时自动使用有道翻译,
    查询结果会保存到sqlite 数据库中
    使用方法 yd word [-a] [-n] [-l] [-c] [-v] [-d word] [--help]
    [-a] 使用API 而不是解析网页获取结果
    [-n] 强制重新获取, 不管数据库中是否已经保存
    [-l] 列出数据库中保存的所有单词
    [-c] 清空数据库
    [-v] 获取单词发音, 单独使用 yd -v 可以获取上一个查询单词的发音
    [-d word] 删除数据库中某个单词
    [--help] 显示帮助信息
    """.format(ver=config.VERSION))


def main():
    config.prepare()
    try:
        options, args = getopt.getopt(sys.argv[1:], 'anld:cv', ['help'])
    except getopt.GetoptError:
        options = [('--help', '')]
    if ('--help', '') in options:
        show_help()
        return

    use_api = False
    use_db = True
    play_voice = False
    for opt in options:
        if opt[0] == '-a':
            use_api = True
        elif opt[0] == '-n':
            use_db = False
        elif opt[0] == '-l':
            show_db_list()
            return
        elif opt[0] == '-d':
            del_word(opt[1])
            return
        elif opt[0] == '-c':
            del_word(None)
            return
        elif opt[0] == '-v':
            play_voice = True

    keyword = ' '.join(args)

    # 播放上一个单词的声音
    if play_voice and not keyword:
        word = Word.get_last_word()
        keyword = word.keyword
        query(keyword, play_voice=True, use_db=True)
    else:
        while not keyword:
            keyword = raw_input(colored('input a word: ', 'blue'))

        query(keyword, use_db, use_api, play_voice)

if __name__ == '__main__':
    main()