# -*- coding: utf-8 -*-
""""""

import re
# import logging

from requests import Session
from bs4 import BeautifulSoup

burl = 'http://www.oxbridgedu.org/'
fetcher = Session()
# logging.getLogger().setLevel(logging.INFO)
# logger = logging.getLogger('iguppy')


def fetch_index():
    """"""
    _next = 'http://www.oxbridgedu.org/article/list_264_{}.html'
    uris = list()
    for i in range(1, 66):
        print(_next.format(i))
        r = fetcher.get(url=_next.format(i))
        if 200 != r.status_code:
            raise Exception('fetch {} failed.'.format(_next))

        page = BeautifulSoup(r.content, 'lxml')
        for a in page.select('.main_lb a'):
            uris.append(burl + a.get('href')[1:])

        # #main_l_fy li
        # _next = None
        # for li in page.select('#main_l_fy li a'):
        #     if '下一页' in li.text.strip():
        #         _next = burl + li.get('href')

    return uris

def fetch_detail(uri=''):
    """fetch case infomation."""
    if uri:
        row = list()

        r = fetcher.get(url=uri)
        if 200 != r.status_code:
            return
        page = BeautifulSoup(r.content, 'lxml')
        for p in page.select('#main_nr > p'):
            text = p.text.split('：')
            if text and 2 == len(text):
                _k, _v = text
                # print(_k.strip(), ':', _v.strip())
                row.append((_k.strip(), _v.strip()))
        return row

toefls = ['TOEFL', '托福', ]


def deal_data(data=None):
    """"""
    if data is None:
        return
    for _r in data:
        if '姓名' in _r[0]:
            print(_r[1])
        elif '毕业学校' in _r[0]:
            print(_r[1])
        elif '毕业专业' in _r[0]:
            print(_r[1])
        elif '成绩' in _r[0]:
            print(_r[1])
        elif '录取大学' in _r[0]:
            if '\xa0' in _r[1]:
                p = re.search(r'(.+)\\xa0', _r[1])
                if p:
                    print(p.group(1))
                else:
                    print(_r[1])
            else:
                print(_r[1])
        elif '录取专业' in _r[0]:
            print(_r[1])
        elif '录取学位' in _r[0]:
            print(_r[1])
        else:
            print(_r)

def async_fetch():
    """"""
    # response = self._io_loop.run_sync(functools.partial(
    #         self._async_client.fetch, request, **kwargs))
    # return response
    from tornado.httpclient import AsyncHTTPClient as AHC
    from tornado.gen import coroutine
    from tornado.ioloop import IOLoop
    client = AHC()

    @coroutine
    def handle_fetch():
        response = yield client.fetch('http://www.betteredu.net/star/')
        print(response.body)

    IOLoop().current().run_sync(handle_fetch)
    # handle_fetch()


def main():
    """"""
    uris = fetch_index()
    # rows = list()
    for _u in uris:
        _row = fetch_detail(_u)
        # rows.append(_row)
        if _row:
            deal_data(_row)
        print('\n')

if __name__ == '__main__':
    print('Running ...')
    main()
