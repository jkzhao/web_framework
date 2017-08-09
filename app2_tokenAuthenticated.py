# -*- coding: utf-8 -*-

from web import Router, Application
from web.utils import jsonfy
from webob import Response
from functools import wraps
from base64 import b64decode
from webob.exc import HTTPUnauthorized
import jwt
import json
import datetime

'''
jwt是一种编码方式，用一定的算法把一些东西编码到token中，编码之后是字符串。
编码之后的字符串并非是加密的，是完全可以解密出来的。所以我们在匹配完用户名和密码后，encode的时候只把用户名encode进去了。
In [6]: import jwt

In [7]: key = 'hslahjgl'

In [8]: jwt.encode({'user': 'jkzhao'}, key, 'HS512')
Out[8]: b'eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoiamt6aGFvIn0.kyKYExUYJsm0ZavSHSl8ocVzmC9JodCHPnpp7wNm7HxrsWjG1gjnJbMtXqldO1ggGHB-pSRQMKZq1Qqa4LWbKA'

In [9]: encoded = jwt.encode({'user': 'jkzhao'}, key, 'HS512')

In [10]: jwt.decode(encoded, key, ['HS512'])
Out[10]: {'user': 'jkzhao'}

In [11]: import datetime

#指定失效时间为当前时间
In [12]: encoded = jwt.encode({'user': 'jkzhao', 'exp': datetime.datetime.utcnow
    ...: ()}, key, 'HS512')

In [13]: jwt.decode(encoded, key, ['HS512']) #再次decode的时候，会报 ExpiredSignatureError: Signature has expired

In [14]: encoded = jwt.encode({'user': 'jkzhao', 'exp': datetime.datetime.utcnow
    ...: () + datetime.timedelta(seconds=60)}, key, 'HS512') #一分钟后失效

In [15]: jwt.decode(encoded, key, ['HS512'])
Out[15]: {'exp': 1502261059, 'user': 'jkzhao'}

In [16]: jwt.decode(encoded, key, ['HS512'])
Out[16]: {'exp': 1502261059, 'user': 'jkzhao'}
'''

__KEY = 'hfaksdlhg' # key是用来判断是不是服务端发出来的key，可以自行定义该值

router = Router()

def authenticated(fn): # 用json web token来验证。凡是被这个装饰器装饰的handler都是受保护的，需要认证才能访问
    @wraps(fn)
    def wrap(ctx, request):
        token = request.headers.get('X-Authorization-Token') # 自定义头
        print(token)
        if token is None:
            raise HTTPUnauthorized()
        try:
            decoded = jwt.decode(token.encode(), __KEY, ['HS512'])
            user = decoded.get('user')
            if user is None:
                raise HTTPUnauthorized()
            request.user = user
            return fn(ctx, request)
        except Exception:
            raise HTTPUnauthorized()

    return wrap

@router.route('/')
@authenticated
def main(ctx, request):
    return Response('hello world')

@router.route('/login', methods=['POST']) # 登录接口
def login(ctx, request):
    payload = json.loads(request.body.decode())
    if payload.get('username') == 'jkzhao' and payload.get('password') == 'pass': # 实际业务这里需要去数据库查询
        exp = datetime.datetime.utcnow() + datetime.timedelta(hours=8)
        token = jwt.encode({'user': 'jkzhao', 'exp': exp}, __KEY, 'HS512').decode()
        # return Response(json.dumps({'token': token}), content_type='application/json', charset='UTF-8') # 返回一个json字符串
        return jsonfy(code=200, token=token)
    # return Response(json.dumps({'code': 401, 'message': 'username or password not match'}), content_type='application/json', charset='UTF-8')
    return jsonfy(code=401, message='username or password not match')

# $ curl -XPOST http://127.0.0.1:3000/login -d '{"username": "jkzhao", "password": "pass"}'
# {"token": "eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE1MDIyOTM5NjksInVzZXIiOiJqa3poYW8ifQ.uWxmuCuj5d8Yfo8PyzyorbE0X0t_cpu4lychC4inpEY8YPifhopJZF-QhSKv7IdU9tdrwzYrfiWcoB5w2XIiKw"}
# $ curl -H 'X-Authorization-Token: eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE1MDIyOTM5NjksInVzZXIiOiJqa3poYW8ifQ.uWxmuCuj5d8Yfo8PyzyorbE0X0t_cpu4lychC4inpEY8YPifhopJZF-QhSKv7IdU9tdrwzYrfiWcoB5w2XIiKw' http://127.0.0.1:3000
# hello world

app = Application()
app.add_router(router)

if __name__ == '__main__':
    from wsgiref.simple_server import make_server

    server = make_server('0.0.0.0', 3000, app)  # 创建一个容器
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()

