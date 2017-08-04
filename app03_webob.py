# -*- coding: utf-8 -*-

'''
webob：不是web框架，只是做以面向对象的方式封装wsgi协议
'''
from html import escape
from webob import Request, Response # webob里封装了Request和Response
                                    # https://docs.pylonsproject.org/projects/webob/en/stable/reference.html#request
                                    # https://docs.pylonsproject.org/projects/webob/en/stable/reference.html#response

def application(environ, start_response):
    '''利用第三方的轮子'''
    request = Request(environ)
    name = request.params.get('name', 'anonymous') # webob里获取params，如果有多个值，会返回第一个
    body = 'hello {}'.format(escape(name))

    return Response(body)(environ, start_response)

if __name__ == '__main__':
    from wsgiref.simple_server import make_server

    server = make_server('0.0.0.0', 3000, application) # 创建一个容器
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()

