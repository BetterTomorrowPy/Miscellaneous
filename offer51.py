# -*- coding: utf-8 -*-

import re
import requests

from pyspider.libs.base_handler import *


class Handler(BaseHandler):
    crawl_config = {
    }

    def on_start(self):
        self.crawl('http://www.51offer.com/school/index.html', callback=self.index_page)

    @config(age=10 * 24 * 60 * 60)
    def index_page(self, response):
        for each in response.doc('#scountry a').items():
            print(each)
            self.crawl(each.attr.href, callback=self.fetch_coll)
            # self.crawl(each.attr.href, callback=self.detail_page)

    @config(priority=2)
    def fetch_coll(self, response):
        """"""
        uris = set()
        for a in response.doc('.schoolLabel li a').items():
            uris.add(a.attr.href)
        # print(uris)
        for u in uris:
            # print(u)
            self.crawl(u, callback=self.coll_home)
        _next = response.doc('.next')
        if _next:
            self.crawl(_next.attr.href, callback=self.fetch_coll)

    @config(priority=2)
    def coll_home(self, response):
        """"""
        # college`s photo uri
        photo_uri = ''
        p = re.search(r'/school/photo(.+)\.html', response.text)
        if p:
            photo_uri = p.group(0)
        
        # college`s specialty uri
        specialty_uri = ''
        p = re.search(r'/school/specialty(.+)\.html', response.text)
        if p:
            specialty_uri = p.group(0)
        
        # location
        _location = [l.text() for l in response.doc('.mete span label').items()]
        location = ','.join(_location)
        print(location)
        
        info = ''
        _info = response.doc('.summarize .text-content')
        if _info:
            info = _info.text()
            # print('-' * 8)
            print(info)
            
        # logo
        logo = ''
        _logo = response.doc('.school-logo img')
        if _logo:
            logo = _logo.attr.src
        print(logo)
            
        # name
        name = response.doc('.school-info h2')
        if name:
            print(name.text())
        cname = response.doc('.school-info h1')
        if cname:
            print(cname.text())
            
        # coll uri
       
        _puri = 'http://www.51offer.com' + photo_uri
        _suri = 'http://www.51offer.com' + specialty_uri
        
        
        r = requests.get(_puri)
        _puris = list()
        p = re.compile(r'"picture_url":"(.+?)"')
        uris = p.findall(r.text)
        
        # def photo_specialty():
        #     _fetcher = HTTPClient()
        #     _response = _fetcher.fetch(_puri)
        #     p = re.compile(r'"picture_url":"(.+?)"')
        #     uris = p.findall(_response.body.decode('utf-8'))
        #     if uris:
        #         return set(uris)
        #     return {}
        
        # r = photo_specialty()
            
        # print(uris)
        # r = self.crawl(_puri, callback=self.detail_page)
        return {
            'name': name.text(), 
            'cname': cname.text(), 
            'location': location, 
            'logo': logo, 
            'photo_uris': uris, 
            'coll_uri': response.url, 
            'level': 1,
            'info': info
        }
        
        
    @config(priority=2)
    def detail_page(self, response):
         p = re.compile(r'"picture_url":"(.+?)"')
         uris = p.findall(response.text)
         if uris:
            return uris 
         return # -*- coding: utf-8 -*-

import re
import requests

from pyspider.libs.base_handler import *


class Handler(BaseHandler):
    crawl_config = {
    }

    def on_start(self):
        self.crawl('http://www.51offer.com/school/index.html', callback=self.index_page)

    @config(age=10 * 24 * 60 * 60)
    def index_page(self, response):
        for each in response.doc('#scountry a').items():
            print(each)
            self.crawl(each.attr.href, callback=self.fetch_coll)
            # self.crawl(each.attr.href, callback=self.detail_page)

    @config(priority=2)
    def fetch_coll(self, response):
        """"""
        uris = set()
        for a in response.doc('.schoolLabel li a').items():
            uris.add(a.attr.href)
        # print(uris)
        for u in uris:
            # print(u)
            self.crawl(u, callback=self.coll_home)
        _next = response.doc('.next')
        if _next:
            self.crawl(_next.attr.href, callback=self.fetch_coll)

    @config(priority=2)
    def coll_home(self, response):
        """"""
        # college`s photo uri
        photo_uri = ''
        p = re.search(r'/school/photo(.+)\.html', response.text)
        if p:
            photo_uri = p.group(0)
        
        # college`s specialty uri
        specialty_uri = ''
        p = re.search(r'/school/specialty(.+)\.html', response.text)
        if p:
            specialty_uri = p.group(0)
        
        # location
        _location = [l.text() for l in response.doc('.mete span label').items()]
        location = ','.join(_location)
        print(location)
        
        info = ''
        _info = response.doc('.summarize .text-content')
        if _info:
            info = _info.text()
            # print('-' * 8)
            print(info)
            
        # logo
        logo = ''
        _logo = response.doc('.school-logo img')
        if _logo:
            logo = _logo.attr.src
        print(logo)
            
        # name
        name = response.doc('.school-info h2')
        if name:
            print(name.text())
        cname = response.doc('.school-info h1')
        if cname:
            print(cname.text())
            
        # coll uri
       
        _puri = 'http://www.51offer.com' + photo_uri
        _suri = 'http://www.51offer.com' + specialty_uri
        
        
        r = requests.get(_puri)
        _puris = list()
        p = re.compile(r'"picture_url":"(.+?)"')
        uris = p.findall(r.text)
        
        # def photo_specialty():
        #     _fetcher = HTTPClient()
        #     _response = _fetcher.fetch(_puri)
        #     p = re.compile(r'"picture_url":"(.+?)"')
        #     uris = p.findall(_response.body.decode('utf-8'))
        #     if uris:
        #         return set(uris)
        #     return {}
        
        # r = photo_specialty()
            
        # print(uris)
        # r = self.crawl(_puri, callback=self.detail_page)
        return {
            'name': name.text(), 
            'cname': cname.text(), 
            'location': location, 
            'logo': logo, 
            'photo_uris': uris, 
            'coll_uri': response.url, 
            'level': 1,
            'info': info
        }
        
        
    @config(priority=2)
    def detail_page(self, response):
         p = re.compile(r'"picture_url":"(.+?)"')
         uris = p.findall(response.text)
         if uris:
            return uris 
         return {}