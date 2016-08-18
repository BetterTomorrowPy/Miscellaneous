# -*- coding: utf-8 -*-
""""""
import re

from requests import Session
from bs4 import BeautifulSoup
from torndb import Connection

_burl = 'http://www.hsliuxue.com.cn/'
fetcher = Session()
db = Connection(host='', database='', 
                user='', password='')


class HTTPError(Exception):
    pass


def fetch_index_url():
    """"""
    r = fetcher.get(url=_burl)
    if 200 != r.status_code:
        raise HTTPError('fetch {} failed!'.format(_burl))
    page = BeautifulSoup(r.content, 'lxml')
    dx = page.select('#DaXue > div a')
    zx = page.select('#ZhongXue > div a')

    return [(_a.get_text().strip()[:2], _a.get_text().strip()[2:4], 
        _burl + _a.get('href')) for _a in dx[1:] + zx[1:]]
    

def fetch_list(u=None):
    """"""
    if not u:
        raise ValueError

    r = fetcher.get(url=u[2])
    if 200 != r.status_code:
        raise HTTPError

    page = BeautifulSoup(r.content, 'lxml')
    lf = page.select_one('#ListFrame')
    if lf:
        _next = _burl + lf.get('src')

        def get_coll_uri(uri=''):
            """"""
            print('fetching {}'.format(uri))
            r = fetcher.get(url=_next)
            if 200 != r.status_code:
                raise HTTPError
            with open('fds.html', 'wb') as fd:
                fd.write(r.content)
            page = BeautifulSoup(r.content, 'lxml')
            _uris = page.select('.news_list2 > ul a')

            _colls = [(u[0], u[1], _burl + _u.get('href')) for _u in _uris]

            rt = page.select_one('.rt')
            if rt.get('href'):
                return _burl + rt.get('href'), list(set(_colls))
            return None, list(set(_colls))

        schools = list()
        while True:
            # print(_next)
            try:
                next_uri, colls = get_coll_uri(_next)
                schools.extend(colls)
                if next_uri is None:
                    break
                _next = next_uri
                print('fetched {}'.format(_next))
            except:
                continue

        return schools


def fetch_detail(row=None):
    """"""
    if not row:
        raise ValueError
    r = fetcher.get(url=row[2])
    if 200 != r.status_code:
        raise HTTPError
    # with open('detail.html', 'wb') as fd:
    #     fd.write(r.content)
    page = BeautifulSoup(r.content, 'lxml')
    _info = page.select_one('.Expert_info')
    if _info:
        try:
            result = dict()

            result['country'] = row[0]
            if row[1] == '中学':
                result['level'] = 3
            else:
                result['level'] = 4
            result['site_url'] = row[2]

            _name = _info.select_one('h1').contents
            result['name'] = _name[0].strip()
            result['eg_name'] = _name[2].strip()
            # _logo = _info.select_one('.Expert_info > p img')
            # print(_logo)

            p = re.search(r'eWebEditor/UploadFile/(\d+\.[a-z]+)', r.text)
            if p:
                _lu = _burl + p.group(0)
                _path = p.group(1)
                result['logo'] = '/ins_logo/27/' + _path
                down_img(_lu, '27/' + _path)
                # print(_lu)
            else:
                p = re.search(r'Files/image/(.+\.[a-z]+)', r.text)
                if p:
                    _lu = _burl + p.group(0)
                    _path = p.group(1)
                    result['logo'] = '/ins_logo/27/' + _path
                    down_img(_lu, '27/' + _path)
                    # print(_path)

            info = list()

            _rows = page.select('.Expert_info p strong')

            for _r in _rows:
                if _r.get_text():
                    text = _r.text.split('：')
                    if 2 == len(text):
                        info.append((text[0].strip(), text[1].strip()))
                    else:
                        continue
                # text = _r.prettify()
                # p = re.compile(r'<[^>]*>')
                # text = p.sub('', text)
                # p = re.compile('\n')
                # print(p.sub('', text))
            if not info:
                _div = page.select('.Expert_info > div')
                for _d in _div:
                    if _d.get_text():
                        text = _d.text.split('：')
                        # print(text)
                        if 2 == len(text):
                            info.append((text[0].strip(), text[1].strip()))
                        else:
                            continue

            for _i in info:
                if '位置' in _i[0]:
                    result['area'] = _i[1]
                elif '网址' in _i[0]:
                    result['gw'] = _i[1]
                elif '建校' in _i[0]:
                    _p = re.search(r'(\d+)', _i[1])
                    result['bulit_time'] = _p.group(1)
                elif '类型' in _i[0]:
                    result['type'] = _i[1]
                elif '性质' in _i[0]:
                    result['xz'] = _i[1]
                else:
                    continue
            print(result)
            save_data(result)

        except:
            pass
    return 

# INSERT INTO `xiongyang`.`t_institution_source` (`f_site_id`, `f_country`, `f_area`, `ins_name`, `ins_ename`, `f_logo`, `ins_cname`, `f_site_url`, `f_founded`, `f_url`, `f_level_id`, `f_private`, `f_board`) VALUES ('27', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'xx', 'x', '12', 'x', 'xx');

def down_img(uri='', path=''):
    """"""
    r = fetcher.get(url=uri)
    with open(path, 'wb') as fd:
        fd.write(r.content)

def save_data(data=None):
    """"""
    if data:
        sql = "INSERT INTO `xiongyang`.`t_institution_source` (`f_site_id`, `f_country`, `f_area`, `ins_name`, `f_logo`, `ins_ename`, `f_site_url`, `f_founded`, `f_url`, `f_level_id`, `f_private`, `f_board`) VALUES ('27', %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        db.execute(sql, data.get('country', ''), data.get('area', ''), data.get('name', ''), data.get('logo', ''), 
            data.get('eg_name', ''), data.get('site_url', ''), data.get('bulit_time', ''), data.get('gw', ''), 
            str(data.get('level', '')), data.get('xz', ''), data.get('type', ''))
    return 



def main():
    uris = fetch_index_url()
    for _u in uris:
        for row in fetch_list(_u):
            # remove `u` in python3
            # print('fetching {0} {1} {2}'.format(row[0], row[1], row[2]))
            fetch_detail(row)

if __name__ == '__main__':
    print('Running ... ')
    main()
    # db.execute("DELETE FROM xiongyang.t_institution_source WHERE f_site_id = 27")
