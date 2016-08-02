# -*- coding: utf-8 -*-
"""Update zinch.cn data."""
import re
import json

from requests import Session
from bs4 import BeautifulSoup
from tornado.queues import Queue
from concurrent.futures import ThreadPoolExecutor
from torndb import Connection
# from motor.motor_asyncio import AsyncIOMotorClient

db = Connection(host='192.168.0.1', database='database', 
                user='root', password='KY8oyP5fvWMIeMZz4te6')

fetcher = Session()

b_uri = 'http://www.zinch.cn/'
uris = [ 
    ('ss/us', '美国') ,
    ('ss/us/program', '美国') , 
    ('ss/us/hs', '美国'), 
    ('ss/us/co', '美国'), 
    ('ss/IEP', '美国'), 
    ('ss/us/business', '美国'), 
    ('ss/us/graduate', '美国'),
    ('ss/uk', '英国'), 
    ('ss/au', '澳大利亚'), 
    ('ss/ca', '加拿大'), 
    ('ss/jp', '日本'), 
    ('ss/jp/language', '日本'), 
    ('ss/schools/Europe', '欧洲'), 
    ('ss/schools/Asia', '亚洲'), 
    ('ss/art', '')
]

_headers = {
    'Host': 'www.zinch.cn', 
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0', 
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 
    'Referer': 'http://www.zinch.cn/', 
    'Content-Type': 'application/x-www-form-urlencoded'
}
_p_headers = {
    'Host': 'cdm.zinch.cn', 
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0', 
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
}

default_logo = ''
default_image = ''

_thread_pool = ThreadPoolExecutor(8)
q = Queue()


def fetch_index_page(uri='', country=''):
    """"""
    r = fetcher.get(url=uri, headers=_headers)
    if 200 != r.status_code:
        print('> Fetch url :{} failed.'.format(uri))
        return
    # p = re.compile(r'/(\w+)')
    # path = p.findall(uri)[-1]
    # with open('{}.html'.format(path), 'wb') as fd:
    #     fd.write(r.content)
    page = BeautifulSoup(r.content, 'html.parser')
    try:
        blocks = page.select('.properties-name-cn a')
        pager = page.select('.pager li a')[-1]
    except:
        return
    for block in blocks:
        # print('-' * 8)
        _uri = b_uri + block.get('href')[1:]
        print(_uri)
        try:
            fetch_detail_page(_uri, country)
        except:
            with open('detail.log', 'a') as fd:
                fd.write(_uri)
                fd.write('\n')
        # q.put(_uri)
    next = pager.get('href').strip('/')
    if next:
        # p = re.search('^(/+)ss', next)
        # _next = next
        # print(p.group(0))
        # if p:
        #     _next = next.replace(p.group(1), '/')
        pr = b_uri + next
        # pr.replace('/////', '/')
        print(pr)
        try:
            fetch_index_page(pr, country)
        except:
            print('*' * 8, pr)
    return


def fetch_detail_page(uri='', country=''):
    """"""
    r = fetcher.get(url=uri, headers=_headers)
    if 200 != r.status_code:
        print('* Request detail page :{} failed.'.format(uri))
        return
    page = BeautifulSoup(r.content, 'html.parser')

    header = page.find('div', attrs={'class': 'school-profile-header-v2-left-basic-info clearfix'})
    logo = header.select('.imagecache-104x104')[0].get('src')
    cname = header.select('.school-name-cn')[0].get_text().strip()
    ename = header.select('.school-name-en')[0].get_text().strip()
    blo = header.select('.school-location-info')[0].get_text().strip()
    # lo = header.select('.school-location-provice-search-link')[0].get_text().strip()
    smap = header.select('.modalframe-map-child')[0].get('href')

    # r = fetcher.get(url=smap)
    # latitude, longitude
    _uri = b_uri + smap[1:]
    r = fetcher.get(url=_uri, headers=_headers)
    la = 0.0
    lo = 0.0
    if 200 == r.status_code:
        # "latitude":"40.343989","longitude":"-74.651448"
        loca = re.search(r'"latitude":"(.+?)","longitude":"(.+?)"', r.text)
        if loca:
            la = loca.group(1)
            lo = loca.group(2)
    else:
        pass

    # down logo
    _path = 'static\\logo\\default.jpg'

    if logo:
        if logo == 'http://cdm.zinch.cn/sites/default/files/imagecache/104x104/imagefield_default_images/school-default-logo.png':
            print('> default_logo')
        else:
            try:
                r = fetcher.get(url=logo, headers=_p_headers)
                # print(r.status_code)
                _path = 'static\\logo\\{}.jpg'.format(ename)
                with open(_path.format(ename), 'wb') as fd:
                    fd.write(r.content)
            except:
                pass

    def down_images(uri='', name='', retry=0):
        r = Session().get(url=uri, headers=_p_headers)
        if 200 != r.status_code:
            if retry > 3:
                return
            retry += 1
            print('Failed! now retry {}'.format(retry))
            down_images(uri=uri, retry=retry)
        with open(name, 'wb') as fd:
            fd.write(r.content)
        return True

    r = fetcher.get(url=uri+'/album', headers=_headers)
    img_name = 'static\\images\\' + uri[20:] + '_{}.jpg'
    images = list()
    if 200 == r.status_code:
        pi = re.search(r'"zinch_school_photos":\{(.+?)\}', r.text)
        if pi:
            tmp = '{' + pi.group(1).replace('\/', '/') + '}'
            # print(tmp)
            imgs = json.loads(tmp)
            _count = 1
            # _imgs = imgs.values()
            # print(_imgs)
            # return
            for img in imgs.values():
                print('Fetching:', img)
                _name = img_name.format(_count)
                _count += 1
                _result = down_images(img, _name)
                if _result:
                    images.append(_name)
                
        # home = BeautifulSoup(r.content, 'html.parser')
        # imgs = home.select('#Smailllist')
        # print(imgs)
        # for img in imgs:
        #     print(img)


    info = {
        'country': country, 
        'uri': uri, 
        'name': cname, 
        'english_name': ename, 
        'city': blo[4:-7].strip(), 
        'latitude': la, 
        'longitude': lo, 
        'logo_uri': _path, 
        'images': images
    }
    print('>')
    try:
        insert_per_data(info)
    except:
        pass

def insert_per_data(d={}):
    """"""
    if not isinstance(d, dict):
        return
    if not d:
        return
    try:
        sql = "INSERT INTO `xiongyang`.`t_institution_source` (`f_site_id`, `f_country`, `f_name`, `f_ename`, `f_cname`, `f_site_url`, `f_level_id`, `f_city`, `f_longitude`, `f_latitude`, `f_logo`, `f_update`) \
VALUES ('4', '%s', '%s', '%s', '%s', '%s', 1, '%s', '%s', '%s', '%s', '2016-07-29 14:46:22')" % (d.get('country', ''), d.get('name', ''), d.get('english_name', ''), d.get('name', ''), d.get('uri', ''), 
    d.get('city', ''), d.get('longitude', ''), d.get('latitude', ''), d.get('logo_uri', ''))
        iid = db.execute(sql)
        # iid = 1
        print(sql)
        print('iid:', iid)
        if iid:
            # _path = ':'.join(d.get('images', ''))
            for image in d.get('images', ''):
                _sql = "INSERT INTO `xiongyang`.`t_institution_pic` (`f_path`, `f_type`, `f_ins_id`) VALUES ('%s', 1, %d)" % (image, iid)
                print('path_id:', db.execute(_sql))
                # print(_sql.encode('utf-8'))
    except:
        print('Insert failed: ', d)
    return

def main():
    """"""
    for uri in uris[1:]:
        _uri = b_uri + uri[0]
        # print(_uri)
        fetch_index_page(_uri, uri[1])

if __name__ == '__main__':
    print('running ... ')
    main()
    # fetch_index_page('http://www.zinch.cn/ss/au?page=3', '澳大利亚')
    # d = db.execute("DELETE FROM xiongyang.t_institution_source WHERE f_site_id = 4")
    # db.execute("DELETE FROM xiongyang.t_institution_pic")
    # print(d)


