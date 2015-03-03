# coding:utf-8

import requests
import re
import json
from bs4 import BeautifulSoup


class youdao_web:
    web_url = 'http://dict.youdao.com/search?keyfrom=dict.top&q='
    translation_url = 'http://fanyi.youdao.com/translate?keyfrom=dict.top&i='
    result = {
        "query": "",
        "errorCode": 0,
    }

    def get_result(self, word):
        self.word = word
        r = requests.get(self.web_url + word)
        r.raise_for_status()
        self.parse(r.text)
        return self.result

    def parse(self, html):
        soup = BeautifulSoup(html)
        root = soup.find(id='results-contents')

        #query 搜索的关键字
        keyword = root.find(class_='keyword')
        if not keyword:
            self.result['query'] = self.word
        else:
            self.result['query'] = unicode(keyword.string)

        #基本解释
        basic = root.find(id='phrsListTab')
        if basic:
            trans = basic.find(class_='trans-container')
            if trans:
                self.result['basic'] = {}
                self.result['basic']['explains'] = [unicode(tran.string) for tran in trans.find_all('li')]
                #中文
                if len(self.result['basic']['explains']) == 0:
                    exp = trans.find(class_='wordGroup').stripped_strings
                    self.result['basic']['explains'].append(' '.join(exp))

                #音标
                phons = basic(class_='phonetic', limit=2)
                if len(phons) == 2:
                    self.result['basic']['uk-phonetic'], self.result['basic']['us-phonetic'] = \
                        [unicode(p.string)[1:-1] for p in phons]
                elif len(phons) == 1:
                    self.result['basic']['phonetic'] = unicode(phons[0].string)[1:-1]

        #翻译
        if 'basic' not in self.result:
            self.result['translation'] = self.get_translation(self.word)


        #网络释义(短语)
        web = root.find(id='webPhrase')
        if web:
            self.result['web'] = [
                {
                    'key': unicode(wordgroup.find(class_='search-js').string).strip(),
                    'value': [v.strip() for v in unicode(wordgroup.find('span').next_sibling).split(';')]
                } for wordgroup in web.find_all(class_='wordGroup', limit=4)
            ]
            # for wordgroup in web.find_all(class_='wordGroup', limit=4):
            #     item = {'key': unicode(wordgroup.find(class_='search-js').string).strip(),
            #             'value': [v.strip() for v in unicode(wordgroup.find('span').next_sibling).split(';')]}
            #     self.result['web'].append(item)

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


if __name__ == '__main__':
    test = youdao_web()
    print test.get_result('application')