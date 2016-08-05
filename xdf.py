# -*- coding: utf-8 -*-
"""新东方前途留学案例采集"""
import re
import time
import hashlib

from datetime import datetime
from requests import Session
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from torndb import Connection

db = Connection(host='', database='', 
                user='', password='')

_thread_pool = ThreadPoolExecutor(max_workers=8)

_headers = {
    'Host': 'liuxue.xdf.cn', 
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0', 
    'Accept': '*/*', 
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8', 
    'X-Requested-With': 'XMLHttpRequest', 
    'Referer': 'http://liuxue.xdf.cn/case/'
}

b_url = 'http://liuxue.xdf.cn/search/xdfsearch/anli_search_newl.jsp'


def fetch_index(page=0, country='', lqsj=''):
    """"""
    post_data = {
        'country': country, 
        'sPage': page, 
        'degree': '', 
        'gpa1': '', 
        'gpa2': '', 
        'lqsj': lqsj, 
        'orderby': '', 
        'schoolranking1': '', 
        'schoolranking2': ''
    }
    r = Session().post(url=b_url, headers=_headers, params=post_data)
    # with open('xdf_index.html', 'wb') as fd:
    #     fd.write(r.content)
    if 200 != r.status_code:
        print('Fetch index page failed')
        return

    page = BeautifulSoup(r.content, 'html.parser')
    items = page.select('.sy_ckan')
    _uris = [[i.get('href'), country, lqsj] for i in items]
    if not (len(_uris) > 0):
        print('Get uris length is 0.')
        return
    # _path = _thread_pool.map(fetch_detail, _uris)
    # for p in _path:
    #     print(p)
    for _u in _uris:
        fetch_detail(_u)
        print('')


def fetch_detail(u=tuple()):
    """"""
    # path = hashlib.new('md5', uri.encode('utf-8')).hexdigest()
    # print(path)
    if not u:
        return

    r = Session().get(url=u[0], headers=_headers)
    if 200 != r.status_code:
        return

    page = BeautifulSoup(r.content, 'html.parser')
    _info = page.select_one('.gu_leftsidebar_info')
    lis = _info.select('ul > li')

    stu = {'country': u[1], 'time': u[2]}
    for li in lis:
        row = li.get_text().split('：')
        rp = re.search(r'xing="(.+)"', li.get_text())
        if rp:
            row[1] = rp.group(1)
        if '录取学生' in row:
            stu['name'] = row[1]
        elif '录取院校' in row:
            stu['coll'] = row[1]
        elif '录取专业' in row:
            stu['cors'] = row[1]
        elif '攻读学位' in row:
            stu['level'] = row[1]
        elif '申请人GPA' in row:
            stu['gpa'] = row[1]
        else:
            continue

    # print(stu)
    try:
        insert_data(stu)
    except:
        print(stu)


def insert_data(stu=None):
    """"""
    if stu is None:
        return
    # _db = Connection(host='', database='', 
    #                  user='', password='')

    name = stu.get('name', '某同学')
    _sql = "SELECT id FROM xiongyang.t_cs_students_src WHERE f_site_id = 25 AND f_surname = '%s' AND f_name = '%s'" % (name[0], name[1:])
    sid = 0
    try:
        _s = db.get(_sql)
        if _s:
            print('{} is exsits.'.format(name))
            sid = _s.get('id')
    except:
        pass

    if sid == 0:
        s_sql = "INSERT INTO `xiongyang`.`t_cs_students_src` (`f_site_id`, `f_country_id`, \
        `f_surname`, `f_name`, `stu_gpa`) VALUES (25, 1, %s, %s, %s)"
        try:
            sid = db.execute(s_sql, name[0], name[1:], stu.get('gpa', 0))
        except:
            pass
    print('sid > ', sid)

    _now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    _time = stu.get('time', '2016') + '/01/01'
    _csql = '''INSERT INTO `xiongyang`.`t_cs_cases_src` (`f_site_id`, `f_student_id`, 
    `f_app_type`, `app_ins_name`, `app_cos_name`, `tmp_admission`, `f_admitted_date`, 
    `updatetime`) VALUES (25, %s, %s, %s, %s, '录取', %s, %s)'''
    try:
        cid = db.execute(_csql, sid, stu.get('level', ''), stu.get('coll', ''), 
            stu.get('cors', ''), _time, _now)
        print('cid > ', cid)
    except:
        pass


def main():
    """"""
    _c = '美国'
    _l = '2014'
    page = 1681

    for p in range(1, page + 1):
        print('page: {}'.format(p))
        fetch_index(p, _c, _l)
        # time.sleep(3)
    db.close()
        
if __name__ == '__main__':
    print('Runnig ... ')
    main()
    # fetch_index()
    # db.execute("DELETE FROM xiongyang.t_cs_students_src where f_site_id = 25")
