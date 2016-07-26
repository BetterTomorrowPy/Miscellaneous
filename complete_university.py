# -*- coding: utf-8 -*-
import re

from requests import Session
from bs4 import BeautifulSoup
from torndb import Connection
# from motor.motor_asyncio import AsyncIOMotorClient

db = Connection(host='', database='', 
                user='', password='')

fetcher = Session()
uri = 'http://www.thecompleteuniversityguide.co.uk/league-tables/rankings?'

headers = {
    'Host': 'www.thecompleteuniversityguide.co.uk', 
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0', 
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 
    'Referer': 'http://www.thecompleteuniversityguide.co.uk/league-tables/rankings?'
}


def main():
    """"""
    r = fetcher.get(url=uri, headers=headers, timeout=15)
    if 200 != r.status_code:
        print('Request Error.')
        return
    get_per_year('http://www.thecompleteuniversityguide.co.uk/league-tables/rankings?y=2017')
    
    page = BeautifulSoup(r.content, 'html.parser')
    # print(page.prettify())
    a_tags = page.select('a')
    for a in a_tags:
        year = re.match(r'\?y=(\d+)', a.get('href'))
        if year:
            _uri = uri + year.group(0)[1:]
            get_per_year(_uri)
        # print(a.get('href'))
        

def get_per_year(uri=''):
    """"""
    print('>>>', uri)
    if not uri:
        return
    r = fetcher.get(url=uri, headers=headers, timeout=15)
    if r.status_code != 200:
        print('Request url {} failed.'.format(uri))
        return
    page = BeautifulSoup(r.content, 'html.parser')
    urls = page.select('a[href^="?s="]')
    for u in urls:
        href = u.get('href')
        name = u.get_text()
        r_name = 'Complete University ' + name
        _sql = "SELECT id FROM `xiongyang`.`t_rank_list` WHERE f_name = '{}'".format(r_name)
        try:
            r_id = db.get(_sql)
            if not r_id:
                result = db.execute("INSERT INTO `xiongyang`.`t_rank_list` (`f_type_idx`, `f_name`, `f_info`, `country`, `f_country_id`, `f_dm1`, `f_dm2`, `f_dm3`, `f_dm4`, `f_dm5`, `updatetime`) VALUES ('2', '{}', '--', '英国', '4165', 'Entry Standards', 'Student Satisfaction', 'Research Quality', 'Graduate Prospects', 'Overall Score', '2016-07-26 16:56:03')".format(r_name))
                r_id = result
            print(r_id)
        except:
            print('----')
            continue

        if href == '?s=Arts%2fMusic+Institutions&y=2017':
            print('*', 's=Arts%2fMusic+Institutions&y=2017')
            # diao yong ziji.
            continue
        # print(href[1:])
        _uri = uri + href[1:]
        try:
            get_table(r_id.get('id'), _uri)
            print('--------')
        except:
            print(_uri, 'failed')
            continue


def get_table(r_id=0, uri='http://www.thecompleteuniversityguide.co.uk/league-tables/rankings?y=2017'):
    """"""
    if not uri:
        # 无趣
        return
    year = re.search(r'y=(\d+)', uri).group(1)
    # print(year)

    r = fetcher.get(url=uri, headers=headers, timeout=15)
    if r.status_code != 200:
        print('Request url {} failed.'.format(uri))
        return
    page = BeautifulSoup(r.content, 'html.parser')
    table = page.find('table', attrs={'class': 'leagueTable hoverHighlight narrow'})
    trs = table.select('tbody > tr')
    for tr in trs:
        tds = tr.select('td')
        tds_list = list()
        tds_dict = dict()
        for td in tds:
            tds_list.append(td.get_text().strip().replace("'", "`"))
        if len(tds_list) != 13:
            continue
        # print(tds_list)
        year_0 = '{}'.format(year)
        year_1 = 'CUG Rank {}'.format(int(year) - 1)

        tds_dict[year] = tds_list[0]
        tds_dict[year_1] = tds_list[1]
        tds_dict["University Name"] = tds_list[2]
        tds_dict["Entry Standards"] = tds_list[3]
        tds_dict["Student Satisfaction"] = tds_list[5]
        tds_dict["Research Quality"] = tds_list[7]
        tds_dict["Graduate Prospects"] = tds_list[9]
        tds_dict["Overall Score"] = tds_list[11]
        
        insert_data(year, r_id, tds_dict)
        

def insert_data(year, r_id, data):
    """"""
    sql = "INSERT INTO `xiongyang`.`t_rank` (f_rank_idx, f_rank_list_id, f_country_id, tmp_ins_name, tmp_ins_ename, f_year, f_info, f_dm1, f_dm2, f_dm3, f_dm4, f_dm5) \
VALUES ({0}, {1}, 4165, '{2}', '{3}', '{4}', '{5}', '{6}', '{7}', '{8}', '{9}', '{10}')"
    year = str(year)
    _sql = sql.format(data[year], r_id, data["University Name"], data["University Name"], year, '', 
        data["Entry Standards"], data["Student Satisfaction"], data["Research Quality"], 
        data["Graduate Prospects"], data["Overall Score"])
    # print(_sql)
    try:
        result = db.execute(_sql)
        print('>', result)
    except:
        print('Execute failed: ', _sql)
        return


if __name__ == '__main__':
    print('running ... ')
    main()
    # get_table()




