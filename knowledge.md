实现一个简单的web框架，不实现模板渲染，实现一个restful的web框架。restful是不处理cookie和session的

一个简单的Web框架应该实现哪些功能：
- request解析
- response封装
- 路由(Tornado没有子路由)

其他的东西，比如认证，都是写一个装饰器就能搞定了。框架有是好的，没有我们就自己写个装饰器。

插件，比如数据库，缓存等。web框架的中间件，处理之前做些事，处理之后做些事。比如把权限控制放到这个中间件里面做，当然我们完全可以在应用里面直接写装饰器来权限控制。
restful的web框架认证可以采用http basic方式验证，也可以使用json web token的方式认证，非restful的web框架一般都用cookie和session认证。

json web token其实是一种编码方式，把一些东西编码到token里面，可以看看它的python库--pyjwt。

拦截器、中间件、过滤器

# CGI
CGI是一个协议。
当请求某个地址的时候，http服务器会启动一个外部程序，并且把web程序的输出返回给用户。
    
CGI规范了http和外部程序的通讯方式，
- 输入：通过环境变量
- 输出：通过标准输出

CGI缺陷：
- 并发模式是多进程
- 进程由http服务器管理

## CGI ——> FastCGI
进程管理由fastcgi实现。
http服务器把http协议转化成fastcgi协议，通过socket发送给fastcgi daemon，比如php的fmp就是fastcgi
并发模型变得多种多样

## CGI ——> WSGI (web server gateway interfaces)
WSGI是一个协议: https://www.python.org/dev/peps/pep-3333/
    
WSGI分成两部分：
- 容器(或称为网关、服务器)：实现了协议转换，http——>wsgi
- 应用：处理业务逻辑

容器和应用怎么通讯？
- fastcgi是通过socket通信，wsgi的容器和应用通过函数调用来通讯。什么情况下可以通过函数调用来通讯呢？必须在同一个进程内。也就是说wsgi容器和应用是跑在同一个进程内的。
- 比较流行的wsgi容器：gunicorn uWSGI






