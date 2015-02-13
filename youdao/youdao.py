# coding:utf-8

import sys
import getopt
import requests
import json
from termcolor import colored
from youdao_web import youdao_web
from youdao_db import  youdao_db


class youdao:
    params = {
        'keyfrom': 'longcwang',
        'key': '131895274',
        'type': 'data',
        'doctype': 'json',
        'version': '1.1',
        'q': 'query'
    }
    api_url = 'http://fanyi.youdao.com/openapi.do'
    error_code = {
        0: u'正常',
        20: u'要翻译的文本过长',
        30: u'无法进行有效的翻译',
        40: u'不支持的语言类型',
        50: u'无效的key',
        60: u'无词典结果，仅在获取词典结果生效'
    }

    def get_response(self, word, use_api):
        if use_api:
            self.params['q'] = word
            r = requests.get(self.api_url, params=self.params)
            r.raise_for_status()    # a 4XX client error or 5XX server error response
            result = r.json()
        else:
            yd = youdao_web()
            result = yd.get_result(word)

        return result

    def show(self, result):
        if result['errorCode'] != 0:
            print colored(self.error_code[result['errorCode']], 'red')
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

    def query(self, word, use_db=True, use_api=False):
        try:
            db = youdao_db()
            result = None
            if use_db:
                data = db.get_word(word)
                if data:
                    result = json.loads(data)
            if not result:
                result = self.get_response(word, use_api)
                db.save_word(word, result)
            self.show(result)

        except requests.HTTPError as e:
            print colored(u'网络错误: %s' % e.message, 'red')


def main():
    options, args = getopt.getopt(sys.argv[1:], 'an')

    use_api = False
    use_db = True
    for opt in options:
        if opt[0] == '-a':
            use_api = True
        if opt[0] == '-n':
            use_db = False

    word = ' '.join(args)

    while not word:
        word = raw_input(colored('input a word: ', 'blue'))

    yd = youdao()
    yd.query(word, use_db, use_api)

if __name__ == '__main__':
    main()