# -*- coding: utf-8 -*-
""""""

import re
import logging

from requests import Session
from bs4 import BeautifulSoup

burl = 'http://www.xinquanedu.com/news/chenggonganli/'
fetcher = Session()
logging.getLogger().setLevel(logging.INFO)
logger = logging.getLogger('iguppy')


def fetch_list():
    """"""
    _next = burl
    rows = list()
    while True:
        try:
            r = fetcher.get(url=_next)
            if 200 != r.status_code:
                continue
            page = BeautifulSoup(r.content, 'lxml')
            for dd in page.select('.list_new_cgal dl dd'):
                aa = dd.select('a')
                al = list()
                for a in aa[:-1]:
                    text = a.text
                    al.append(text)
                uri = aa[-1].get('href')
                # print(uri)
                # if uri.startswith('/'):
                #     uri = uri[1:]
                duri = 'http://www.xinquanedu.com' + uri
                al.append(duri)
                # try:
                # fetch_detail(duri)
                # except:
                #     print('resolve {} failed.'.format(duri))
                rows.append(al)

            _next = None
            for a in page.select('a[href^="list"]'):
                if '下一页' == a.text.strip():
                    _next = burl + a.get('href')
                    print(_next)
            if not _next:
                break

        except:
            pass

    return rows


def fetch_detail(row=None):
    """"""
    if not row:
        return
    print(row)

    r = fetcher.get(url=row[-1])
    if 200 != r.status_code:
        return
    # with open('xxx.html', 'wb') as fd:
    #     fd.write(r.content)
    page = BeautifulSoup(r.content, 'lxml')
    # p = re.compile(r'\<p\>(.+?)：(.*?)\</p\>')
    # results = p.findall(r.content.decode('utf-8'))
    for p in page.select('.jzms_xw_xx02 > p'):
        text = p.text
        if text and '：' in text:
            tl = text.split('：')
            if 2 == len(tl) and '' != tl[-1]:
                _k, _v = tl
                print(_k.strip(), ':',  _v.strip())
    # print(results)
    # for row in results:
    #     print(row)



if __name__ == '__main__':
    print('Running .... ')
    # rows = fetch_list()
    
    # for row in rows:
    #     fetch_detail(row)
    fetch_detail([1, 'http://www.xinquanedu.com/news/chenggonganli/shenyanggongsi/2011/1208/5512.html'])