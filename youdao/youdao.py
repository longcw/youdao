# coding:utf-8

import sys
import getopt
import requests
from termcolor import colored


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

    def get_response(self, word):
        self.params['q'] = word
        r = requests.get(self.api_url, params=self.params)
        r.raise_for_status()    # a 4XX client error or 5XX server error response
        return r.json()

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
                print colored(u'基本词典:', 'blue')
                print colored('\t'+'\n\t'.join(result['basic']['explains']), 'yellow')

            print colored(u'有道翻译:', 'blue')
            print colored('\t'+'\n\t'.join(result['translation']), 'cyan')

            if 'web' in result:
                print colored(u'网络释义:', 'blue')
                for item in result['web']:
                    print '\t' + colored(item['key'], 'cyan') + ': ' + '; '.join(item['value'])

    def query(self, word):
        try:
            result = self.get_response(word)
            self.show(result)
        except requests.HTTPError as e:
            print colored(u'网络错误: %s' % e.message, 'red')


def main():
    options, args = getopt.getopt(sys.argv[1:], [])

    if not args:
        word = raw_input(colored('input a word: ', 'blue'))
    else:
        word = ' '.join(args)
    yd = youdao()
    yd.query(word)

if __name__ == '__main__':
    main()