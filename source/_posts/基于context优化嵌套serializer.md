---
title: 基于context优化嵌套serializer
date: 2022-03-02 18:23:00
tags: Rest
categories: Rest
---

很多同学可能项目中使用过`django-rest-framework`包，它可以帮助我们进行序列化，分页，鉴权，路由注册等等功能。虽然使用起来比较方便，但是有些时候性能方面还是要差一些的，比如下面的情况：

<!--more-->

```python
class Order(models.Model):
    id = models.BigAutoField(primary_key=True)
    order_number = models.BigIntegerField(default=1001)
    customer_id = models.IntegerField()
    price = models.DecimalField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
        default=0,
        null=True,
    )
    ...

class Payment(models.Model):
    id = models.BigAutoField(primary_key=True)
    pay_method = models.CharField(max_length=32)
    order_id = models.IntegerField()
    ...
    
class Consumer(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=32)
    ...
```

如上有`Order`，`Payment`，`Consumer`三个`model`，那么如果我们需要返回`Order`的完整信息，那么就需要查询三个表中的数据，比如下面的`Serializer`

```python
class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        exclude = ("id",)
    
class ConsumerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Consumer
        exclude = ("id",)


class OrderSerializer(serializers.ModelSerializer):
    payment_info = serializers.SerializerMethodField()
    customer_info = serializers.SerializerMethodField()
    
    def get_payment_info(self, obj: Order):
        payment_obj = Payment.objects.get(order_id=obj.id)
        return PaymentSerializer(payment_obj).data
    def get_customer_info(self, obj: Order):
        customer_obj = Customer.objects.get(id=obj.custome_id)
        return PaymentSerializer(payment_obj).data
    class Meta:
        model = Order
        exclude = ("id", customer_id)
```

那么如果我们使用上面的序列化类去进行序列化的话就是这样

```python
[OrderSerializer(obj).data for obj in order_query_set]
```

这样的结果就是在每个循环内又进行了两次数据库的`IO`，如果有更多的关联表信息，那`IO`数量就会更多，从而查询结果更慢。

这时我们可以使用`context`参数，通过`in`方式一次查询出所有的关联信息，然后通过`namedtuple`组装成类似`model`的结构，再去序列化

```python
context = {
	"payment_context": {order_id: namedtuple("Payment", payment_data.keys())(**payment_data)},
	"customer_context": {customer_id: namedtuple("Customer", customer_data.keys())(**customer_data)},
}
[OrderSerializer(obj, context=context).data for obj in order_query_set]
```

这样就可以把`context`传入到`OrderSerializer`中，那么我们接下来只需要在稍稍改动一下`OrderSerializer`就可以了

```python
class OrderSerializer(serializers.ModelSerializer):
    payment_info = serializers.SerializerMethodField()
    customer_info = serializers.SerializerMethodField()
    
    def get_payment_info(self, obj: Order):
        payment_obj = sel.context["payment_context"].get(obj.id) or Payment.objects.get(order_id=obj.id)
        return PaymentSerializer(payment_obj).data
    def get_customer_info(self, obj: Order):
        customer_obj = sel.context["customer_context"].get(obj.custome_id) or Customer.objects.get(id=obj.custome_id)
        return PaymentSerializer(payment_obj).data
    class Meta:
        model = Order
        exclude = ("id",)

```

好啦，只需要上面那样，优先从我们`context`中查询，如果查询不到又做了一步兼容，再去查询`db`，这样使用部分内存节省了大量的`IO`时间。