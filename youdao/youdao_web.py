# coding:utf-8

import requests
import re
from bs4 import BeautifulSoup


class youdao_web:
    web_url = 'http://dict.youdao.com/search?keyfrom=dict.top&q='
    result = {
        "translation": [],
        "basic": {
            "explains": []
        },
        "query": "",
        "errorCode": 0,
        "web": []
    }


    def get_result(self, word):
        r = requests.get(self.web_url + word)
        r.raise_for_status()
        self.parse(r.text)
        return self.result

    def parse(self, html):
        soup = BeautifulSoup(html)
        root = soup.find(id='results-contents')

        self.result['query'] = unicode(root.find(class_='keyword').string)
        basic = root.find(id='phrsListTab')
        if not basic:
            del self.result['basic']
        else:
            trans = basic.find(class_='trans-container')
            for tran in trans.find_all('li'):
                self.result['basic']['explains'].append(unicode(tran.string))

            #中文
            if len(self.result['basic']['explains']) == 0:
                exp = trans.find(class_='wordGroup').stripped_strings
                self.result['basic']['explains'].append(' '.join(exp))

            #音标
            phons = basic(class_='phonetic', limit=2)
            if len(phons) == 2:
                self.result['basic']['uk-phonetic'] = unicode(phons[0].string)[1:-1]
                self.result['basic']['us-phonetic'] = unicode(phons[1].string)[1:-1]
            elif len(phons) == 1:
                self.result['basic']['phonetic'] = unicode(phons[0].string)[1:-1]

            web = root.find(id='webPhrase')
            for wordgroup in web.find_all(attrs={'class': re.compile(r'^wordGroup$')}, limit=4):
                item = {
                    'key': unicode(wordgroup.find(class_='search-js').string).strip(),
                    'value': wordgroup.get_text().strip().split('\n')
                }
                self.result['web'].append(item)



if __name__ == '__main__':
    test = youdao_web()
    print test.get_result('test')