# coding:utf-8

import re
import json
import os
import requests
import webbrowser
from termcolor import colored
from bs4 import BeautifulSoup
from config import VOICE_DIR


class YoudaoSpider:
    """
    通过有道获取单词解释, 以及展示查询结果
    """

    params = {
        'keyfrom': 'longcwang',
        'key': '131895274',
        'type': 'data',
        'doctype': 'json',
        'version': '1.1',
        'q': 'query'
    }
    api_url = u'http://fanyi.youdao.com/openapi.do'
    voice_url = u'http://dict.youdao.com/dictvoice?type=2&audio={word}'
    web_url = u'http://dict.youdao.com/search?keyfrom=dict.top&q='
    translation_url = u'http://fanyi.youdao.com/translate?keyfrom=dict.top&i='

    error_code = {
        0: u'正常',
        20: u'要翻译的文本过长',
        30: u'无法进行有效的翻译',
        40: u'不支持的语言类型',
        50: u'无效的key',
        60: u'无词典结果，仅在获取词典结果生效'
    }

    result = {
        "query": "",
        "errorCode": 0,
    }

    def __init__(self, word):
        self.word = word

    def get_result(self, use_api=False):
        """
        获取查询结果
        :param use_api:是否使用有道API, 否则解析web版有道获取结果
        :return:与有道API返回的json数据一致的dict
        """
        if use_api:
            self.params['q'] = self.word
            r = requests.get(self.api_url, params=self.params)
            r.raise_for_status()    # a 4XX client error or 5XX server error response
            self.result = r.json()
        else:
            r = requests.get(self.web_url + self.word)
            r.raise_for_status()
            self.parse_html(r.text)
        return self.result

    def parse_html(self, html):
        """
        解析web版有道的网页
        :param html:网页内容
        :return:result
        """
        soup = BeautifulSoup(html, "lxml")
        root = soup.find(id='results-contents')

        # query 搜索的关键字
        keyword = root.find(class_='keyword')
        if not keyword:
            self.result['query'] = self.word
        else:
            self.result['query'] = unicode(keyword.string)

        # 基本解释
        basic = root.find(id='phrsListTab')
        if basic:
            trans = basic.find(class_='trans-container')
            if trans:
                self.result['basic'] = {}
                self.result['basic']['explains'] = [unicode(tran.string) for tran in trans.find_all('li')]
                # 中文
                if len(self.result['basic']['explains']) == 0:
                    exp = trans.find(class_='wordGroup').stripped_strings
                    self.result['basic']['explains'].append(' '.join(exp))

                # 音标
                phons = basic(class_='phonetic', limit=2)
                if len(phons) == 2:
                    self.result['basic']['uk-phonetic'], self.result['basic']['us-phonetic'] = \
                        [unicode(p.string)[1:-1] for p in phons]
                elif len(phons) == 1:
                    self.result['basic']['phonetic'] = unicode(phons[0].string)[1:-1]

        # 翻译
        if 'basic' not in self.result:
            self.result['translation'] = self.get_translation(self.word)

        # 网络释义(短语)
        web = root.find(id='webPhrase')
        if web:
            self.result['web'] = [
                {
                    'key': unicode(wordgroup.find(class_='search-js').string).strip(),
                    'value': [v.strip() for v in unicode(wordgroup.find('span').next_sibling).split(';')]
                } for wordgroup in web.find_all(class_='wordGroup', limit=4)
            ]

    def get_translation(self, word):
        """
        通过web版有道翻译抓取翻译结果
        :param word:str 关键字
        :return:list 翻译结果
        """
        r = requests.get(self.translation_url+word)
        if r.status_code != requests.codes.ok:
            return None

        pattern = re.compile(r'"translateResult":\[(\[.+\])\]')
        m = pattern.search(r.text)
        result = json.loads(m.group(1))
        return [item['tgt'] for item in result]

    @classmethod
    def get_voice(cls, word):
        voice_file = os.path.join(VOICE_DIR, word+'.mp3')
        if not os.path.isfile(voice_file):
            r = requests.get(cls.voice_url.format(word=word))
            with open(voice_file, 'wb') as f:
                f.write(r.content)
        return voice_file




if __name__ == '__main__':
    test = YoudaoSpider('application')
    print test.get_result()
