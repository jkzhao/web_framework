# -*- coding: utf-8 -*-

'''
路由处理
'''
import re
from collections import namedtuple
from html import escape
from webob import Request, Response # webob里封装了Request和Response
from webob.dec import wsgify # webob提供的装饰器，可以将代码大大简化

# @wsgify
# def application(request): #但是这样每增加一个url，就得修改application函数
#     if re.match(r'/favicon.ico$', request.path): # 正则表达式实现路由规则
#     # if request.path == '/favicon.ico': # 图片，rb二进制形式打开
#         return favicon(request)
#     if re.match(r'/hello$', request.path):
#     # if request.path.startswith('/hello'):
#         return hello(request)
#     if re.match(r'/$', request.path):
#     # if request.path.startswith('/'):
#         return main(request)

Route = namedtuple('Route', ['pattern', 'methods', 'handler'])

class Application:
    def __init__(self, **options): # options这里作为全局的设置，传递给views
        self.routes = []
        self.options = options

    def _route(self, pattern, methods, handler):
        self.routes.append(Route(pattern, methods, handler))

    # def route(self, pattern, methods=None):
    #     if methods is None:
    #         methods = ('GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTION')
    #
    #     def dec(fn): # fn就是传递进来的handler
    #         self._route(pattern, methods, fn)
    #         return fn # 这里不需要执行fn，原样返回就行了
    #
    #     return dec
    def route(self, pattern, methods=None):
        if methods is None:
            methods = ('GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTION')

        def dec(fn): # fn就是传递进来的handler
            self._route(pattern, methods, fn)
            def wrap(*args, **kwargs):
                return fn # 这里不需要执行fn，原样返回就行了
            return wrap

        return dec

    @wsgify
    def __call__(self, request):
        for route in self.routes: # 一个应用不会有太多的route，这里查询效率不会低的
            if request.method in route.methods:
                m = re.match(route.pattern, request.path)
                if m:
                    request.args = m.groupdict()
                    return route.handler(self, request)


# 上面都是框架代码，下面是业务代码
# app = Application()
app = Application(debug=True) # 传递全局的参数给handler，比如数据库连接

@app.route(r'/$') # 装饰器路由
def main(app, request):
    return Response('this is man page')

@app.route(r'/hello/(?P<name>\w+)$') # 传递方式变为 127.0.0.1:3000/hello/jkzhao 这样就可以通过path来传递参数了。Django url就是利用这种正则表达式
def hello(app, request):
    if app.options.get('debug'):
        for k, v in request.headers.items():
            print('{} ==> {}'.format(k, v))
    # name = request.params.get('name', 'anonymous') # 传递方式是 127.0.0.1:3000/hello?name=jkzhao
    body = 'hello {}'.format(escape(request.args.get('name')))
    return Response(body)

@app.route(r'/favicon.ico$')
def favicon(app, request):
    with open('./favicon.ico', 'rb') as f:
        response = Response(body=f.read(), content_type='image/x-icon')
        return response

if __name__ == '__main__':
    from wsgiref.simple_server import make_server # 是不是单线程要看容器，这就是个单线程容器

    # 实现了装饰器route，就不用下面的方式了
    # application = Application()
    # application.route(r'/favicon.icon$', favicon)
    # application.route(r'/hello$', hello)
    # application.route(r'/$', main)

    server = make_server('0.0.0.0', 3000, app) # 创建一个容器
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()



