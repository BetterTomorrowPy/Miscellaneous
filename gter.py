#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Created on 2016-08-10 07:38:12
# Project: gter
import re

from pyspider.libs.base_handler import *


class Handler(BaseHandler):
    crawl_config = {
    }

    @every(minutes=24 * 60)
    def on_start(self):
        self.crawl('http://bbs.gter.net/forum.php?gid=454', callback=self.index_page)

    @config(age=10 * 24 * 60 * 60)
    def index_page(self, response):
        for each in response.doc('table[class="fl_tb"] tr h2 a').items():
            # print(each.attr.href)
            self.crawl(each.attr.href, callback=self.forum_page)

    def forum_page(self, response):
        """"""
        for each in response.doc('tbody[id^="normalthread"] .new .xst').items():
            self.crawl(each.attr.href, callback=self.detail_page)

        _n = response.doc('.nxt')
        if _n:
            print(_n.attr.href)
            self.crawl(_n.attr.href, callback=self.forum_page)

    def detail_page(self, response):
        """"""
        _tables = response.doc('table[class^="cgtl"]').items()
        # _tables = response.doc('table[summary^="offer"] tr').items()
        if _tables:
            for t in _tables:
                p = re.compile(r'</?\w+[^>]*>')
                # p = re.search(r'</?\w+[^>]*>', t.outer_html())
                print(p.findall(t.outer_html()))
                # print(p.group(0))
                
            
            return {
                "url": response.url,
                "title": response.doc('title').text(),
            }
