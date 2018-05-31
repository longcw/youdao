# coding:utf-8

import sys
import os
import shutil
import argparse
import requests
import json
import webbrowser
from collections import deque
from termcolor import colored
from spider import YoudaoSpider
from model import Word
import config


def show_result(result):
    """
    展示查询结果
    :param result: 与有道API返回的json 数据结构一致的dict
    """
    if 'stardict' in result:
        print colored(u'StarDict:', 'blue')
        print result['stardict']
        return

    if result['errorCode'] != 0:
        print colored(YoudaoSpider.error_code[result['errorCode']], 'red')
    else:
        print colored('[%s]' % result['query'], 'magenta')
        if 'basic' in result:
            if 'us-phonetic' in result['basic']:
                print colored(u'美音:', 'blue'), colored('[%s]' % result['basic']['us-phonetic'], 'green'),
            if 'uk-phonetic' in result['basic']:
                print colored(u'英音:', 'blue'), colored('[%s]' % result['basic']['uk-phonetic'], 'green')
            if 'phonetic' in result['basic']:
                print colored(u'拼音:', 'blue'), colored('[%s]' % result['basic']['phonetic'], 'green')

            print colored(u'基本词典:', 'blue')
            print colored('\t'+'\n\t'.join(result['basic']['explains']), 'yellow')

        if 'translation' in result:
            print colored(u'有道翻译:', 'blue')
            print colored('\t'+'\n\t'.join(result['translation']), 'cyan')

        if 'web' in result:
            print colored(u'网络释义:', 'blue')
            for item in result['web']:
                print '\t' + colored(item['key'], 'cyan') + ': ' + '; '.join(item['value'])


def play(voice_file):
    out1 = os.dup(1)
    out2 = os.dup(2)
    os.close(1)
    os.close(2)
    try:
        webbrowser.open(voice_file)
    finally:
        os.dup2(out1, 1)
        os.dup2(out2, 2)


def query(keyword, use_db=True,  use_dict=True, play_voice=False):
    update_word = [True]
    word = Word.get_word(keyword)
    result = {'query': keyword, 'errorCode': 60}
    if use_db and word:
        result.update(json.loads(word.json_data))
        update_word[0] = False
    elif update_word[0]:
        # 从starditc中查找
        if use_dict and config.config.get('stardict'):
            try:
                from lib.cpystardict import Dictionary
            except ImportError:
                from lib.pystardict import Dictionary
            colors = deque(['cyan', 'yellow', 'blue'])
            stardict_base = config.config.get('stardict')
            stardict_trans = []
            for dic_dir in os.listdir(stardict_base):
                dic_file = os.listdir(os.path.join(stardict_base, dic_dir))[0]
                name, ext = os.path.splitext(dic_file)
                name = name.split('.')[0]
                dic = Dictionary(os.path.join(stardict_base, dic_dir, name))
                try:
                    dic_exp = dic[keyword.encode("utf-8")]
                except KeyError:
                    pass
                else:
                    dic_exp = unicode(dic_exp.decode('utf-8'))
                    stardict_trans.append(colored(u"[{dic}]:{word}".format(dic=name, word=keyword), 'green'))
                    color = colors.popleft()
                    colors.append(color)
                    stardict_trans.append(colored(dic_exp, color))
                    stardict_trans.append(colored(u'========================', 'magenta'))
            if stardict_trans:
                result['stardict'] = u'\n'.join(stardict_trans)
                result['errorCode'] = 0

        # 从stardict中没有匹配单词
        if not result['errorCode'] == 0:
            spider = YoudaoSpider(keyword)
            result.update(spider.get_result(use_api=False))

        # 更新数据库
        new_word = word if word else Word()
        new_word.keyword = keyword
        new_word.json_data = json.dumps(result)
        new_word.save()

    show_result(result)
    if play_voice:
        print(colored(u'获取发音:{word}'.format(word=keyword), 'green'))
        voice_file = YoudaoSpider.get_voice(keyword)
        print(colored(u'获取成功,播放中...', 'green'))
        play(voice_file)


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


def parse_args():
    """Parse input arguments."""
    parser = argparse.ArgumentParser(description='控制台下的有道词典')
    parser.add_argument('word', nargs='*', type=str)
    parser.add_argument('-y', '--youdao', action='store_true', help='优先使用有道词典（默认使用stardict）')
    parser.add_argument('-n', '--new', action='store_true', help='忽略本地数据库，强制重新查词')
    parser.add_argument('-l', '--list', action='store_true', help='列出本地保存的所有单词')
    parser.add_argument('-c', '--clean', action='store_true', help='清空本地数据库')
    parser.add_argument('-v', '--voice', action='store_true', help='获取单词发音')
    parser.add_argument('-d', '--delete', action='store_true', help='删除本地单词')
    parser.add_argument('-s', '--stardict', dest='stardict', type=str, default='', help='设置stardict词典路径')

    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    config.prepare()

    if args.stardict:
        if os.path.isdir(args.stardict):
            config.set_dict_path(args.stardict)
            print('stardict 路径设置成功：{}'.format(args.stardict))
        else:
            print('stardict 路径设置失败. 路径"%s"不存在.'.format(args.stardict))
        return

    if args.list:
        show_db_list()
        return

    if args.clean:
        del_word(None)
        return

    if len(args.word) > 0:
        keyword = unicode(' '.join(args.word), encoding=sys.getfilesystemencoding())
    else:
        word = Word.get_last_word()
        keyword = word.keyword

    if args.delete:
        del_word(keyword)
        return

    use_db = not args.new
    use_dict = not args.youdao
    play_voice = args.voice
    query(keyword, use_db, use_dict, play_voice)


if __name__ == '__main__':
    main()
