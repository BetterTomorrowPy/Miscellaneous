# -*- coding: utf-8 -*-
""""""
import re

from datetime import datetime
from requests import Session
from bs4 import BeautifulSoup
from torndb import Connection

from concurrent.futures import ThreadPoolExecutor

# from pyspider.libs.base_handler import *
_thread_pool = ThreadPoolExecutor(8)
db = Connection(host='', database='', 
                user='', password='')
fetcher = Session()


def fetch_index():
    """"""
    r = fetcher.get(url='http://bbs.gter.net/forum.php?gid=454')
    if 200 != r.status_code:
        return
    page = BeautifulSoup(r.content, 'html.parser')
    _uris = page.select('table[class="fl_tb"] tr h2 a')
    return [_u.get('href') for _u in _uris]

def fetch_srouce(url=''):
    """"""
    next = url
    while next:
        print(next)
        r = fetcher.get(url=next)
        if 200 != r.status_code:
            return
        page = BeautifulSoup(r.content, 'html.parser')
        _duris = page.select('tbody[id^="normalthread"] .xst')
        
        # print(_duris)
        uris = [_du.get('href') for _du in _duris]
        # print(uris)
        for u in uris:
            try:
                fetch_detail(u)
            except:
                with open('fetch_fail.log', 'a') as fd:
                    fd.write(u)
                    fd.write('\n')

        _next = page.select_one('.nxt')
        if _next:
            next = _next.get('href')
        else:
            next = None
    return

def fetch_detail(url=''):
    """"""
    r = fetcher.get(url=url)
    if 200 != r.status_code:
        return
    page = BeautifulSoup(r.content, 'html.parser')
    _offers = page.select('table[summary^="offer"]')
    if _offers:
        # print(_offers)
        offer_list = list()
        for _o in _offers:
            _offer = dict()
            for tr in _o.select('tbody tr'):
                try:
                    if '申请学校' in tr.get_text():
                        _coll = tr.get_text().split(':')
                        _offer['coll'] = _coll[1].strip('\n').strip()
                    elif '学位' in tr.get_text():
                        _degree = tr.get_text().split(':')
                        _offer['degree'] = _degree[1].strip('\n').strip()
                    elif '专业' in tr.get_text():
                        _corse = tr.get_text().split(':')
                        _offer['corse'] = _corse[1].strip('\n').strip()
                    elif '申请结果' in tr.get_text():
                        _result = tr.get_text().split(':')
                        _offer['result'] = _result[1].strip('\n').strip()
                    elif '入学年份' in tr.get_text():
                        _year = tr.get_text().split(':')
                        _offer['year'] = _year[1].strip('\n').strip()
                    # elif '入学学期' in tr.get_text():
                    #     _xq = tr.get_text().split(':')
                    #     print(_xq[1].strip('\n').strip())
                    elif '通知时间' in tr.get_text():
                        _time = tr.get_text().split(':')
                        _offer['time'] = _time[1].strip('\n').strip()
                    else:
                        continue
                except:
                    continue
            offer_list.append(_offer)
        print(offer_list)
        print('\n')

        user = dict()
        _profile = page.select_one('table[summary="个人情况"]')
        for pr in _profile.select('tbody tr'):
            try:
                if 'TOEFL' in pr.get_text():
                    p = re.search(r'Overall: (\d+),', pr.get_text())
                    if p:
                        user['toefl'] = p.group(1)
                    else:
                        user['toefl'] = p.get_text()
                    # _toefl = pr.get_text().split(':')
                    # print(_toefl[2].strip('\n').strip()) GMAT
                elif 'GRE' in pr.get_text():
                    p = re.search(r'Overall: (\d+),', pr.get_text())
                    if p:
                        user['gre'] = p.group(1)
                    else:
                        user['gre'] = p.get_text()
                elif 'GMAT' in pr.get_text():
                    p = re.search(r'Overall: (\d+),', pr.get_text())
                    if p:
                        user['gmat'] = p.group(1)
                    else:
                        user['gmat'] = p.get_text()
                elif 'GPA' in pr.get_text():
                    p = re.search(r'Overall: (\d+),', pr.get_text())
                    if p:
                        user['gpa'] = p.group(1)
                    else:
                        user['gpa'] = p.get_text()
                elif 'IELTS' in pr.get_text():
                    p = re.search(r'Overall: (\d+),', pr.get_text())
                    if p:
                        user['ielts'] = p.group(1)
                    else:
                        user['ielts'] = p.get_text()
                    # _gre = pr.get_text().split(':')
                    # print(_gre[2].strip('\n').strip())
                elif '本科学校档次' in pr.get_text():
                    _level = pr.get_text().split(':')
                    user['level'] = _level[1].strip('\n').strip()
                elif '成绩' in pr.get_text():
                    # _sorce = pr.get_text().split(':')
                    # print(_sorce[1].strip('\n').strip())
                    user['sorce'] = pr.get_text().strip()
                elif '专业' in pr.get_text():
                    _sorce = pr.get_text().split(':')
                    user['zy'] = _sorce[1].strip('\n').strip()
                    # user['sorce'] = pr.get_text().strip()
                else:
                    continue
            except:
                continue
        # name
        _name = page.select_one('.authi .xw1')
        user['name'] = _name.get_text() 
        print(user)  
        print('-' * 8) 
        try:
            save_result(user, offer_list)
        except:
            pass
        # print(_profile)
    return


def save_result(user=None, offers=None):
    """"""
    _now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ssql = "INSERT INTO `xiongyang`.`t_cs_students_src` (`f_site_id`, `f_country_id`, `f_level_id`, `f_surname`, `tmp_ins_cname`, `stu_cos_name`, `stu_gpa`, `stu_gmat_gre`, `stu_toefl`, `stu_ielts`, `f_features`, `updatetime`) VALUES ('26', '1', '4', %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    if user.get('gre'):
        _gmat_gre = user['gre']
    elif user.get('gmat'):
        _gmat_gre = user['gmat']
    else:
        _gmat_gre = ''
    _result = 0
    try:
        _result = db.execute(ssql, user.get('name', ''), user.get('level', ''), user.get('zy', ''), 
            user.get('gpa', ''), _gmat_gre, user.get('toefl', ''), user.get('ielts', ''), 
            user.get('sorce', ''), _now)
    except:
        _result = db.get("SELECT id FROM `xiongyang`.`t_cs_students_src` WHERE f_site_id = 26 AND f_surname = '{}'".format(user.get('name', '')))
    print('user > ', _result)

    if offers:
        for o in offers:
            try:
                osql = "INSERT INTO `xiongyang`.`t_cs_cases_src` (`f_site_id`, `f_level_id`, `f_student_id`, `f_app_type`, `app_ins_name`, `app_cos_name`, `tmp_admission`, `f_app_date`, `f_admitted_date`, `updatetime`) VALUES ('26', '4', %s, %s, %s, %s, %s, %s, %s, %s)"
                _year = o.get('year')
                if len(_year) == 4:
                    year = _year + '/01/01'
                else:
                    year = '2016/01/01'
                _or = db.execute(osql, _result, o.get('degree', ''), o.get('coll', ''), o.get('corse', ''), 
                    o.get('result', ''), year, o.get('time', ''), _now)
                print('case - ', _or)
            except:
                continue

def main():
    uris = fetch_index()
    for u in uris:
        print(u)
        fetch_srouce(u)


# class Handler(BaseHandler):
#     crawl_config = {
#     }

#     @every(minutes=24 * 60)
#     def on_start(self):
#         self.crawl('http://bbs.gter.net/forum.php?gid=454', callback=self.index_page)

#     @config(age=10 * 24 * 60 * 60)
#     def index_page(self, response):
#         for each in response.doc('table[class="fl_tb"] tr h2 a').items():
#             # print(each.attr.href)
#             self.crawl(each.attr.href, callback=self.forum_page)

#     def forum_page(self, response):
#         """"""
#         for each in response.doc('tbody[id^="normalthread"] .new .xst').items():
#             self.crawl(each.attr.href, callback=self.detail_page)

#         _n = response.doc('.nxt')
#         if _n:
#             print(_n.attr.href)
#             self.crawl(_n.attr.href, callback=self.forum_page)

#     def detail_page(self, response):
#         # for tr in response.doc('table[summary^="offer"] tr').items():
#         #     print(tr)
#         # 'table[class="cgtl"]'
#         for t in response.doc('table[summary^="offer"]').items():
#             print(t)
            
#         return {
#             "url": response.url,
#             "title": response.doc('title').text(),
#         }


if __name__ == '__main__':
    main()
    # db.execute("DELETE FROM xiongyang.t_cs_students_src where f_site_id = 26")
    # db.execute("DELETE FROM xiongyang.t_cs_cases_src where f_site_id = 26")
    # fetch_srouce('http://bbs.gter.net/forum-1010-3.html')
