# -*- coding: utf-8 -*-

'''
webob：不是web框架，只是做以面向对象的方式封装wsgi协议
'''
import re
from html import escape
from webob import Request, Response # webob里封装了Request和Response
                                    # https://docs.pylonsproject.org/projects/webob/en/stable/reference.html#request
                                    # https://docs.pylonsproject.org/projects/webob/en/stable/reference.html#response

from webob.dec import wsgify # webob提供的装饰器，可以将代码大大简化。这个装饰器拦截了wsgi的输入，也修改了它的返回

@wsgify
def application(request): #但是这样每增加一个url，就得修改application函数
    if re.match(r'/favicon.ico$', request.path): # 正则表达式实现路由规则
    # if request.path == '/favicon.ico': # 图片，rb二进制形式打开
        return favicon(request)
    if re.match(r'/hello$', request.path):
    # if request.path.startswith('/hello'):
        return hello(request)
    if re.match(r'/$', request.path):
    # if request.path.startswith('/'):
        return main(request)

def main(request):
    return Response('this is man page')

def hello(request):
    name = request.params.get('name', 'anonymous')
    body = 'hello {}'.format(escape(name))
    return Response(body)

def favicon(request):
    with open('./favicon.ico', 'rb') as f:
        response = Response(body=f.read(), content_type='image/x-icon')
        return response

# def application(environ, start_response):
#     '''利用第三方的轮子'''
#     request = Request(environ)
#     name = request.params.get('name', 'anonymou， s') # webob里获取params，如果有多个值，会返回第一个
#     body = 'hello {}'.format(escape(name))
#
#     return Response(body)(environ, start_response)

if __name__ == '__main__':
    from wsgiref.simple_server import make_server

    server = make_server('0.0.0.0', 3000, application) # 创建一个容器
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()



