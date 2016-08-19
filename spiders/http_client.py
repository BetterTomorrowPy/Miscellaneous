# -*- coding: utf-8 -*-

import weakref
import functools

# from tornado.httpclient import AsyncHTTPClient
from tornado import httputil

from tornado.ioloop import IOLoop
from tornado.util import Configurable
from tornado.concurrent import TracebackFuture


class HTTPClient(object):
    """tornado httpclient srouce."""
    def __init__(self, async_client_class=None, **kwargs):
        self._io_loop = IOLoop(make_current=False)
        if async_client_class is None:
            async_client_class = AsyncHTTPClient
        self._async_client = async_client_class(self._io_loop, **kwargs)
        self._closed = False

    def __del__(self):
        self.close()

    def close(self):
        if not self._closed:
            self._async_client.close()
            self._io_loop.close()
            self._closed = True

    def fetch(self, request, **kwargs):
        response = self._io_loop.run_sync(functools.partial(
            self._async_client.fetch, request, **kwargs))
        return response


class AsyncHTTPClient(Configurable):
    @classmethod
    def configurable_base(cls):
        return AsyncHTTPClient

    @classmethod
    def configurable_default(cls):
        from tornado.simple_httpclient import SimpleAsyncHTTPClient
        return SimpleAsyncHTTPClient

    @classmethod
    def _async_clients(cls):
        attr_name = '_async_client_dict_' + cls.__name__
        if not hasattr(cls, attr_name):
            setattr(cls, attr_name, weakref.WeakKeyDictionary())
        return getattr(cls, attr_name)

    def __new__(cls, io_loop=None, force_instance=False, **kwargs):
        io_loop = io_loop or IOLoop.current()
        if force_instance:
            instance_cache = None
        else:
            instance_cache = cls._async_clients()
        if instance_cache is not None and io_loop in instance_cache:
            return instance_cache[io_loop]
        instance = super(AsyncHTTPClient, cls).__new__(cls, io_loop=io_loop, **kwargs)

        instance._instance_cache = instance_cache
        if instance_cache is not None:
            instance_cache[instance.io_loop] = instance
        return instance

    def initialize(self, io_loop=None, defaults=None):
        self.io_loop = io_loop
        self.defaults = dict(HTTPRequest._DEFAULTS_)
        if defaults is not None:
            self.defaults.update(defaults)
        self._closed = False

    def close(self):
        if self._closed:
            return
        self._closed = True
        if self._instance_cache is not None:
            if self._instance_cache.get(self.io_loop) is not self:
                raise RuntimeError("inconsistent AsyncHTTPClient cache")
            del self._instance_cache[self.io_loop]

    def fetch(self, request, callback=None, raise_error=True, **kwargs):
        if self._closed:
            raise RuntimeError('fetch() called on closed AsyncHTTPClient')
        if not isinstance(request, HTTPRequest):
            request = HTTPRequest(url=request, **kwargs)
        else:
            if kwargs:
                raise ValueError("kwargs can't be used if request is an HTTPRequest object"

        request.headers = httputil.HTTPHeaders(request.headers)
        request = _RequestProxy(request, self.defaults)
        future = TracebackFuture()
        if callback is not None:
            import time
            from tornado import stack_context
            from tornado.web import HTTPError
            callback = stack_context.wrap(callback)

            def handle_future(future):
                exc = future.exception()
                if isinstance(exc, HTTPError) and exc.response is not None:
                    response = exc.response
                elif exc is not None:
                    response = HTTPResponse(
                        request, 599, error = exc, 
                        request_time=time.time() - request.start_time
                        )
                else:
                    response = future.result()
                self.io_loop.add_callback(callback, response)
            future.add_done_callback(handle_future)

        def handle_response(response):
            if raise_error and response.error:
                future.set_exception(response.error)
            else:
                future.set_result(response)
        self.fetch_impl(request, handle_response)
        return future

    def fetch_impl(self, request=None, callback=None):
        raise NotImplementedError()

    @classmethod
    def configure(cls, impl, **kwargs):
        super(AsyncHTTPClient, cls).configure(impl, **kwargs)


def async_fetch():
    """"""
    # response = self._io_loop.run_sync(functools.partial(
    #         self._async_client.fetch, request, **kwargs))
    # return response
    from tornado.httpclient import AsyncHTTPClient as AHC
    from tornado.gen import coroutine
    from tornado.ioloop import IOLoop
    client = AHC()

    @coroutine
    def handle_fetch():
        response = yield client.fetch('http://www.betteredu.net/star/')
        print(response.body)

    IOLoop().current().run_sync(handle_fetch)
