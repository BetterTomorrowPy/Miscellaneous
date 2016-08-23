
#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2016-08-23 01:35:17
# Project: nihao
import re

from pyspider.libs.base_handler import *



class Handler(BaseHandler):
    crawl_config = {
        'headers': {
        'Host': 'school.nihaowang.com', 
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0', 
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 
        'Referer': 'http://school.nihaowang.com/175-0-0-0-0-0-0-0-0-0-0-2-2-5-0-0-0-0-0-0-3-01.html', 
        'Cookie': 'Hm_lvt_ebbf3ce31194ceb57b6daa1fcb0d1b19=1471509840,1471915288; CNZZDATA1851864=cnzz_eid%3D1131454011-1471508834-%26ntime%3D1471914541; ASP.NET_SessionId=igiovldwvnuipk2rfhu3f0ke; BAIDU_SSP_lcr=https://www.baidu.com/link?url=GI9K125i3rnLbxL2-kKs-1IPGbxogQGmaugpHPEfdPYALULzJxwxyPCC3YEO1CAv&wd=&eqid=c430c030002042300000000557bba50a; Hm_lpvt_ebbf3ce31194ceb57b6daa1fcb0d1b19=1471917344; sTitle=s; uHistory=2844%7C3738; currentUniversity=3738; SNSUserPassPort=logLoginID=108412F732BE7769&headImg=6072F863219AE0B6A43F283D422EA93E7F78580DF672D78FF67BD76C97136BF042641E5133CE72605190F6FD6A3271E90215C9FFB00423146CA242D97F871F9D5448C56FED82769AA4F75C41B7E3B69DF73A1288B514FC1278EDE6EBC388A435FAD592E916140420738ED68F05B0CD7C8A7E5B447BB91D14B6CD17DF82FB31CD&nickName=1DC128B3E79E4F0E&username=0FEC0767F10F99C8&email=BB3703AC122ED68621158ACF223C02F2&id=0FEC0767F10F99C8&msg=237558D98FC05769&um=D508F6B392C86500E4C72AF6D1789AAB1B30DC61CA934A58D30D09B942A5CD1D; jwjdstatus=1'
        }
    }

    @every(minutes=24 * 60)
    def on_start(self):
        self.crawl('http://school.nihaowang.com/', callback=self.index_page)

    @config(age=10 * 24 * 60 * 60)
    def index_page(self, response):
        # print(response.content)
        for each in response.doc('.teach_list_2 > a').items():
            print(each.attr.title.strip())
            print(each.attr.href)
            self.crawl(each.attr.href, callback=self.list_page)
            
    def list_page(self, response):
        """"""
        for each in response.doc('.college_content a').items():
            self.crawl(each.attr.href, callback=self.detail_page)
            
        _next = response.doc('.PagerIcon')
        if _next:
            self.crawl(_next.attr.href, callback=self.list_page)

    @config(priority=2)
    def detail_page(self, response):
        result = dict()
        p = re.search(r"LatLngs = [\'|\"](.+)[\'|\"]", response.text)
        # print(response.text)
        if p:
            # print(p.group(1))
            lat, lng = p.group(1).split(',')
            result['lat:'] = lat
            result['lng:'] = lng
        _logo = response.doc('#div_Logo > img')
        if _logo:
            result['logo'] = _logo.attr.src
            
        _name = response.doc('.school_hd_scName_cn')
        if _name:
            text = _name.text()
            # if '?' in text:
            #     text = text[:text.index('?')]
            p = re.search(r'\[(.+)\](.+)', text)
            
            result['country'] = p.group(1)
            result['coll'] = p.group(2)

        _ename = response.doc('.school_hd_scName_en')
        if _ename:
            result['eg_name'] = _ename.text().strip()

        # print(dir(_intro))
        _intro = response.doc('.intro #introInfo2')
        if _intro:
            # print(dir(response.etree.cssselect('.intro #introInfo2')[0]))
            _intro_text = response.etree.cssselect('.intro #introInfo2')[0].text.strip()
            result['intro'] = _intro_text
        
        imgs = list()
        for _i in response.doc('#focus ul li img').items():
            imgs.append(_i.attr.src1)
        result['imgs'] = imgs
            
        return result
