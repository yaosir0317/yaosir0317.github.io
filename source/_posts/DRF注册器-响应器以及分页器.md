---
title: DRF组件学习之三
date: 2018-12-11 15:47:52
tags: 
	- Rest
	- Django
categories: Rest
---

# url注册器

通过DRF的视图组件，数据接口逻辑被我们优化到最剩下一个类，接下来，我们使用DRF的url控制器来帮助我们自动生成url，使用步骤如下：

<!--more-->

## 导入模块

```python 
from rest_framework import routers
```

## 生成一个注册器实例对象

```python 
router = routers.DefaultRouter()
```

## 将需要自动生成url的接口注册

```python
router.register(r"books", views.BookView)
```

## 开始自动生成url

```python
urlpatterns = [
	re_path('^', include(router.urls)),
]
```

# 响应器

之前我们使用DRF的Response类来将数据响应给客户端，不管是POSTMAN还是浏览器，都能浏览到经过格式化后的漂亮的数据，DRF是怎么做的呢？其实就是通过响应器组件

## 导入模块

```python
from rest_framework.renderers import JsonRenderer
```

## 指定返回类

```python
class BookView(APIView):
	 render_classes = [JsonRenderer]
```

renderer_classes的查找逻辑与之前的解析器等等组件是完全一样的。这样就设置不使用restframework而是默认json数据格式

# 分页器

为了服务器性能考虑，也为了用户体验，我们不应该一次将所有的数据从数据库中查询出来，返回给客户端浏览器，如果数据量非常大，这对于服务器来讲，可以说是性能灾难，而对于用户来讲，加载速度将会非常慢。

使用方式

> 导入模块
>
> from rest_framework.pagination import PageNumberPagination	
>
> - 获取数据
>     books = Book.objects.all()
> - 创建一个分页器对象
>     paginater = PageNumberPagination()
> - 开始分页
>     paged_books = paginater.paginate_queryset(books, request)
> - 开始序列化
>     serialized_books = BookSerializer(paged_books, many=True)
> - 返回数据
>     return Response(serialized_books.data)

## 分页器组件局部实现

### 自定义一个分页类并集成PageNumberPagination

```python
class MyPagination(PageNumberPagination):
    # 每页显示数量
    page_size = 2
    # 通过路由访问页码 ?page=1
    page_query_param = 'page'
    # 通过路由访问中显示的数量 ?page=1&size=2
    page_size_query_param = 'size'
    # 最大显示数量
    max_page_size = 5
```

### 实例化一个分页类对象

```python
paginater = MyPagination()
```

### 开始分页

```python
paged_books = paginater.paginate_queryset(books, request)
```

### 开始序列化

```python
serialized_books = BookSerializer(paged_books, many=True)
```

### 返回数据

```python
return Response(serialized_books.data)
```

