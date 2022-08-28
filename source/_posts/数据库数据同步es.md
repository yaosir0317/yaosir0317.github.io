---
title: 数据库数据同步es
date: 2021-08-07 14:50:03
tags: 关系型数据库
categories: 关系型数据库
---

最新需要做订单的模糊查询功能，根据订单的`用户邮箱`,`订单中产品的名称、系列`等等订单中的信息去搜索相关订单，显然这个场景使用关系行数据库的模糊查询是不现实的，因此使用非常适合做搜索功能的elasticsearch来做，然后需要解决的问题就变成了，怎么把数据库的数据同步到es

<!--more-->

# 方案一：使用框架的信号功能

例如Django框架中的`post_save`监控`model`的`save`行为，使用`post_delete`监控`delete`, 这样拿到数据的变化信息根据业务需求`同步发送/异步发送`到es中，从而实现数据库数据变化同步到es

**优点：**

- 实现简单，不需要额外的三方应用/模块

**缺点：**

- 一些场景不适用，比如django中`model.bulk_create`和`model.update`并不会调用model的`save()`方法，因此也不会触发`post_save`信号。

# 方案二：使用数据库的触发器

通过使用数据库的`trigger`来监听所有的`insert`, `update`, `delete`, 从而获得变化的数据进行同步

**优点：**

- 立即捕获数据的更改，实时处理更改事件。
- 触发器可以捕获所有变化的事件类型：INSERT、UPDATE 和 DELETE。

**缺点：**

- 触发器会增加原始语句的执行时间，从而影响数据库的性能。
- 创建和管理触发器会增加额外的操作复杂性。

# 方案三：通过更新时间查询变化数据

在数据表设置`updated_at`字段，记录数据最后的更新时间，记录下上次同步es的时间，通过sql查询

```
SELECT * FROM table WHERE updated_at > 'last_sync_to_es' ;
```

​	**优点：**

- 实现简单，仅通过数据库的查询就可以实现

**缺点：**

- 基于查询层来提取数据，这会给数据库带来额外的负载。
- 需要数据表存在一个列（此处为*updated_at*）来跟踪记录最后一次修改的时间。
- 无法获取物理删除的数据，逻辑删除的可以捕获

# 方案四(最终使用的方案)：基于数据库的主从数据同步实现

阿里的开源项目[canal](https://github.com/alibaba/canal)，它通过模拟 MySQL slave 的交互协议，伪装自己为 MySQL slave ，向 MySQL master 发送dump 协议，MySQL master 收到 dump 请求，开始推送 binary log 给 slave (即 canal )，canal 解析 binary log 对象，得到同步的数据，通过tcp或者发送到消息中间件，从而实现数据同步到es。

而我们使用的是`postgres`，因此采用的是谷歌云上的postgres-cdc服务通过pgsql的逻辑复制来实现的，从 9.4 版开始，PostgreSQL 提供了[逻辑复制](https://www.postgresql.org/docs/current/logical-replication.html) 以便在可能不同的物理机器上的不同 PostgreSQL 实例之间高效、安全地复制数据。从技术上讲，它是磁盘上的预写日志，它保存所有更改 PostgreSQL 数据库数据的事件，例如，插入、更新和删除。

**优点：**

- 捕获所有变化的事件类型：INSERT、UPDATE 和 DELETE。
- 不会影响数据库的性能。

**缺点：**

- 一些较低的数据库版本可能不被支持，例如非常旧的 PostgreSQL 版本（早于 9.4）不支持逻辑复制。