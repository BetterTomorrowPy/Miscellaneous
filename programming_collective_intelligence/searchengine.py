# -*- coding: utf-8 -*-
"""集体智慧编程chapter4"""
from tornado.httpclient import AsyncHTTPClient


class Crawler(object):
    """"""
    def __init__(self, db=''):
        pass

    def __del__(self):
        pass

    def commit(self):
        pass

    def get_entry_id(self, table=None, field=None, value=None, create_new=True):
        return None

    def addto_index(self, url='', soup=None):
        print('Indexing {0}'.format(url))

    def get_text_only(self, soup=None):
        return None

    def separate_words(self, text):
        return None

    def isindexed(self, url=''):
        return False

    def add_link_ref(self, url='', url_from='', url_to='', link_text=''):
        pass

    def crawl(self, pages=None, depth=2):
        pass

    def create_index_tables(self):
        pass