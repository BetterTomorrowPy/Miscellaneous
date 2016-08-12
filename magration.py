# -*- coding: utf-8 -*-
""""""
import re
import json

from datetime import datetime
from torndb import Connection
from requests import Session

db_src = Connection(host='192.168.0.1', database='', 
                    user='', password='')
db_des = Connection(host='192.168.0.1', database='', 
                    user='', password='')
fetcher = Session()


def get_data():
    """"""
    rows = db_src.query('SELECT result FROM `offer_51`')
    if rows:
        for _r in rows[3:]:
            result = _r.get('result').decode('utf-8')
            # isinstance(result, str)
            jr = json.loads(result)
            # print(jr)
            try:
                down_img(jr)
            except:
                continue

def down_img(jr=None):
    """"""
    jrs = dict()
    rp = r'/?([a-z]*\d+\.[a-z]+)'
    _lp = re.search(rp, jr['logo'])
    if _lp:
        lp = _lp.group(1)
        _ph = '/2/logo/' + lp
        print(_ph)
        jrs['logo'] = _ph
        r = fetcher.get(jr['logo'])
        with open('2\\logo\\' + lp, 'wb') as fd:
            fd.write(r.content)
    pus = jr['photo_uris']
    phsl = list()
    for p in pus:
        _pu = re.search(rp, p)
        if _pu:
            r = fetcher.get(p)
            _pn = _pu.group(1)
            _pa = '/2/picture/' + _pn
            phsl.append(_pa)
            with open('2\\picture\\' + _pn, 'wb') as fd:
                fd.write(r.content)
    jrs['photo_uris'] = phsl
    location = jr['location']
    cc = location.split(',')
    if cc:
        jrs['country'] = cc[0]
        jrs['city'] = cc[1]
    info = jr['kv_info']
    _fy = list()
    for i in info:
        if '雅思' in i:
            jrs['ielts'] = i.replace('\xa0', '').replace('提高拿Offer概率', '').replace('免费测试雅思成绩', '').strip()
        elif '费' in i:
            _fy.append(i.replace('\xa0', ''))
        else:
            continue
    jrs['fy'] = ','.join(_fy)

    # print(jrs)
    jr.update(jrs)
    try:
        save_data(jr)
    except:
        print(jr)

def save_data(jr=None):
    """"""
    if not jr:
        return
    _now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    isql = "INSERT INTO `xiongyang`.`t_institution_source` (`f_site_id`, `f_country`, `ins_name`, `f_logo`, `ins_cname`, `f_site_url`, `f_level_id`, `f_city`, `f_intro`, `f_update`, `fee`, `performance`) VALUES ('2', %s, %s, %s, %s, %s, '4', %s, %s, %s, %s, %s)"
    try:
        iid = db_des.execute(isql, jr.get('country', ''), jr.get('name', ''), jr.get('logo', ''), 
            jr.get('cname', ''), jr.get('coll_uri', ''), jr.get('city', ''), jr.get('info', ''), 
            _now, jr.get('fy', ''), jr.get('ielts', ''))
        # iid = db_des.get('SELECT id FROM `xiongyang`.`t_institution_source` WHERE f_site_id = 2 AND ins_name = %s', jr.get('cname', ''))
    except:
        _iid = db_des.get('SELECT id FROM `xiongyang`.`t_institution_source` WHERE f_site_id = 2 AND ins_name = %s', jr.get('name', ''))
        iid = _iid.get('id', 0)
        db_des.execute('UPDATE `xiongyang`.`t_institution_source` SET f_logo = %s WHERE f_site_id = 2 AND id = %s', jr.get('logo', ''), str(iid))
    print('r > ', iid)
    if iid:
        for u in jr.get('photo_uris', []):
            try:
                pid = db_des.execute("INSERT INTO `xiongyang`.`t_institution_pic` (`f_path`, `f_type`, `f_ins_id`) VALUES (%s, '1', %s)", u, str(iid))
                print(pid)
            except:
                continue

if __name__ == "__main__":
    print('Running ... ')
    get_data()
    # db_des.execute("DELETE FROM xiongyang.t_institution_pic WHERE f_ins_id = 0")
