# -*- coding: utf-8 -*-

# WSGI demo
'''
封装request对象和response对象，以面向对象的方式，封装是为了给开发者方便
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

class Response:
    STATUS = {
        200: 'OK',
        301: 'Moved Permanently',
        302: 'Move temporarily',
        404: 'Not Found',
        500: 'Internal Server Error',
        503: 'Service Unavailable'
    }

    def __init__(self, body=None):
        self.body = body
        self.status = '200 OK'
        self.headers = {
            'content-type': 'text/html',
            'content-length': str(len(self.body))
        }

    def set_body(self, body):
        self.body = body
        self.headers['content-length'] = str(len(self.body))

    def set_status(self, status_code, status_text=''):
        self.status = '{} {}'.format(status_code, self.STATUS.get(status_code, status_text))

    def set_header(self, name, value):
        self.headers[name] = value

    def __call__(self, start_response): # wsgi的响应是分两部分的，一部分是头，一部分是body。
        start_response(self.status, [(k, v) for k, v in self.headers.items()]) # 返回头
        return [self.body.encode()] # 返回body


def application(environ, start_response): # 封装成对象之后，应用开发者只需要写这个函数机会可以了
    request = Request(environ)
    name = request.params.get('name', ['anonymous'])[0]
    body = 'hello {}'.format(escape(name))

    # start_response(status, headers)
    # return [body.encode()]

    return Response(body)(start_response) # 返回给wsgi容器

if __name__ == '__main__':
    from wsgiref.simple_server import make_server

    server = make_server('0.0.0.0', 3000, application) # 创建一个容器
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()

