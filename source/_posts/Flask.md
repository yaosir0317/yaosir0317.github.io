---
title: Flask
date: 2019-01-10 16:41:36
tags: Flask
categories: Flask
---

# Flask

一个小而精的web框架

你只需要三行代码就可以搭建一个web项目

```python
from flask import Flask
app = Flask(__name__)
app.run("0.0.0.0",5000,debug=True)
```

<!--more-->

## flask-Response

```python
from flask import render_template
render		 return render_template("index.html")
from flask import redrict
redrict      return redrict("/路由地址")

return "" 
from flask import jsonify
jsonify		return jsonify({"name":"v1"}) # 响应头中加入Content-Type：application/json 
from flask import send_file
send_file	return send_file("文件路径") # 打开文件并返回文件内容
# 会自动识别文件类型 Content-Type：文件类型
# 二进制文件时背景特殊颜色
```



## flask-Request

request为公共变量
from flask import request

```python
request.method # 获取当前请求的方式
request.form # 获取FormData中的数据 to_dict()字典操作
request.args # 获取url中的数据 to_dict()字典操作
request.json # 请求头当中Content-Type：application/json将数据序列化到json中
request.data # Content-Type无法被识别的时候,b""原始请求数据
request.files # 获取文件数据，save("文件名")
request.values #查看 form 和 url 中的数据 不要使用 to_dict 会覆盖form中的数据
```



## flask-路由

> 1.`endpoint` 反向生成url地址标志 默认视图函数名 url_for
> 2.`methods` 视图函数允许的请求方式
> 3.`"/index/<page>" `动态路由路由参数
> ​	def index(page)	接收动态路由参数
> 4.`defaults={"nid":"123456"}` 默认参数
> 5.`strict_slashes=True` 是否严格遵循路由地址
> 6.`redirect_to="/login"` 永久重定向 301

## flask-实例化

> 1.template_folder="temp" 默认模板路径 templates
> 2.static_folder="static", 默认静态文件路径 static
> 3.static_url_path="/static" 访问静态文件路由地址 默认是"/"+static_folder
> 4.static_host=None 指定静态文件服务器地址
> 5.host_matching = False,  # 如果不是特别需要的话,慎用,否则所有的route 都需要host=""的参数
> 6.subdomain_matching = False,  # 理论上来说是用来限制SERVER_NAME子域名的
> 7.instance_path = None,  # 指向另一个Flask实例的路径
> 8.instance_relative_config = False  # 是否加载另一个实例的配置
> 9.root_path = None  # 主模块所在的目录的绝对路径,默认项目目录

## flask-对象

> 'DEBUG': False,  # 是否开启Debug模式
> 'TESTING': False,  # 是否开启测试模式
> 'SECRET_KEY': None # 在启用Flask内置Session的时候/开启flash,一定要有它
> 'PERMANENT_SESSION_LIFETIME': 31,  # days , Session的生命周期(天)默认31天
> 'SESSION_COOKIE_NAME': 'session',  # 在cookies中存放session加密字符串的名字

你可以使用指定对象的方式

```python
class FlaskDebug(object):
    DEBUG=True
    SECRET_KEY="DEBUGmoshidesecret_key"
    PERMANENT_SESSION_LIFETIME = 7
    SESSION_COOKIE_NAME = "debug_session"

app.config.from_object(FlaskDebug)
```

## flask-蓝图

Blueprint 当成一个不能被启动的 app Flask示例

url_prefix="/blue" url前缀

```python
from flask import Blueprint,render_template
blueapp = Blueprint("blueapp",__name__,template_folder="apptemp",url_prefix="/blue")
@blueapp.route("/blueapp")
def blueappfunc():
    return render_template("blueapp.html")
	
app.register_blueprint(views.blueapp) # 注册到app上
```

## flask-特殊装饰器

```python
@app.before_request # 请求进入视图函数之前
@app.after_request # 响应返回客户端之前
 
@app.errorhandler(404) # 重定义错误页面返回信息
def error404(error_info):
	return error_info # error_info可以替换成自己定义的错误提示
```



## Jinja2

> {{ }} 引用变量 执行函数
> {% %} 逻辑代码中使用

## Flask-Session

属于公共变量
from flask import session

```python
app.secret_key = "123456789"
```

是存在cookie中的键值对（序列化后的数据），为了节省flask的开销，相对安全