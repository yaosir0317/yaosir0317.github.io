---
title: DRF权限认证频率组件
date: 2018-11-15 19:13:32
tags: Rest
categories: Django #文章文类
---

在编程的世界中，我们认为，用户输入的所有数据都是不可靠的，不合法的，直接使用用户输入的数据是不安全的，因此就需要认证组件、权限组件以及频率组件。

# DRF用户认证

<!--more-->

## 局部认证

### 定义一个认证类

```python
class UserAuth(BaseAuthentication):
	
    def authenticate_header(self, request):
        pass
    # 所有的认证逻辑都在authenticate
    def authenticate(self, request):
        user_token = request.query_params.get("token")
        try:
            # 通过
		   # 1. 拿到用户传递的token
		   # 2. 拿到数据里面的token与用户传递的token进行比对
            token = UserToken.objects.get(token=user_token)
            # 后面权限会用到
            return token.user, token.token
        except Exception:
            # 不通过
            raise APIException("没有认证")
```

如果不希望每次都写那个无用的authenticate_header方法，我们可以这样：

导入模块,然后继承BaseAuthentication类

```
from rest_framework.authentication import BaseAuthentication
```

实现方式非常简单，到token表里面查看token是否存在，然后根据这个信息，返回对应信息即可，然后，在需要认证通过才能访问的数据接口里面注册认证类即可：

### 在需要认证的数据接口里面指定认证类

```python
class EgView(ModelViewSet):
    # 指定认证类
    authentication_classes = [UserAuth]
    # 获取数据
    queryset = Eg.objects.all()
    serializer_class = BookSerializer
```

可以指定多个认证类，需要注意的是，如果需要返回数据，请在最后一个认证类中返回

## 全局认证

如果希望所有的数据接口都需要认证怎么办？就是这句代码：

```python
authentication_classes=api_settings.DEFAULT_AUTHENTICATION_CLASSES
```

如果认证类自己没有authentication_classes，就会到settings中去找，通过这个机制，我们可以将认证类写入到settings文件中即可实现全局认证：

```python
REST_FRAMEWORK = {
    "DEFAULT_PARSER_CLASSES": (JsonParser, FormParser),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'authenticator.utils.authentication.UserAuth',  # 认证类1
        'authenticator.utils.authentication.UserAuth2',  # 认证类2
    ),
}
```

# DRF权限认证

### 定义一个权限类

```python
class UserPerm():
    message = "您没有查看该数据的权限！"

    def has_permission(self, request, view):
        # 用户权限
        if request.user.user_type == 3:
            # 有当前访问的地址权限
            return True
        # 无权限
        return False
```

### 指定权限验证类

```python
class EgView(ModelViewSet):
    # 指定权限类
    permission_classes = [UserPerm]
    queryset = Eg.objects.all()
    serializer_class = BookSerializer
```

# DRF频率组件

## 使用DRF的简单频率控制来控制用户访问频率(局部)

### 定义一个频率类

导入模块

```python 
from rest_framework.throttling import SimpleRateThrottle
```

定义并继承SimpleRateThrottle

```python
class RateThrottle(SimpleRateThrottle):
    # 指定访问频率
    rate = '5/m'
	# 指定区分用户方式
    def get_cache_key(self, request, view):
        return self.get_ident(request)
```

### 指定频率类

```python
class EgView(ModelViewSet):
    # 指定频率类
    throttle_classes = [RateThrottle]
    queryset = Eg.objects.all()
    serializer_class = BookSerializer
    # 自定异常
    def throttled(self, request, wait):
        raise MyException(wait=wait)
```

```python
class MyException(exceptions.Throttled):
    # 自定异常内容
    default_detail = '连接次数过多'
    extra_detail_plural = extra_detail_singular = '请在 {wait} 秒后访问'

    def __init__(self, wait=None, detail=None, code=None):
        super().__init__(wait=wait, detail=detail, code=code)
```

## 使用DRF的简单频率控制来控制用户访问频率(全局)

### 创建全局频率类并继承SimpleRateThrottle

```python
class RateThrottle(SimpleRateThrottle):
    # 指定访问频率
    scope = 'visit_rate'

    # 指定通过什么方式来区分用户
    def get_cache_key(self, request, view):
    	return self.get_ident(request)
```

### 在settings里面指定频率类和访问频率

```python
REST_FRAMEWORK = {
    "DEFAULT_THROTTLE_CLASSES": ('serializer.utils.app_throttles.RateThrottle',),
    "DEFAULT_THROTTLE_RATES": {
    "visit_rate": "5/m"
    }
}
```







