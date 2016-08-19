# -*- coding: utf-8 -*-

from tornado.testing import *


class APITestCase(AsyncTestCase):
    """"""
    @gen_test
    def test_http_fetch(self):
        client = AsyncHTTPClient(self.io_loop)
        response = yield client.fetch('http://baidu.com')
        # print(response.body)
        self.assertIn("FriendFeed", response.body)


api = APITestCase()
api.test_http_fetch()