# -*- coding: utf-8 -*-
""""""

import re
import time
import pickle

from requests import Session
from torndb import Connection
from bs4 import BeautifulSoup

buri = 'http://school.nihaowang.com/'

fetcher = Session()

_headers = {
    'Host': 'school.nihaowang.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:48.0) Gecko/20100101 Firefox/48.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Referer': 'http://school.nihaowang.com/',
    'Upgrade-Insecure-Requests': 1,
}

db = Connection(host='', database='',
                user='', password='')


def request_area():
    """"""
    try:
        r = fetcher.get(url='http://school.nihaowang.com/', headers=_headers)
    except IOError as e:
        print(pickle.dumps(e))
    if 200 != r.status_code:
        print('Request category by area failed.')
        return

    page = BeautifulSoup(r.text, 'html.parser')
    countries = page.select('.teach_list_2 > a')
    areas = list()
    for c in countries:
        _area = c.get('title')
        _uri = c.get('href')
        areas.append((_area, buri + _uri))
    return areas


def request_school_list(uri=None):
    """"""
    if not uri:
        return

    def request_per_page_school_list(url=None):
        r = fetcher.get(url=url, headers=_headers)
        if 200 != r.status_code:
            print('Request {} failed!'.format(url))
            return

        page = BeautifulSoup(r.text, 'html.parser')
        _aus = [a.get('href') for a in page.select('.college_title > div > a')]

        return list(set(_aus))    # return college uris

    uri = uri.replace('1-01', '{}-01')
    page_num = 1
    colleges = list()
    while True:
        _url = uri.format(page_num)
        print(_url)
        _cs = request_per_page_school_list(_url)
        if len(_cs) == 0:
            break
        colleges.extend(_cs)
        page_num += 1
    return colleges


def request_school_detail(uri=None, country=None):
    """"""
    text = fetch_return_text(uri=uri, headers=_headers)
    if text:
        coll_info = dict()
        coll_info['site_url'] = uri
        ll = re.search(r"LatLngs = '(.+),(.+)';", text)
        if ll:
            # print(ll.group(1), ll.group(2))
            coll_info['lat'] = ll.group(1)
            coll_info['lag'] = ll.group(2)
        p = re.search(r'/(\d+)\.html', uri)
        if p:
            coll_info['site_id'] = p.group(1)
        page = BeautifulSoup(text, 'html.parser')
        # print(page.prettify())
        # logo uri
        _logo = page.select_one('#div_Logo > img')
        if _logo:
            logo = _logo.get('src')
            logo = down_img(logo, 3, 'logo\\')
            coll_info['logo'] = '/ins_logo/5/' + logo

        # college name.
        _c_name = page.select_one('.school_hd_scName_cn')
        _e_name = page.select_one('.school_hd_scName_en')
        tmp = _c_name.get_text().strip()
        if '（' in tmp:
            _count = tmp.index('（')
            tmp = tmp[:_count]
        # print(tmp)
        p = re.search(r'］|\](.+)', tmp)
        if p:
            # print(p.group(1))
            coll_info['name'] = p.group(1)
        tmp = _e_name.get_text()
        if '(' in tmp:
            _count = tmp.index('(')
            tmp = tmp[:_count]
            coll_info['eg_name'] = tmp.strip()
        else:
            coll_info['eg_name'] = tmp.strip()

        # base info.
        _is = page.select('#ul_InfoBase > li')
        for _info in _is:
            row = _info.get_text().split('：')
            if '省州' == row[0]:
                coll_info['area'] = row[1]
            elif '城市' == row[0]:
                coll_info['city'] = row[1]
            elif '性质' == row[0]:
                coll_info['private'] = row[1]
            elif '建校年代' == row[0]:
                coll_info['founded'] = row[1]
            elif '中国教育部是否认证' == row[0]:
                coll_info['certification'] = ':'.join(row)
            else:
                continue
        # 官网
        _gw = page.select_one('.school_list > div')
        if _gw:
            # _k = _gw.select_one('span').get_text().strip()[:-1]
            _v = _gw.select_one('a')
            if _v:
                coll_info['gw'] = _v.get_text().strip()

        # 简介
        _intro = page.select_one('#introInfo2')
        if not _intro:
            _intro = page.select_one('#introInfo1')
        coll_info['intro'] = _intro.get_text().strip()[:-4].replace('\xa0', '')

        # 校园图片
        _pics = page.select('#focus > ul > li img')
        pics = list()
        if _pics:
            # print('pictures:')
            for _pic in _pics:
                try:
                    _p = down_img(_pic.get('src1'))
                    if _p:
                        pics.append(_p)
                except IOError as e:
                    print(pickle.dumps(e))
                    continue
        coll_info['pics'] = pics
        print(coll_info)
        save_coll(coll_info, country[0])
        return True


def down_img(uri=None, retry=1, lp=''):
    """"""
    if not uri:
        return

    p = re.search(r'school/(.+)\.', uri)
    if p:
        _path = p.group(1).replace('/', '_') + '.jpg'
        path = lp + _path

    def down():
        req = Session().get(url=uri)
        if req.status_code != 200:
            print('Request {0} failed!'.format(uri))
            return False
        with open(path, 'wb') as fd:
            fd.write(req.content)
        return True

    for i in range(retry):
        _status = down()
        if _status:
            break
        time.sleep(3)
    return _path


def fetch_return_text(uri=None, headers={}, status=200):
    """"""
    from requests import Session
    try:
        # print(uri)
        r = Session().get(url=uri, headers=headers)
    except IOError as e:
        import pickle
        print(pickle.dumps(e))
        raise Exception('Request {} failed!'.format(uri))
    # print(r.text)
    if status != r.status_code:
        raise Exception('{0} with http status:{1}'.format(uri, r.status_code))
    return r.text


def save_coll(coll=None, country=None):
    """"""
    c = coll
    sql = "INSERT INTO `xiongyang`.`t_institution_source` (`f_site_id`, `f_site_ins_id`, `f_country`, `f_area`, " \
          "`ins_name`, `ins_ename`, `f_logo`, `f_site_url`, `f_founded`, `f_url`, `f_city`, `f_longitude`, " \
          "`f_latitude`, `f_intro`, `f_private`, `f_certification`) VALUES (55, %s, %s, %s, %s, %s, %s, %s, %s, %s, " \
          "%s, %s, %s, %s, %s, %s)"
    # sql = "INSERT INTO `xiongyang`.`t_institution_source` (`f_site_id`, `f_site_ins_id`, `f_country`, `f_area`, `ins_name`, `ins_ename`, `f_logo`, `f_site_url`, `f_founded`, `f_url`, `f_city`, `f_longitude`, `f_latitude`, `f_intro`, `f_private`, `f_certification`) VALUES (55, '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')"
    # _sql = sql % (c.get('site_id'), country, c.get('area'), c.get('name'), c.get('eg_name'), c.get('logo'), c.get('site_url'), c.get('founded'), c.get('gw'), c.get('city'), c.get('lag'), c.get('lat'), c.get('intro'), c.get('private'), c.get('certification'))
    db.execute(sql, c.get('site_id'), country, c.get('area'), c.get('name'), c.get('eg_name'), c.get('logo'),
               c.get('site_url'), c.get('founded'), c.get('gw'), c.get('city'), c.get('lag'), c.get('lat'),
               c.get('intro'), c.get('private'), c.get('certification'))

    p_sql = "INSERT INTO `xiongyang`.`t_institution_pic` (`f_path`, `f_site_ins_id`, `delflag`) VALUES (%s, %s, 3)"
    for _u in c.get('pics'):
        _u = '/ins_pic/5/' + _u
        db.execute(p_sql, _u, c.get('site_id'))


def main():
    """"""
    areas = request_area()
    for area in areas:
        rows = request_school_list(area[1])
        for row in rows:
            coll_status = False
            for _count in range(3):
                try:
                    coll_status = request_school_detail(row, area)
                except:
                    print('Request {0}-{1}.'.format(row, _count+1))
                if coll_status:
                    break
            if not coll_status:
                with open('failed.log', 'a') as fd:
                    fd.write(area[0])
                    fd.write(row)
                    fd.write('\n')

if __name__ == '__main__':
    print('running ...')
    main()
