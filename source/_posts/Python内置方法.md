---
title: Python内置方法
date: 2018-12-14 20:32:11
tags: Python
categories: 内置函数
---

# sorted

用于可迭代对象的排序

```python
sorted(iterable,key,reverse)
```

<!--more-->

第一个参数必传为需要排序的对象

第二个参数为`key=name`,name为排序所依据的字段,此参数可选

第三个参数默认为False,当设置`reverse=False`时,进行反序排序

# or - and - not 运算

运算优先级not  >  and  >  or

## not

> not True = False
>
> not False = True
>
> 0 = False
>
> other = True

## and

> True and False = False
>
> False and True = False
>
> 0 and 2 = 0
>
> 2 and 0 = 0
>
> 0 and False = 0
>
> False and 0 = False
>
> 1 and 2 = 2
>
> 2 and 1 = 1

##  or

or与and的运算规律完全相反,建议记住and运算规律,计算or时以and运算规律,结果与规律相反

> True or False = True
>
> False or True = True
>
> 0 or 2 = 2
>
> 2 or 0 = 2
>
> 0 or False = False
>
> False or 0 = 0
>
> 1 or 2 = 1
>
> 2 or 1 = 2

# itertools

模块提供的全部是处理迭代功能的函数，它们的返回值不是list，而是迭代对象，只有用`for`循环迭代的时候才真正计算。

# iter

以读取文件为例

```python
with open("models.py", "rb") as e:
    for i in iter(lambda: e.read(1024), b""):
        print(i)
```

此例中iter()的第一个参数读取文件,第二个参数为,结束字符,当读取b""时,读取结束