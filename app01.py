# -*- coding: utf-8 -*-

# WSGI demo
# https://www.python.org/dev/peps/pep-3333/

# WSGI 通过函数调用来通信，所以一个 WSGI应用 是一个callable对象（callable对象：函数、实现了__call__方法的类）
# 所以可以写一个函数作为wsgi应用，但是这个函数的参数是有规定的。
# 参数1：既然是通信，environ将客户端一次请求的内容带过来。参数1和参数2都是容器传递给应用
# 参数2：start_response 是一个callable对象，是个回调函数，代表开始响应了。需要通知容器告知，应用开始响应了
def application(environ, start_response):
    # for k, v in environ.items():
    #     print('{} => {}'.format(k, v)) # 客户端和本地环境变量都打印出来了

    print(environ.get('QUERY_STRING')) # 浏览器输入127.0.0.1:3000/?name=jkzhao&age=26，打印出来是name=jkzhao&age=26。解析出来就可以获得客户端传递的参数了
    from urllib.parse import parse_qs
    from html import escape # 转义，原来这两个模块都是在cgi模块中的
    params = parse_qs(environ.get('QUERY_STRING')) # {'age': ['26'], 'name':['jkzhao']} value是个list，防止传入多个name
    name = params.get('name', ['anonymous'])[0]
    body = 'hello {}'.format(name)
    # 但是这种比较危险，比如 127.0.0.1:3000/?name=<script type='text/javascript'>alert('fuck you')</script>
    # 结果是 hello <script type='text/javascript'>alert('fuck you')</script>
    # 这是因为chrome浏览器为我们做了工作了，会检测到xss攻击，否则会一直弹窗。所以不能假设用户浏览器比较高级，我们在服务器要处理：
    body = 'hello {}'.format(escape(name))

    # body = 'hello world'
    status = '200 OK'
    headers = [
        ('content-type', 'text/plain'),
        ('content-length', str(len(body)))
    ]
    start_response(status, headers) # 固定写法，http的头部，下面的是body

    return [body.encode()] # wsgi解析时是迭代解析的，我们可以传递多个body过去，传个可迭代对象list过去。里面的元素必须是bytes

# 需要一个容器才能跑起来
# Python标准库里有容器的实现
if __name__ == '__main__':
    from wsgiref.simple_server import make_server

    server = make_server('0.0.0.0', 3000, application) # 创建一个容器
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()

# 也可以用容器 gunicorn 跑这个应用。通常开发的时候用wsgiref就可以了，生产上就要用第三方容器了，比如gunicorn
# pip install gunicorn
# gunicorn -b 0.0.0.0 app1:application
