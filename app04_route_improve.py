# -*- coding: utf-8 -*-

'''
路由完善-subroute：
    如果是非常大型的应用，可能根据三级域名做不同的路由，根据的path的前缀做不同的处理，这就是 子路由 的概念。
    在flask中有 蓝图 的概念，也就是子路由的概念。

    三级域名：
           一个完整的域名由二个或二个以上部分组成，各部分之间用英文的句号"."来分隔，
           最后一个"."的右边部分称为顶级域名（TLD，）顶级域名“.”的左边部分称为一级域名，一级域名"."的左边部分称为二级域名（SLD），二级域名的左边部分称为三级域名，
           以此类推，每一级的域名控制它下一级域名的分配。三级域名是形如“a.youa.baidu.com”的域名，可以当做是二级域名的子域名，特征为域名包含三个“.”，一般来说，三级域名都是免费的。

            形如：china.world.com/beijing，采取目录形式并且以“/”代替“.”的不能够称为三级域名，甚至不能称为域名，一般称之为域名下的“二级目录”。
'''
import re
from collections import namedtuple
from html import escape
from webob import Request, Response # webob里封装了Request和Response
from webob.dec import wsgify # webob提供的装饰器，可以将代码大大简化


Route = namedtuple('Route', ['pattern', 'methods', 'handler'])

class Router:
    def __init__(self, prefix='', domain=None):
        self.routes = []
        self.domain = domain
        self.prefix = prefix

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
                        request.args = m.groupdict()
                        return route.handler

class Application:
    def __init__(self, **options): # options这里作为全局的设置，传递给views
        self.routers = []
        self.options = options
    def add_router(self, router):
        self.routers.append(router)

    @wsgify
    def __call__(self, request):
        for router in self.routers: # 一个应用不会有太多的route，这里查询效率不会低的
            handler = router.match(request)
            if handler:
                return handler(self, request)


# 上面都是框架代码，下面是业务代码
# app = Application()
# app = Application(debug=True) # 传递全局的参数给handler，比如数据库连接

r1 = Router()
r2 = Router('/r2') # 前缀r2，127.0.0.1:3000/r2/hello/jkzhao
r3 = Router(domain='jinzhi.wisedu.com') # 需要修改hosts文件，配置ip地址和这个主机名相对应。但是改完之后，所有的就得用域名的方式访问

@r3.route(r'/$')
def main(app, request):
    return Response('this is man page')

@r2.route(r'/hello/(?P<name>\w+)$') # 传递方式变为 127.0.0.1:3000/hello/jkzhao 这样就可以通过path来传递参数了
def hello(app, request):
    body = 'hello {}'.format(escape(request.args.get('name')))
    return Response(body)

@r1.route(r'/favicon.ico$')
def favicon(app, request):
    with open('./favicon.ico', 'rb') as f:
        response = Response(body=f.read(), content_type='image/x-icon')
        return response

if __name__ == '__main__':
    from wsgiref.simple_server import make_server # 是不是单线程要看容器，这就是个单线程容器

    app = Application()
    app.add_router(r1)
    app.add_router(r2)
    app.add_router(r3)

    server = make_server('0.0.0.0', 3000, app) # 创建一个容器
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()


