# -*- coding: utf-8 -*-

from web import Router, Application
from webob import Response
from functools import wraps
from base64 import b64decode
from webob.exc import HTTPUnauthorized

router = Router()

def authenticated(fn): #基于http basic的一种验证方式，当然也可以用json web token来验证。
    @wraps(fn)
    def wrap(ctx, request):
        header = request.headers.get('Authorization') # Authorization: Basic Y29teW46cGFzcw==
        print(header)
        if header is None:
            raise HTTPUnauthorized()
        user, password = b64decode(header.split()[-1].encode()).decode().split(':')
        if user == 'jkzhao' and password == 'pass':
            request.user = user
            return fn(ctx, request)
        raise HTTPUnauthorized()
    return wrap

@router.route('/')
@authenticated # 如果浏览器输入http://127.0.0.1:3000/，没有传递认证用户和密码，页面就会显示 401 Unauthorized
def main(ctx, request): # 如果用chrome浏览器输入http://jkzhao:pass@127.0.0.1:3000/，有可能还是报401，打开shell终端，curl http://jkzhao:pass@127.0.0.1:3000/ # chrome现在是必须是https才让传这个头部
    return Response('hello world')

app = Application()
app.add_router(router)

if __name__ == '__main__':
    from wsgiref.simple_server import make_server

    server = make_server('0.0.0.0', 3000, app)  # 创建一个容器
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
