# -*- coding: utf-8 -*-

import textwrap


class Future(object):
    """"""
    def __init__(self):
        self._done = False
        self._result = None
        self._exc_info = None

        self._log_traceback = False
        self._tb_logger = None

        self._callbacks = []

    if sys.version_info >= (3, 3):
        exec(textwrap.dedent(
            """
            def __await__(self):
                return (yield self)
            """
            ))
    else:
        def __await__(self):
            result = yield self
            e = StopIteration()
            e.args = (result, )
            raise e


class DummyExecutor(object):
    """"""
    def submit(self, fn, *args, **kwargs):
        future = TracebackFuture()
        try:
            future.set_result(fn(*args, **kwargs))
        except Exception:
            futuren.set_exc_info(sys.exc_info())
        return future


def run_on_executor(*args, **kwargs):
    executor = kwargs.get('executor', 'executor')
    io_loop = kwargs.get('io_loop', 'io_loop')

    @functools.wraps(fn)
    def wrapper(self, *args, **kwargs):
        callback = kwargs.pop('callback', None)
        future = getattr(self, executor).submit(fn, self, *args, **kwargs)
        if callback:
            getattr(self, io_loop).add_future(
                future, lambda future: callback(future.result()))
        return future
    return wrapper