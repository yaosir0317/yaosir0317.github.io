---
title: DRF序列化组件
date: 2018-12-14 14:07:56
tags: 
	- Rest 
	- Django
categories: Rest #文章文类
---

# rest	

rest下的url

> url唯一代表资源，http请求方式来区分用户行为

url的设计规范

> GET：   127.0.0.1:9001/books/		   # 获取所有数据
> GET:    127.0.0.1:9001/books/{id}     	   # 获取单条数据
> POST：  127.0.0.1:9001/books/		   # 增加数据
> DELETE: 127.0.0.1:9001/books/{id}     	   # 删除数据
> PUT:    127.0.0.1:9001/books/{id}    	   # 修改数据

<!-- more -->

数据响应规范

> GET：   127.0.0.1:9001/books/		   # 返回[{}, {}, {}]
> GET:    127.0.0.1:9001/books/{id}      	   # {} 单条数据
> POST：  127.0.0.1:9001/books/		   # {} 添加成功的数据
> DELETE: 127.0.0.1:9001/books/{id}      	   # "" 返回空
> PUT:    127.0.0.1:9001/books/{id}	   	   # {} 更新后完整的数据

错误处理

> { "error": "message" }

# 解析器组件

> - 解析器组件是用来解析用户请求的数据的（application/json), content-type
> - 必须继承APIView
> - request.data触发解析

APIView的使用

> pip install djangorestframework

```
from rest_framework.views import APIView

class LoginView(APIView):
	def get(self, request):
	pass
```

# 序列化组件

## Django自带的serializer

```python
from django.serializers import serialize  # 引入

origin_data = Book.objects.all()
serialized_data = serialize("json", origin_data)
```

## DRF的序列化组件

### 接口设计

```python
from rest_framework import serializers	#引入
```

创建一个序列化类

```python
class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
		# model字段
        fields = ('title',
                  'price',
                  'publish',
                  'authors',
                  'author_list',
                  'publish_name',
                  'publish_city'
                  )
        # 只需写入不需要展示的字段
        extra_kwargs = {
            'publish': {'write_only': True},
            'authors': {'write_only': True}
        }
	# source为自定义需要展示的信息
    publish_name = serializers.CharField(max_length=32, read_only=True, source='publish.name')
    publish_city = serializers.CharField(max_length=32, read_only=True, source='publish.city')
	# 多对多字段需要自己手动获取数据，SerializerMethodField()
    author_list = serializers.SerializerMethodField()

    def get_author_list(self, book_obj):
        # 拿到queryset开始循环 [{}, {}, {}, {}]
        authors = list()

        for author in book_obj.authors.all():
            authors.append(author.name)

        return authors
```

**开始序列化**

get接口(查询多条数据)    &   post接口

```python
class BookView(APIView):
    def get(self, request):
        # 获取queryset
        origin_data = Book.objects.all()
        # 开始序列化
        serialized_data = BookSerializer(origin_data, many=True)
        return Response(serialized_data.data)
    def post(self, request):
        verified_data = BookSerializer(data=request.data)
        if verified_data.is_valid():
            book = verified_data.save()
            authors = Author.objects.filter(nid__in=request.data['authors'])
            book.authors.add(*authors)
            return Response(verified_data.data)
        else:
            return Response(verified_data.errors)
```

get(查询单条数据)	&	put接口	&	delete接口

```python
class BookFilterView(APIView):
    def get(self, request, nid):
        book_obj = Book.objects.get(pk=nid)
        serialized_data = BookSerializer(book_obj, many=False)
        return Response(serialized_data.data)

    def put(self, request, nid):
        book_obj = Book.objects.get(pk=nid)
        verified_data = BookSerializer(data=request.data, instance=book_obj)
        if verified_data.is_valid():
            verified_data.save()
            return Response(verified_data.data)
        else:
            return Response(verified_data.errors)

    def delete(self, request, nid):
        book_obj = Book.objects.get(pk=nid).delete()
        return Response()
```

缺点:

> serializers.Serializer无法插入数据，只能自己实现create字段太多，不能自动序列化

## 接口设计优化

### 使用视图组件的mixin进行接口逻辑优化

导入mixin

```python
from rest_framework.mixinx import (
					ListModelMix,
					CreateModelMixin,
					DestroyModelMixin,
					UpdateModelMixin,
					RetrieveModelMixin
				)
from rest_framework.generics import GenericAPIView

```

定义序列化类

```python 
Class BookSerializer(serializers.ModelSerializer):
			      class Meta:
				      Book
					  fields = ()
					  ...如上
```

因为使用模块化编程,建议将定义的序列化类放在单独的模块中,再在view.py中导入

```python
from .app_serializers import BookSerializer
```

定义视图类​	  

```python
class BookView(ListModelMixin, CreateModelMixin, GenericAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer	    
    def get():
        return self.list()

    def post():
        return self.create()
class BookFilterView(RetrieveModelMixin, DestroyModelMixin, UpdateModelMixin, GenericAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    def get():
        return self.retrieve()

    def delete():
        return self.destroy()

    def put():
        return self.update()
```

注意:

> 查询单挑数据的url需要给查询的id进行正则分组
>
> re_path(r'books/(?P<pk>\d+)/$, views.BookFilterView.as_view())

### 使用视图组件的view进行接口逻辑优化

导入模块

```python
from rest_framework import generics
```

视图类​				

```python
class BookView(generics.ListCreateAPIView)
    queryset = Book.objects.all()
    serializer_class = BookSerializer	
class BookFilterView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
```

### 使用视图组件的viewset进行接口逻辑优化

导入模块

```python
from rest_framework.viewsets import ModelViewSet
```

设计url

```python
re_path(r'books/$, views.BookView.as_view({
    'get': 'list',
    'post': 'create'
	})),
re_path(r'books/(?P<pk>\d+)/$', views.BookView.as_view({
    'get': 'retrieve',
    'delete': 'destroy',
    'put': 'update'
	}))
```

设计视图类

```python 
class BookView(ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
```

