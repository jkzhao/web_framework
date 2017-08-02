# -*- coding: utf-8 -*-

# WSGI demo
'''
封装request对象和response对象
'''
from urllib.parse import parse_qs
from html import escape
import os

class Request:
    def __init__(self, environ):
        self.params = parse_qs(environ.get('QUERY_STRING'))
        self.path = environ.get('PATH_INFO')
        self.method = environ.get('REQUEST_METHOD')
        self.body = environ.get('wsgi.input') # GET请求是没有body的，可以用postman来测试POST请求时的body，或者用curl -XPOST http://127.0.0.1:3000 -d '{"name":"jkzhao"}'

        self.headers = {} # 可以是字典，也可以是列表
        server_env = os.environ
        for k, v in environ.items():
            if k not in server_env.keys():
                self.headers[k.lower()] = v



def application(environ, start_response):
    request = Request(environ)
    name = request.params.get('name', ['anonymous'])[0]
    body = 'hello {}'.format(escape(name))

    status = '200 OK'
    headers = [
        ('content-type', 'text/plain'),
        ('content-length', str(len(body)))
    ]
    start_response(status, headers)

    return [body.encode()]

if __name__ == '__main__':
    from wsgiref.simple_server import make_server

    server = make_server('0.0.0.0', 3000, application) # 创建一个容器
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()

