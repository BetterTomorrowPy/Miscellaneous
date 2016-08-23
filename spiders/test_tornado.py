# -*- coding: utf-8 -*-

import time

from datetime import datetime
from tornado.testing import *


class APITestCase(AsyncTestCase):
    """"""
    @gen_test
    def test_http_fetch(self):
        client = AsyncHTTPClient(self.io_loop)
        response = yield client.fetch('http://baidu.com')
        # print(response.body)
        self.assertIn("FriendFeed", response.body)


# api = APITestCase()
# api.test_http_fetch()
def test_mktime():
	_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	ta = time.strptime(_now, '%Y-%m-%d %H:%M:%S')
	print(time.mktime(ta))

test_mktime()