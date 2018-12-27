---
title: Django-ContentType
date: 2018-12-12 16:50:36
tags: 
	- ContentType 
	- Django
categories: Django
---

# 什么是Django ContentTypes

Django ContentTypes是由Django框架提供的一个核心功能，它对当前项目中所有基于Django驱动的model提供了更高层次的抽象接口。 

<!--more-->

我们一直强调的一句话是，编程是数据结构和算法的结合。所谓数据就是用户需要访问和操作的资源，比如购物类App里面的商品，图书、衣服、鞋帽等等。算法就是我们通过一系列的获取数据、过滤数据、汇总并编排数据并最终展现给用户的一个过程。

算法的实现过程非常重要，但是算法的实现复杂度直接与数据的存储结构相关，数据的存储结构如果设计的非常好，那么向用户展示数据的算法可能会非常简单，反之，则将异常复杂。

一切优化，最终都是关于需求的优化。ContentTypes就是用来优化表结构

# 使用

当使用django-admin初始化一个django项目的时候，可以看到在默认的INSTALL_APPS已经包含了django.contrib.contenttypes:

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]
```

而且注意django.contrib.contenttypes是在django.contrib.auth之后，这是因为auth中的permission系统是根据contenttypes来实现的。

# ContentType的通用类型

此处将引用在stackoverflow中回答的例子讲述对通用类型的理解。 
假设以下的应用场景：

```python
from django.db import models
from django.contrib.auth.models import User

class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=75)
    body = models.TextField(blank=True)

class Picture(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField()
    caption = models.TextField(blank=True)
    
class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField(blank=True)
    post = models.ForeignKey(Post, null=True)
    picture = models.ForeignKey(Picture, null=True)
```

里面包含文章Post，Picture和评论Comment模型。Comment可以是对Post的评论，也可以是对Picture的评论。如果你还想对其它对象（比如回答，用户) 进行评论, 这样你将需要在comment对象里添加非常多的ForeignKey。你的直觉会告诉你，这样做很傻，会造成代码重复和字段浪费。实际生产中也绝不允许我们的这么做,一个更好的方式是，只有当你需要对某个对象或模型进行评论时，才创建comment与那个模型的关系。这时你就需要使用django contenttypes了。

ContentType提供了一种GenericForeignKey的类型，通过这种类型可以实现在Comment对其余所有model的外键关系。 修改后的Comment模型如下：

```python
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation

class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField(blank=True)
    # ContentType
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
```

在这里，通过使用一个content_type属性代替了实际的model（如Post，Picture），而object_id则代表了实际model中的一个实例的主键，其中，content_type和object_id的字段命名都是作为字符串参数传进content_object的。

下面先创建数据

```python
>>> from app01.models import User
>>> from app01.models import Post
>>> from app01.models import Picture
>>> from app01.models import Comment
>>> user = User.objects.create_user(username="yao", password="123")
>>> post = Post.objects.create(author=user,title="1",body="")
>>> picture = Picture.objects.create(author=user,image="image1",caption="111")
>>> post2 = Post.objects.create(author=user,title="2",body="")
>>> picture2 = Picture.objects.create(author=user,image="image2",caption="222")
```

comment添加数据

```python
>>> post1 = Post.objects.get(title="1")
>>> picture1 = Picture.objects.get(caption="111")
>>> post2 = Post.objects.get(title="2")
>>> picture2 = Picture.objects.get(caption="222")
>>> c1 = Comment.objects.create(author=user,body="",content_object=post1)
>>> c2 = Comment.objects.create(author=user,body="",content_object=post2)
>>> c3 = Comment.objects.create(author=user,body="",content_object=picture1)
>>> c4 = Comment.objects.create(author=user,body="",content_object=picture2)
```

查询

```python
>>> c1.content_type
>>> <ContentType: post>
>>> c1.object_id
>>> 1
>>> c1.content_object
>>> <Post: Post object (1)>
```

