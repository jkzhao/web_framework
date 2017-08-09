# -*- coding: utf-8 -*-

from web import Router, Application
from webob import Response

router = Router()

@router.route('/')
def main(ctx, request):
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
