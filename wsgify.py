# -*- coding: utf-8 -*-

from webob import Request
from functools import wraps

def wsgify(fn):
    '''wsgify装饰器简单实现'''
    @wraps(fn)
    def wrap(environ, start_response):
        request = Request(environ)
        resp = fn(request)
        return resp(environ, start_response)

    return wrap