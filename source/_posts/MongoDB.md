---
title: MongoDB
date: 2019-01-16 16:53:27
tags: 
	- MongoDB
	- Linux
categories: MongoDB
---

# MongoDB

MongoDB 是由C++语言编写的，是一个基于分布式文件存储的开源数据库系统。

在高负载的情况下，添加更多的节点，可以保证服务器性能。

MongoDB 旨在为WEB应用提供可扩展的高性能数据存储解决方案。

MongoDB 将数据存储为一个文档，数据结构由键值(key=>value)对组成。MongoDB 文档类似于 JSON 对象。字段值可以包含其他文档，数组及文档数组。

<!--more-->

# 安装

- 下载

    `curl -O https://fastdl.mongodb.org/linux/mongodb-linux-x86_64-3.0.6.tgz `

- 解压

    `tar -zxvf mongodb-linux-x86_64-3.0.6.tgz `

- 移动到安装目录

    `mv  mongodb-linux-x86_64-3.0.6/ /usr/local/mongodb`

- 添加环境变量

- 创建数据库目录

    `mkdir -p /data/db`

    注意：/data/db 是 MongoDB 默认的启动的数据库路径(--dbpath)。

# 使用

## 开始

- ### 创建一个数据库

    `use yao`

    MongoDB中如果你使用了不存在的对象,那么就等于你在创建这个对象

- ### 创建一张表(Collection)

    `db`

    `db.db_yao`

## 增加

- ### insert

    `db.db_yao.insert({"name":"yao","age":20})`

    这个方法目前官方已经不推荐

- ### insertOne

    `db.db_yao.insertOne({"name":"yao","age":20})`

    插入一条数据

- ### insertMany

    `db.db_yao.insertMany([`

    ​	`{"name":"yao_1","age":20},`

    ​	`{"name":"yao_2","age":20},`

    `])`

    插入多条数据

## 查找

- ### find

    无条件查找:将该表(Collection)中所有的数据一次性返回

    `db.db_yao.find({})`

    查询结果:

    > /* 1 createdAt:2019/1/16 下午7:16:19*/
    > {
    > ​	"_id" : ObjectId("5c3f128355f17e734880f90e"),
    > ​	"name" : "yao_1",
    > ​	"age" : 20
    > },
    >
    > /* 2 createdAt:2019/1/16 下午7:18:13*/
    > {
    > ​	"_id" : ObjectId("5c3f12f509371218e4d0c331"),
    > ​	"name" : "yao_2",
    > ​	"age" : 20
    > }

"_id" 是一个ObjectId 类型,这是MongoDB自动给我们添加到系统唯一标识

- ### findOne

    `db.db_yao.findOne({})`

    无条件查找一条数据,默认当前Collection中的第一条数据

    `db.db_yao.findOne({"name" : "yao_1"})`

    条件查找一条name等于yao_1的数据,如有多条数据则返回更靠前的数据

## 修改

- ### update

    `update({"name":"yao_1"},{$set:{"age":21}})`

    根据条件修改该条数据的内容,这里要注意的是({"条件"},{"关键字":{"修改内容"}}),其中如果条件为空,那么将会修改Collection中所有的数据

    这个方法目前官方已经不推荐

- ### updateOne 

    `updateOne({"age":19},{$set:{"name":"yao"}})`

    根据条件修改一条数据的内容,如出现多条,只修改最高前的数据

- ### updateMany

    `updateMany({"age":19},{$set:{"name":"pig"}})`

    根据条件修改所有数据的内容,多条修改

$set:{"name":"yao"}中: $set 是update时的关键字,表示我要设置name属性的值为"yao"

那么我们之前说过MongoDB的灵活性,没有就代表我要创建,所以说如果该条Documents没有name属性,他就会自动创建一个name属性并且赋值为"yao"

## 删除

- ### remove

    `remove({})`

    无条件删除数据,这里要注意了,这是删除所有数据,清空Collection

    `remove({"name":"yao"}) `

    条件删除name等于"yao"的所有Document

# MongoDB的数据类型

- Object  ID ：Documents 自生成的 _id

- String： 字符串，必须是utf-8

- Boolean：布尔值，true 或者false (Python中 True False 首字母大写)

- Integer：整数 (Int32 Int64 一般用Int32)

- Double：浮点数 (没有float类型,所有小数都是Double)

- Arrays：数组或者列表，多个值存储到一个键 (Python中的List)

- Object：如果你学过Python的话,那么这个概念特别好理解,就是Python中的字典,这个数据类型就是字典

- Null：空数据类型 , 一个特殊的概念,None Null

- Timestamp：时间戳

- Date：存储当前日期或时间unix时间格式 (我们一般不用这个Date类型,时间戳可以秒杀一切时间类型)

## Object  ID

> "_id" : ObjectId("5b151f8536409809ab2e6b26")
>
> #"5b151f85" 代指的是时间戳,这条数据的产生时间
> #"364098" 代指某台机器的机器码,存储这条数据时的机器编号
> #"09ab" 代指进程ID,多进程存储数据的时候,非常有用的
> #"2e6b26" 代指计数器,这里要注意的是,计数器的数字可能会出现重复,不是唯一的
> #以上四种标识符拼凑成世界上唯一的ObjectID
> #只要是支持MongoDB的语言,都会有一个或多个方法,对ObjectID进行转换
> #可以得到以上四种信息
>
> #注意:这个类型是不可以被JSON序列化的

这是MongoDB生成的类似关系型DB表主键的唯一key，具体由24个字节组成：

- 0-8字节是时间戳,
- 9-14字节的机器标识符，表示MongoDB实例所在机器的不同；
- 15-18字节的进程id，表示相同机器的不同MongoDB进程。
- 19-24字节是计数器

# MongoDB的关键字

上中提到过 $set 这个系统关键字,用来修改值的,但是MongoDB中类似这样的关键字有很多, $lt $gt $lte $gte 等等

- ## 等于 

    `db.db_yao.find({"name" : "yao_1"})`

- ## 大于 

    大于:  `db.db_yao.find({"age" : {$gt:20}})`  

    大于等于:  `db.db_yao.find({"age" : {$gte:20}})`  

- ## 小于

    小于:  `db.db_yao.find({"age" : {$lt:20}})` 

    小于等于:  `db.db_yao.find({"age" : {$lte:20}})` 

# update修改器

- ## $inc

    变量 += 1 , 将查询到的结果 加上某一个值 然后保存

    db.db_yao.update({"age" : 20},{$inc:{"age":1}})

    将年龄为20的年纪全部加`1`

- ## $unset

    用来删除Key(field)

    `db.db_yao.update({"age" : 18},{$unset:{"name" : 1}})`

    就是删除 "name" 这个`field`相当于关系型数据库中删除了`字段`

- ## $push

    是用来对Array (list)数据类型进行 增加 新元素的,相当于Python中 list.append() 方法

    要先对原有数据增加一个Array类型的field:

    `db.db_yao.update({},{$set:{"list":[1,2]}})`

    > {
    > ​	"_id" : ObjectId("5c3f128355f17e734880f90e"),
    > ​	"name" : "yao",
    > ​	"age" : 19,
    > ​	"list" : [
    > ​		1,
    > ​		2
    > ​	]
    > }

    接下来将 "age" 为 19的Document 中"list" 添加一个 6

    `db.db_yao.update({"age":19},{$push: {"list":6}}) `

    > {
    > ​	"_id" : ObjectId("5c3f128355f17e734880f90e"),
    > ​	"name" : "yao",
    > ​	"age" : 19,
    > ​	"list" : [
    > ​		1,
    > ​		2,
    > ​		6
    > ​	]
    > }

- ## $pull 

    有了$push 对Array类型进行增加,就一定有办法对其内部进行删减,$pull 就是指定删除Array中的某一个元素

    `db.db_yao.update({"age":19},{$pull: {"list":6}})`

    只要满足条件,就会将Array中所有满足条件的数据全部清除掉

- ## $pop

    指定删除Array中的第一个 或 最后一个 元素

    删除最后一个元素:  `db.db_yao.update({"age":19},{$pop: {"list":1}})`

    删除第一个元素:  `db.db_yao.update({"age":19},{$pop: {"list":-1}})`


# MongoDB的  **"$"**

在MongoDB中有一个非常神奇的符号 "$", 在 update 中 加上关键字 就 变成了 修改器其实 "$" 字符 独立出现也是有意义的 , 我起名叫做代指符,$ 字符 在语句中代表了什么呢? `下标,位置`

`db.db_yao.find({"age":19})`

> {
> ​	"_id" : ObjectId("5c3f128355f17e734880f90e"),
> ​	"name" : "yao",
> ​	"age" : 19,
> ​	"list" : [
> ​		2,
> ​		6,
> ​		2
> ​	]
> }

然后我们的想将list中的6改为2,可以使用

`db.db_yao.update({"age":19},{$set:{"list.1":2}})`

其中list.1就代表索引的意思,但是若是这个array有很长那么使用索引显然不切实际

所以此时可以用"$":

`db.db_yao.update({"age":19,"list":6},{$set:{"list.$":2}})`

解释一下: 如果我们使用`update`的话, 满足条件的数据下标位置就会传递到 $ 字符中,在我们更新操作的时候就相当于对这个位置的元素进行操作

# 其他

- ## Limit 

    从这些 Document 中取出多少个

     `db.db_yao.find({}).limit(2)`

    就是选取两条Document, 从整个Collection的第一条 Document 开始选取两条

- ## Skip 

    要跳过多少个Document

    db.db_yao.find({}).skip(2)

    跳过第一,二条直接从第三条开始

- ## Limit + Skip

    实现跳过第一条,选取第二,三条的效果

    `db.db_yao.find({}).skip(1).limit(2)`

- ## Sort

    `db.db_yao.find({}).sort("age":1)`

    将`find`出来的`Document `按照 `price `进行升序/降序排列

    `1 `为升序 , `-1 `为降序