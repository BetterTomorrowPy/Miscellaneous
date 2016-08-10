# -*- coding: utf-8 -*-
"""Update zinch.cn data."""
import re
import time
import json

from datetime import datetime
from requests import Session
from bs4 import BeautifulSoup
from torndb import Connection
# from motor.motor_asyncio import AsyncIOMotorClient

db = Connection(host='', database='', 
                user='', password='')

fetcher = Session()

b_uri = 'http://www.zinch.cn/'
p_uri = 'http://www.zinch.cn/offer/ajax/more'

_headers = {
'Host': 'www.zinch.cn', 
'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0', 
'Accept': 'application/json, text/javascript, */*', 
'Content-Type': 'application/x-www-form-urlencoded', 
'X-Requested-With': 'XMLHttpRequest', 
'Referer': 'http://www.zinch.cn/offer'
}

_ssql = '''INSERT INTO `xiongyang`.`t_cs_students` (`f_site_id`, `f_country_id`, 
    `f_surname`, `f_name`, `stu_gpa`, `stu_gmat_gre`, `stu_sat_act`, `stu_toefl`
    , `stu_ielts`) VALUES (4, 1, '%s', '%s', '%s', '%s', '%s', '%s', '%s')'''
_csql = '''INSERT INTO `xiongyang`.`t_cs_cases` (`f_site_id`, `f_student_id`, 
    `f_app_type`, `app_ins_name`, `app_cos_name`, `tmp_admission`, `f_admitted_date`, 
    `updatetime`) VALUES (4, %d, '%s', '%s', '%s', '%s', '%s', '%s')'''

def fetch_offer(offset=0):
    """"""
    post_data = {
        'degree': '', 
        'schoolId': '', 
        'similar': None, 
        'start': offset, 
        'status': 0
    }
    try:
        r = fetcher.post(url=p_uri, data=post_data, headers=_headers)
        if 200 != r.status_code:
            with open('offset.txt', 'a') as fd:
                fd.write(offset, ',')
    except:
        time.sleep(8)
        fetch_offer(offset)
        return
    text = json.loads(r.text)
    content = text['content']
    page = BeautifulSoup(content, 'html.parser')
    # print(page.prettify())
    # return 
    offers = page.find_all('li', attrs={'class': 'clear'})
    
    if not offers:
        return
    for o in offers:
        # _info = dict()
        # c_div = o.select('div > div')
        # for div in c_div:
        #     print(div.encode('utf-8'))
        # student name
        name = o.select('.c-brief-name')[0].get_text().strip()
        if '+' in name:
            name = name.replace('+', '').strip()
            # print(name)

        # school item
        school_table = o.select('.c-schools')[0]
        if not school_table:
            continue
        school_item = list()
        theads = school_table.select('table > thead > tr > td')
        for td in theads[:-1]:
            text = td.get_text().strip()
            if text:
                school_item.append(text)
        
        # school info.
        tbody = school_table.select('table > tr')
        if not tbody:
            continue
        cases = list()
        for tr in tbody:
            _case = list()
            for td in tr.select('td')[:-1]:
                _case.append(td.get_text().strip())
            cases.append(_case)
        # print(school_item)
        # print(cases)

        slist = list()
        stlist = list()
        try:
            # 分数items
            c_test = o.select('.c-test')[0]
            spans = c_test.select('ul > li > span')
            for span in spans:
                slist.append(span.get_text().strip())

            # 分数result
            strongs = c_test.select('ul > li > strong')
            for strong in strongs:
                stlist.append(strong.get_text().strip())
        except:
            continue
        # print(slist)
        # print(stlist)
        try:
            deal_data(name, cases, slist, stlist)
        except:
            continue

        print('\n')


def deal_data(name='', cases=[], slist=[], stlist=[]):
    """"""
    _test = ('gpa', 'gmat', 'gre', 'sat', 'act', 'toefl', 'ielts')
    _info = dict()
    _schools = list()
    for case in cases:
        _schools.append({
            'coll': case[0], 
            'level': case[1], 
            'disc': case[2], 
            'result': case[3], 
            'time': case[4]
            })
    _info['name'] = name

    if 'GPA' in slist:
        gpa_index = slist.index('GPA')
        _info['gpa'] = stlist[gpa_index]
    if '雅思' in slist:
        ielts_index = slist.index('雅思')
        _info['ielts'] = stlist[ielts_index]
    if '托福' in slist:
        toefl_index = slist.index('托福')
        _info['toefl'] = stlist[toefl_index]
    if 'SAT总分' in slist:
        sat_index = slist.index('SAT总分')
        _info['sat'] = stlist[sat_index]
    if 'ACT' in slist:
        act_index = slist.index('ACT')
        _info['act'] = stlist[act_index]
    if 'GMAT' in slist:
        gmat_index = slist.index('GMAT')
        _info['gmat'] = stlist[gmat_index]
    if 'GRE总分' in slist:
        gre_index = slist.index('GRE总分')
        _info['gre'] = stlist[gre_index]

    # print(_schools)
    # print(_info)
    try:
        insert_data(_info, _schools)
    except:
        return


def insert_data(stu=None, schs=None):
    """"""
    if not stu:
        print('Value error. not student info.')
        return
    _sur_name = stu.get('name', '某同学')[:-2]
    _name = stu.get('name', '某同学')[-2:]
    # `stu_gpa`, `stu_gmat_gre`, `stu_sat_act`, `stu_toefl`
    _gpa = stu.get('gpa', '')
    _toefl = stu.get('toefl', '')
    _ielts = stu.get('_ielts', '')

    _gmat_gre = ''
    if stu.get('gmat', '') and stu.get('gre', ''):
        _gmat_gre = stu.get('gmat', '')
    elif stu.get('gmat', ''):
        _gmat_gre = stu.get('gmat', '')
    elif stu.get('gre', ''):
        _gmat_gre = stu.get('gre', '')

    _sat_act = ''
    if stu.get('sat', '') and stu.get('act', ''):
        _gmat_gre = stu.get('sat', '')
    elif stu.get('sat', ''):
        _gmat_gre = stu.get('sat', '')
    elif stu.get('act', ''):
        _gmat_gre = stu.get('act', '')

    _now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    s_sql = _ssql % (_sur_name, _name, _gpa, _gmat_gre, _sat_act, _toefl, _ielts)
    # print(s_sql)
    try:
        _result = db.execute(s_sql)
        print('student: ', _result)
    except:
        _result = 0
   
    for sch in schs:
        # print(sch)
        _time = sch.get('time', '2016/01/01')
        if len(_time) == 4:
            _time += '/01/01'
        elif len(_time) != 10:
            _time = '2016/01/01'
        c_sql = _csql % (_result, sch['level'], sch['coll'].replace("'", "`"), sch['disc'].replace("'", "`"), 
            sch['result'], _time, _now)
        # print(' ', c_sql)
        try:
            print('c > ', db.execute(c_sql))
        except:
            try:
                _c_sql = _csql % (_result, sch['level'], sch['coll'].replace("'", "`"), sch['disc'].replace("'", "`"), 
                sch['result'], '2013/01/01', _now)
                # print(_c_sql)
                print('c * ', db.execute(_c_sql))
            except:
                with open('zinch_offer_log.txt', 'a') as fd:
                    fd.write(c_sql)


def main():
    """"""
    # 15690
    for i in range(0, 15690):
        print('-' * 16)
        _offset = 20 * i
        # try:
        print('Page number :{}'.format(i))
        fetch_offer(_offset)
        time.sleep(5)
        # except:
        #     continue

if __name__ == '__main__':
    print('running ... ')
    main()
    # db.execute("DELETE FROM xiongyang.t_cs_students WHERE f_site_id = 4")
    # db.execute("DELETE FROM xiongyang.t_cs_cases where f_site_id = 4")
