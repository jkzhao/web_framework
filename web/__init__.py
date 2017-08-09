# -*- coding: utf-8 -*-

import re
from collections import namedtuple
from webob import Request, Response # webob里封装了Request和Response
from webob.dec import wsgify # webob提供的装饰器，可以将代码大大简化
from webob.exc import HTTPNotFound
#from webob.exc import * # 引入webob所有的Exception

# 这里我们把 str 分成3种：1.str 所有不包含 / 的字符；2.word 字母、数字和下划线；3.any：任意字符
PATTERNS = {
    'str': '[^/].+', # 不包含 /，且至少一个字符
    'word': '\w+',
    'any': '.+', # 任意字符，但是至少包含一个
    'int': '[+-]?\d+', # int类型的正则表达式，可选的+或-号，后面是数字
    'float': '[+-]?\d+\.\d+' # float类型正则表达式
}

CASTS= {
    'str': str,
    'word': str,
    'any': str,
    'int': int,
    'float': float
}

Route = namedtuple('Route', ['pattern', 'methods', 'casts', 'handler'])

class Router:
    def __init__(self, prefix='', domain=None):
        self.routes = []
        self.domain = domain
        self.prefix = prefix

    def _route(self, rule, methods, handler):
        pattern, casts = self._rule_parse(rule)
        self.routes.append(Route(pattern, methods, casts, handler))

    def _rule_parse(self, rule):
        pattern = []
        spec = []
        casts = {}
        is_spec = False

        # @r2.route('/hello/{name}/{age:int}') # /hello/(?P<name>[^/]+)/(?P<age>[+-]?\d+)$
        for c in rule:
            if c == '{' and not is_spec:
                is_spec = True # 开始spec字段
            elif c == '}' and is_spec:
                is_spec = False # 结束spec字段
                # TODO process spec
                name, p, c = self._spec_parse(''.join(spec))
                spec = []
                pattern.append(p)
                casts[name] = c
            elif is_spec:
                spec.append(c)
            else:
                pattern.append(c)

        return '{}$'.format(''.join(pattern)), casts

    def _spec_parse(self, src):
        tmp = src.split(':')  # spec= age:int
        if len(tmp) > 2:
            raise Exception('error pattern')
        name = tmp[0]
        type = 'str'  # type默认为str类型的
        if len(tmp) == 2:
            type = tmp[1]
        pattern = '(?P<{}>{})'.format(name, PATTERNS[type])
        return name, pattern, CASTS[type]

    # def route(self, pattern, methods=None):
    #     if methods is None:
    #         methods = ('GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTION')
    #
    #     def dec(fn): # fn就是传递进来的handler
    #         self._route(pattern, methods, fn)
    #         return fn # 这里不需要执行fn，原样返回就行了
    #
    #     return dec
    def route(self, rule, methods=None):
        if methods is None:
            methods = ('GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTION')

        def dec(fn): # fn就是传递进来的handler
            self._route(rule, methods, fn)
            def wrap(*args, **kwargs):
                return fn # 这里不需要执行fn，原样返回就行了
            return wrap

        return dec

    def _domian_match(self, request):
        return self.domain is None or re.match(self.domain, request.host)

    def _prefix_match(self, request):
        return request.path.startswith(self.prefix)

    def match(self, request):
        if self._domian_match(request) and self._prefix_match(request):
            for route in self.routes:
                if request.method in route.methods:
                    m = re.match(route.pattern, request.path.replace(self.prefix, '', 1))
                    if m:
                        request.args = {}
                        for k, v in m.groupdict().items():
                            request.args[k] = route.casts[k](v)
                        return route.handler

class Application:
    def __init__(self, **options): # options这里作为全局的设置，传递给views
        self.routers = []
        self.options = options

    def add_router(self, router):
        self.routers.append(router)

    @wsgify
    def __call__(self, request):
        for router in self.routers:
            handler = router.match(request)
            if handler:
                return handler(self, request)
        raise HTTPNotFound(detail='no handler match')
