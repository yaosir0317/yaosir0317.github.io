---
title: Django你需要了解的事儿
date: 2018-12-10 15:33:32
tags: Django
categories: Django
---

## MTV模型与MVC模型

**MVC**

> Model（模型）：是应用程序中用于处理应用程序数据逻辑的部分。通常模型对象负责在数据库中存取数据。
>
> View（视图）：是应用程序中处理数据显示的部分。通常视图是依据模型数据创建的。
>
> Controller（控制器）：是应用程序中处理用户交互的部分。通常控制器负责从视图读取数据，控制用户输入，并向模型发送数据。

<!-- more -->

**MTV**

> M 带包模型(Model) 负责业务对象和数据库的关系映射(ORM) T 代表模板(Template) 负责如何把页面展示给用户(html) V 代表视图 （View） 负责业务逻辑 并在适当时候调用Model和Template

## queryset数据类型的特性

> 可以切片使用(不支持负的索引)
>
> 可迭代
>
> 惰性查询
>
> 缓存机制

## queryset数据类型的方法

> create()
>
> p = Person(name="WZ", age=23)
>
> p.save()
>
> .all()
>
> get()
>
> exclude()
>
> valeslist()
>
> orderby()

## 级联删除不等于同时删除

> 级联删除表示主表记录删除，对应表记录 同样删除
>
> 一对多 ， 一对一 时候用，

```
user = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE)
```

## cookie与session的运行机制

> 1.cookie数据存放在客户的浏览器上，session数据放在服务器上
>
> 2.cookie不是很安全，别人可以分析存放在本地的COOKIE并进行COOKIE欺骗 考虑到安全应当使用session。
>
> 3、session会在一定时间内保存在服务器上。当访问增多，会比较占用你服务器的性能 考虑到减轻服务器性能方面，应当使用COOKIE
>
> 4、单个cookie保存的数据不能超过4K，很多浏览器都限制一个站点最多保存20个cookie。 cookie 和session 的联系
>
> session是通过cookie来工作的，可以考虑将登陆信息等重要信息存放为session，其他信息如果需要保留，可以放在cookie中

## 反向解析

作用:防止硬编码,便于维护

```
path("login/",views,login,name = "login")

模板 ：{% url "login"  参数 %}
视图 ：redirct(reverse(login),args=参数)
```

## Q查询的两种使用方式

```
book.object.filter(Q(name = ...)|Q(user = ...))
q=Q()
q.chidnen.append(...)
book.objects.filter(q)
```

## 请求头contentType的作用

> content-type请求头是干吗的呢，http请求头有四种类型，分别是通用头部，请求头部，响应头部以及内容头部，首先，我们要弄清楚，
>
> content-type是属于内容头部，既然是内容头部，那这个请求头是用来向接收端解释传递的该内容主体的，content-type的取值是告诉服务端，你传递过去的内容是啥，你应该准备好如何接收
>
>  

## rbac表结构

> User 用户，
>
> Role 角色 ，
>
> Permission 权限，
>
> 表关系:
>
> 角色和 权限 一对多 和用户一对多

## crm的查询语法

> min()
>
> max()
>
> conut()
>
> avg()

## 向服务器发送一个json数据

```
$.ajax({
        url:'${pageContext.request.contextPath }/rest/jsonBody',
        type:'POST',
        dataType:'json',
        contentType:'application/json;charset=UTF-8',
        data:JSON.stringify(data),
        success:function(data, status){
            console.log(data);
        }
    });

```

## 中介模型

> 多对多字段 创建的时候 Djiango会自动帮我们创建第三张表满足不了我们的需求，可用中介模型使用自定义的第三张表 添加字段。
>
>  

## ForeignKey中的db_constraint参数

> db_constraint 唯一约束
>
> db_constraint = True 方便查询 约束字段
>
> db_constraint = fales 不约束字段 同时也可以查询
>
>  

## 用户认证组件

> 用户登陆的时候
>
> 注册对象auth.login(request,当前登陆人对象)
>
> if 获取 request.user 是否为空
>
> 登陆成功
>
> 优点：可用中间件 校验 ，可全局用
>
>  

## Django常用模块的引入

> from Django.conf import settings
> 1. urls相关操作
>      from django.urls import path, re_path(使用正则时使用), include
>        from django.urls import reverse  // 注意reverse 和另一个reversed区别。前者要明确导入通过名称解析出地址，后者是built-in内置不用导入；两者功能也不一。
>
> 2. HttpResponse生成
>      from django.shortcuts import render, Httpresponse, redirect
>        from django.http import JsonResponse // 响应一个content-type：text/json 返回一个json响应报文,相应的浏览器端也不用在对json反解
>
> 3. 组件auth
>      from django.contrib import auth  //contrib 意味：构件
>        from django.contrib.auth.models import User 
>        from django.contrib.auth.decorators import login_required
>
> 4. 组件forms
>      from django import forms
>        from django.forms import widgets
>        from django.core.exceptions import ValidationError  // django的异常定义都在django.core.exceptions模块中，该异常用于自定义钩子。
>        from django.forms import ModelForm  // 如果一个form的字段数据是被用映射到一个django models.那么一个ModelForm可以帮助你节约很多开发时间。因为它将构建一个form实例，连同构建适当的field和field attributes，利用这些构建信息，都来自一个Model class. 
>        from django.core.files.uploadedfile import SimpleUploadedFile
>
>      from django.forms.models import modelformset_factory
>
> 5. 邮件组件
>      from django.core.mail import send_mail
>
> 6. model组件
>      from django.db import models
>        from django.db.models import F, Q
>        from django.contrib.auth.models import AbstractUser
>        from django.contrib.auth.models import User
>        from django.db import transaction  # 利用model做数据库的事务操作
>
> 7. 分页器相关
>      from django.core import paginator
>
> 8. django admin site相关
>      from django.contrib import admin
>        from django.contrib.admin import ModelAdmin
>
> 9. view 相关
>      from django.view import View  # 用于media访问内置视图
>
> 10. 中间件
>      from django.utils.deprecation import MiddlewareMixin
>
> 11. template模版相关
>       from django import template  # 自定义tag和filter需要用到





