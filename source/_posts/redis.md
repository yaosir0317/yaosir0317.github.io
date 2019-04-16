---
title: 非关系型数据库之 Redis
date: 2019-01-01 17:44:34
tags: Redis
categories: 
	- 非关系型数据库
	- Redis
---

# Redis安装

## yum安装

```
yum install redis -y
```

## 源码安装

- 下载源码包`wget http://download.redis.io/releases/redis-4.0.10.tar.gz`

- 解压缩redis`tar -zxf redis-4.0.10.tar.gz `

    <!--more-->

- 进入redis源码，直接可以编译且安装`make && make install `

- 可以指定配置文件启动redis`vim /opt/redis-4.0.10/redis.conf `

> 1.更改bind参数，让redis可以远程访问
> ​	bind 0.0.0.0
> 2.更改redis的默认端口
> ​	port 6380
> 3.使用redis的密码进行登录
> ​	requirepass 登录redis的密码
> 4.指定配置文件启动
> ​	redis-server redis.conf 

- 通过新的端口和密码登录redis

> redis-cli -p 6380
> 登录后
> auth 密码

- redis还支持交互式的参数，登录数据库

> redis-cli -p 6380  -a  redis的密码  （这个不太安全）

- 通过登录redis，用命令查看redis的密码

```
config set  requirepass  新的密码     	#设置新密码
config get  requirepass  			#获取当前的密码
```

> tips:
>
> 过滤出文件的空白行和注释行,用于稍后再配置中使用
> grep -v "^#"  redis.conf |   grep  -v "^$"

# redis发布订阅

涉及三个角色

1.发布者
​	`publish  频道  消息`		给频道发消息
2.订阅者
​	`SUBSCRIBE  频道  `   	                订阅频道 
​	`PSUBSCRIBE 频道*  `		        支持模糊匹配的订阅
3.频道
​	`channel  频道名`                     自定义

**demo**

```python
import redis


class RedisHelper:

    def __init__(self):
        self.__conn = redis.Redis(host='10.211.55.4')
        self.chan_sub = 'fm104.5'
        self.chan_pub = 'fm104.5'

    def public(self, msg):
        self.__conn.publish(self.chan_pub, msg)
        return True

    def subscribe(self):
        pub = self.__conn.pubsub()
        pub.subscribe(self.chan_sub)
        pub.parse_response()
        return pub
```

订阅者

```python
from monitor.RedisHelper import RedisHelper
 
obj = RedisHelper()
redis_sub = obj.subscribe()
 
while True:
    msg = redis_sub.parse_response()
    print(msg)
```

发布者

```python
from monitor.RedisHelper import RedisHelper
 
obj = RedisHelper()
obj.public('hello')
```

# redis持久化

`Redis`是一种内存型数据库，一旦服务器进程退出，数据库的数据就会丢失，为了解决这个问题，`Redis`提供了两种持久化的方案，将内存中的数据保存到磁盘中，避免数据的丢失。

## RDB

`redis`提供了`RDB持久化`的功能，这个功能可以将`redis`在内存中的的状态保存到硬盘中，它可以**手动执行。**

也可以再`redis.conf`中配置，**定期执行**。

RDB持久化产生的RDB文件是一个**经过压缩**的**二进制文件**，这个文件被保存在硬盘中，redis可以通过这个文件还原数据库当时的状态。

- 在配置文件中添加参数，开启RDB功能,**注释不要写入配置文件中**

> redis.conf 写入:
> ​	port 6379
> ​	daemonize yes
> ​	logfile /data/6379/redis.log
> ​	dir /data/6379
> ​	dbfilename   yaoshao.rdb
> ​	save 900 1                      #rdb机制 每900秒 有1个修>改记录
> ​	save 300 10                    #每300秒        10个修改
> ​	记录
> ​	save 60  10000                #每60秒内        10000修>改记录

- 开启redis服务端，测试rdb功能

```
redis-server redis.conf
```

- 此时检查目录，/data/6379底下没有dbmp.rdb文件

- 通过save触发持久化，将数据写入RDB文件

```
127.0.0.1:6379> set age 18
OK
127.0.0.1:6379> save
OK
```



## AOF

记录服务器执行的所有变更操作命令（例如set del等），并在服务器启动时，通过重新执行这些命令来还原数据集
AOF 文件中的命令全部以redis协议的格式保存，新命令追加到文件末尾。
优点：最大程序保证数据不丢
缺点：日志记录非常大

```
redis-client   写入数据  >  redis-server   同步命令   >  AOF文件
```

- 开启aof功能，在redis.conf中添加参数

> port 6379
> daemonize yes
> logfile /data/6379/redis.log
> dir /data/6379
> appendonly yes
> appendfsync everysec

- 启动redis服务端，指定aof功能，测试持久化数据 

- 检查redis数据目录/data/6379/是否产生了aof文件

```
tail -f appendonly.aof # 实时检查aof文件信息
```

## 数据切换

**redis不重启之rdb数据切换到aof数据**

- 准备rdb的redis服务端

```
redis-server   rdb-redis.conf (这是在rdb持久化模式下)
```

- 切换rdb到aof

> redis-cli  登录redis，然后通过命令，激活aof持久化
> 127.0.0.1:6379>  CONFIG set appendonly yes	#用命令激活aof持久化(临时生效，注意写入到配置文件)
> OK
> 127.0.0.1:6379>  CONFIG SET save "" 			#关闭rdb持久化

- 将aof操作，写入到配置文件，永久生效，下次重启后生效

> port 6379
> daemonize yes 
> logfile /data/6379/redis.log
> dir /data/6379   
> #dbfilename   yaoshao.rdb
> #save 900 1  
> #save 300 10 
> #save 60  10000 
> appendonly yes
> appendfsync everysec

- 测试aof数据持久化 ,杀掉redis，重新启动
- 写入数据，检查aof文件

# 主从同步

> 原理：
> 1. 从服务器向主服务器发送 SYNC 命令。
> 2. 接到 SYNC 命令的主服务器会调用BGSAVE 命令，创建一个 RDB 文件，并使用缓冲区记录接下来执行的所有写命令。
> 3. 当主服务器执行完 BGSAVE 命令时，它会向从服务器发送 RDB 文件，而从服务器则会接收并载入这个文件。
> 4. 主服务器将缓冲区储存的所有写命令发送给从服务器执行。

- 检查redis数据库信息，主从状态的命令

    > redis-cli  -p 6379  info  检查数据库信息
    > redis-cli  -p 6379  info  replication  检查数据库主从信息

- 准备三个redis配置文件，通过端口的区分，启动三个redis数据库实例，然后配置主从复制

> redis-6379.conf 
> port 6379
> daemonize yes
> pidfile /data/6379/redis.pid
> loglevel notice
> logfile "/data/6379/redis.log"
> dbfilename dump.rdb
> dir /data/6379

- 通过命令快速生成配置文件

> `redis-6380.conf `
>
> sed "s/6379/6380/g" redis-6379.conf > redis-6380.conf 
> slaveof  127.0.0.1  6379   #指明主库的身份ip 和端口
>
> ------
>
> `redis-6381.conf `
>
> sed "s/6379/6381/g" redis-6379.conf > redis-6381.conf 
> slaveof  127.0.0.1  6379

- 启动三个数据库实例，检测redis主从同步方案

    > set  key  value # 主
    >
    > get key # 从

- redis主从赋值，故障手动切换

> 1.杀死6379的主库实例
> ​	kill 主库
>
> 2.手动切换主从身份
> ​	1.登录 redis-6380 ，通过命令，去掉自己的从库身份，等待连接
> ​		slaoveof no one  
> ​	2.登录redis-6381 ,通过命令，生成新的主人
> ​		slaveof 127.0.0.1 6380  
>
> 3.测试新的主从数据同步

# Redis-Sentinel

Redis-Sentinel是redis官方推荐的高可用性解决方案，
当用redis作master-slave的高可用时，如果master本身宕机，redis本身或者客户端都没有实现主从切换的功能。

而redis-sentinel就是一个独立运行的进程，用于监控多个master-slave集群，
自动发现master宕机，进行自动切换slave > master。

> sentinel主要功能如下：
>
> - 不时的监控redis是否良好运行，如果节点不可达就会对节点进行下线标识
> - 如果被标识的是主节点，sentinel就会和其他的sentinel节点“协商”，如果其他节点也人为主节点不可达，就会选举一个sentinel节点来完成自动故障转义
> - 在master-slave进行切换后，master_redis.conf、slave_redis.conf和sentinel.conf的内容都会发生改变，即master_redis.conf中会多一行slaveof的配置，sentinel.conf的监控目标会随之调换

## 安装配置

- 准备三个redis数据库实例（三个配置文件，通过端口区分）

> [root@localhost redis-4.0.10]# redis-server redis-6379.conf 
> [root@localhost redis-4.0.10]# redis-server redis-6380.conf 
> [root@localhost redis-4.0.10]# redis-server redis-6381.conf 

- 准备三个哨兵，准备三个哨兵的配置文件

> `redis-sentinel-26379.conf`
>
> port 26379  
> dir /var/redis/data/
> logfile "26379.log"
> sentinel monitor s15master 127.0.0.1 6379 2
> sentinel down-after-milliseconds s15master 30000
> sentinel parallel-syncs s15master 1
> sentinel failover-timeout s15master 180000
> daemonize yes

- 用sed生成`redis-sentinel-26380.conf `, `redis-sentinel-26381.conf `

- 启动三个哨兵

>  redis-sentinel redis-sentinel-26379.conf 
>  redis-sentinel redis-sentinel-26380.conf 
>  redis-sentinel redis-sentinel-26381.conf 

- 检查哨兵的通信状态

`redis-cli -p 26379  info sentinel `

> [root@localhost redis-4.0.10]# redis-cli -p 26379  info sentinel 
> #Sentinel
> sentinel_masters:1
> sentinel_tilt:0
> sentinel_running_scripts:0
> sentinel_scripts_queue_length:0
> sentinel_simulate_failure_flags:0
> master0:name=s15master,status=ok,address=127.0.0.1:6381,slaves=2,sentinels=3

- 杀死一个redis主库，6379节点，等待30s以内，检查6380和6381的节点状态

> kill 6379主节点
> redis-cli -p 6380 info replication 
> redis-cli -p 6381 info replication 

- 恢复6379节点的数据库，查看是否将6379添加为新的slave身份

    (原理就是更改redis的配置文件，切换主从身份)

# redis-cluster

- 准备6个redis数据库实例，准备6个配置文件redis-{7000...7005}配置文件

    ```
    port 7000
    daemonize yes
    dir "/opt/redis/data"
    logfile "7000.log"
    dbfilename "dump-7000.rdb"
    cluster-enabled yes   #开启集群模式
    cluster-config-file nodes-7000.conf　　#集群内部的配置文件
    cluster-require-full-coverage no　　#redis cluster需要16384个slot都正常的时候才能对外提供服务，换句话说，只要任何一个slot异常那么整个cluster不对外提供服务。 因此生产环境一般为no
    ```

> -rw-r--r-- 1 root root 151 Jan  2 19:26 redis-7000.conf
> -rw-r--r-- 1 root root 151 Jan  2 19:27 redis-7001.conf
> -rw-r--r-- 1 root root 151 Jan  2 19:27 redis-7002.conf
> -rw-r--r-- 1 root root 151 Jan  2 19:27 redis-7003.conf
> -rw-r--r-- 1 root root 151 Jan  2 19:27 redis-7004.conf
> -rw-r--r-- 1 root root 151 Jan  2 19:27 redis-7005.conf

- 启动6个redis数据库实例

> [root@localhost yaorediscluster]# redis-server redis-7000.conf 
> [root@localhost yaorediscluster]# redis-server redis-7001.conf 
> [root@localhost yaorediscluster]# redis-server redis-7002.conf 
> [root@localhost yaorediscluster]# redis-server redis-7003.conf 
> [root@localhost yaorediscluster]# redis-server redis-7004.conf 
> [root@localhost yaorediscluster]# redis-server redis-7005.conf 

配置ruby语言环境

> 1.下载ruby语言的源码包，编译安装
> ​		`wget https://cache.ruby-lang.org/pub/ruby/2.3/ruby-2.3.1.tar.gz`
> 2.解压缩
> ​		`./configure --prefix=/opt/ruby/	`   释放makefile
> ​		`make && make install`     编译且安装
> 3.下载安装ruby操作redis的模块包
> ​		`wget http://rubygems.org/downloads/redis-3.3.0.gem`
>
> 4.配置ruby的环境变量
> echo $PATH
>
> vim /etc/profile
> 写入最底行
> `PATH=$PATH:/opt/ruby/bin/`
> 读取文件
> `source /etc/profile `
>
> 5.通过ruby的包管理工具去安装redis包，安装后会生成一个redis-trib.rb这个命令
> 一键创建redis-cluster 其实就是分配主从关系 以及 槽位分配 slot槽位分配
> /opt/redis-4.0.10/src/redis-trib.rb create --replicas 1 127.0.0.1:7000 127.0.0.1:7001 127.0.0.1:7002 127.0.0.1:7003 127.0.0.1:7004 127.0.0.1:7005
>
> 6.检查节点主从状态
> `redis-cli -p 7000  info replication `
>
> 7.向redis集群写入数据，查看数据流向
> `redis-cli -p 7000`    #这里会将key自动的重定向，放到某一个节点的slot槽位中
> `set  name  yao `
> `set  addr  beijing  `

# 操作

**String** 操作，String 在内存中格式是一个 name 对应一个 value 来存储

> set(name, value, ex=None, px=None, nx=False, xx=False)
>
> ```python
> # 在Redis中设置值，默认，不存在则创建，存在则修改
> # 参数：
>      ex，过期时间（秒）
>      px，过期时间（毫秒）
>      nx，如果设置为True，则只有name不存在时，当前set操作才执行
>      xx，如果设置为True，则只有name存在时，岗前set操作才执行
> ```
>
> setnx(name, value)
>
> ```
> # 设置值，只有name不存在时，执行设置操作（添加）
> ```
>
> setex(name, value, time)
>
> ```
> # 设置值
> # 参数：
>      time，过期时间（数字秒 或 timedelta对象）
> ```
>
> psetex(name, time_ms, value)
>
> ```
> # 设置值
> # 参数：
>      time_ms，过期时间（数字毫秒 或 timedelta对象）
> ```
>
> mset(*args, **kwargs)
>
> ```python
> # 批量设置值
> # 如：
>     mset(k1='v1', k2='v2')
>     或
>     mget({'k1': 'v1', 'k2': 'v2'})
> ```
>
> get(name)
>
> ```
> # 获取值
> ```
>
> mget(keys, *args)
>
> ```python
> # 批量获取
> # 如：
>     mget('ylr', 'nick')
>     或
>     r.mget(['ylr', 'nick'])
> ```
>
> getset(name, value)
>
> ```
> # 设置新值并获取原来的值
> ```
>
> getrange(key, start, end)
>
> ```python
>  # 获取子序列（根据字节获取，非字符）
>  # 参数：
>      name，Redis 的 name
>      start，起始位置（字节）
>      end，结束位置（字节）
>  # 如： "索宁" ，0-3表示 "索"
> ```
>
> setrange(name, offset, value)
>
> ```
> # 修改字符串内容，从指定字符串索引开始向后替换（新值太长时，则向后添加）
> # 参数：
>      offset，字符串的索引，字节（一个汉字三个字节）
>      value，要设置的值
> ```
>
> setbit(name, offset, value)
>
> ```python
> # 对name对应值的二进制表示的位进行操作
>  
> # 参数：
>     # name，redis的name
>     # offset，位的索引（将值变换成二进制后再进行索引）
>     # value，值只能是 1 或 0
>  
> # 注：如果在Redis中有一个对应： n1 = "foo"，
>         那么字符串foo的二进制表示为：01100110 01101111 01101111
>     所以，如果执行 setbit('n1', 7, 1)，则就会将第7位设置为1，
>         那么最终二进制则变成 01100111 01101111 01101111，即："goo"
> ```
>
> getbit(name, offset)
>
> ```
> # 获取name对应的值的二进制表示中的某位的值 （0或1）
> ```
>
> bitcount(key, start=None, end=None)
>
> ```python
>  # 获取name对应的值的二进制表示中 1 的个数
>  # 参数：
>      key，Redis的name
>      start，位起始位置
>      end，位结束位置
> ```
>
> bitop(operation, dest, *keys)
>
> ```python
> # 获取多个值，并将值做位运算，将最后的结果保存至新的name对应的值
>  
> # 参数：
>      operation,AND（并） 、 OR（或） 、 NOT（非） 、 XOR（异或）
>      dest, 新的Redis的name
>      *keys,要查找的Redis的name
>  
> # 如：
>     bitop("AND", 'new_name', 'n1', 'n2', 'n3')
>      获取Redis中n1,n2,n3对应的值，然后讲所有的值做位运算（求并集），然后将结果保存 new_name 对应的值中
> ```
>
> strlen(name)
>
> ```
> # 返回name对应值的字节长度（一个汉字3个字节）
> ```
>
> incr(self, name, amount=1)
>
> ```python
> # 自增 name对应的值，当name不存在时，则创建name＝amount，否则，则自增。
>  
> # 参数：
>      name,Redis的name
>      amount,自增数（必须是整数）
>  
> # 注：同incrb
> ```
>
> incrbyfloat(self, name, amount=1.0)
>
> ```python
> # 自增 name对应的值，当name不存在时，则创建name＝amount，否则，则自增。
>  
> # 参数：
>      name,Redis的name
>      amount,自增数（浮点型）
> ```
>
> decr(self, name, amount=1)
>
> ```python
> # 自减 name对应的值，当name不存在时，则创建name＝amount，否则，则自减。
>  
> # 参数：
>      name,Redis的name
>      amount,自减数（整数）
> ```
>
> append(key, value)
>
> ```python
> # 在redis name对应的值后面追加内容
>  
> # 参数：
>     key, redis的name
>     value, 要追加的字符串
> ```

**Hash** 操作，redis 中 Hash 在内存中的存储格式类似字典

>  hset(name, key, value)
>
> ```python
> # name对应的hash中设置一个键值对（不存在，则创建；否则，修改）
>  
> # 参数：
>      name，redis的name
>      key，name对应的hash中的key
>      value，name对应的hash中的value
>  
> # 注：
>      hsetnx(name, key, value),当name对应的hash中不存在当前key时则创建（相当于添加）
> ```
>
> hmset(name, mapping)
>
> ```python
> # 在name对应的hash中批量设置键值对
>  
> # 参数：
>      name，redis的name
>      mapping，字典，如：{'k1':'v1', 'k2': 'v2'}
>  
> # 如：
>     # r.hmset('xx', {'k1':'v1', 'k2': 'v2'})
> ```
>
> hget(name,key)
>
> ```
> # 在name对应的hash中获取根据key获取value
> ```
>
> hmget(name, keys, *args)
>
> ```python
> # 在name对应的hash中获取多个key的值
>  
> # 参数：
>      name，reids对应的name
>      keys，要获取key集合，如：['k1', 'k2', 'k3']
>      *args，要获取的key，如：k1,k2,k3
>  
> # 如：
>      r.mget('xx', ['k1', 'k2'])
>      或
>      print r.hmget('xx', 'k1', 'k2')
> ```
>
> hgetall(name)
>
> ```
> # 获取name对应hash的所有键值
> ```
>
> hlen(name)
>
> ```
> # 获取name对应的hash中键值对的个数
> ```
>
> hkeys(name)
>
> ```
> # 获取name对应的hash中所有的key的值
> ```
>
> hvals(name)
>
> ```
> # 获取name对应的hash中所有的value的值
> ```
>
> hexists(name, key)
>
> ```
> # 检查name对应的hash是否存在当前传入的key
> ```
>
> hdel(name,*keys)
>
> ```
> # 将name对应的hash中指定key的键值对删除
> ```
>
> hincrby(name, key, amount=1)
>
> ```
>  自增name对应的hash中的指定key的值，不存在则创建key=amount 参数：
>      name，redis中的name
>      key， hash对应的key
>      amount，自增数（整数）
> ```
>
> hincrbyfloat(name, key, amount=1.0)
>
> ```python
> # 自增name对应的hash中的指定key的值，不存在则创建key=amount
>  
> # 参数：
>     # name，redis中的name
>     # key， hash对应的key
>     # amount，自增数（浮点数）
>  
> # 自增name对应的hash中的指定key的值，不存在则创建key=amount
> ```
>
> hscan(name, cursor=0, match=None, count=None)
>
> ```python
> # 增量式迭代获取，对于数据大的数据非常有用，hscan可以实现分片的获取数据，并非一次性将数据全部获取完，从而放置内存被撑爆
>  
> # 参数：
>     # name，redis的name
>     # cursor，游标（基于游标分批取获取数据）
>     # match，匹配指定key，默认None 表示所有的key
>     # count，每次分片最少获取个数，默认None表示采用Redis的默认分片个数
>  
> # 如：
>     # 第一次：cursor1, data1 = r.hscan('xx', cursor=0, match=None, count=None)
>     # 第二次：cursor2, data1 = r.hscan('xx', cursor=cursor1, match=None, count=None)
>     # ...
>     # 直到返回值cursor的值为0时，表示数据已经通过分片获取完毕
> ```
>
> hscan_iter(name, match=None, count=None)
>
> ```python
> # 利用yield封装hscan创建生成器，实现分批去redis中获取数据
>  
> # 参数：
>     # match，匹配指定key，默认None 表示所有的key
>     # count，每次分片最少获取个数，默认None表示采用Redis的默认分片个数
>  
> # 如：
>     # for item in r.hscan_iter('xx'):
>     #     print item
> ```

**List** 操作，redis 中的 List 在在内存中按照一个 name 对应一个 List 来存储，像变量对应一个列表。

> lpush(name,values)
>
> ```python
> # 在name对应的list中添加元素，每个新的元素都添加到列表的最左边
>  
> # 如：
>     # r.lpush('oo', 11,22,33)
>     # 保存顺序为: 33,22,11
>  
> # 扩展：
>     # rpush(name, values) 表示从右向左操作
> ```
>
> lpushx(name,value)
>
> ```
> # 在name对应的list中添加元素，只有name已经存在时，值添加到列表的最左边
>  
> # 更多：
>     # rpushx(name, value) 表示从右向左操作
> ```
>
> llen(name)
>
> ```
> # name对应的list元素的个数
> ```
>
> linsert(name, where, refvalue, value))
>
> ```python
> # 在name对应的列表的某一个值前或后插入一个新值
>  
> # 参数：
>     # name，redis的name
>     # where，BEFORE或AFTER
>     # refvalue，标杆值，即：在它前后插入数据
>     # value，要插入的数据
> ```
>
> r.lset(name, index, value)
>
> ```python
> # 对name对应的list中的某一个索引位置重新赋值
>  
> # 参数：
>     # name，redis的name
>     # index，list的索引位置
>     # value，要设置的值
> ```
>
> r.lrem(name, value, num)
>
> ```python
> # 在name对应的list中删除指定的值
>  
> # 参数：
>     # name，redis的name
>     # value，要删除的值
>     # num，  num=0，删除列表中所有的指定值；
>            # num=2,从前到后，删除2个；
>            # num=-2,从后向前，删除2个
> ```
>
> lpop(name)
>
> ```
> # 在name对应的列表的左侧获取第一个元素并在列表中移除，返回值则是第一个元素
>  
> # 更多：
>     # rpop(name) 表示从右向左操作
> ```
>
> lindex(name, index)
>
> ```
> # 在name对应的列表中根据索引获取列表元素
> ```
>
> lrange(name, start, end)
>
> ```
> # 在name对应的列表分片获取数据
> # 参数：
>     # name，redis的name
>     # start，索引的起始位置
>     # end，索引结束位置
> ```
>
> ltrim(name, start, end)
>
> ```
> # 在name对应的列表中移除没有在start-end索引之间的值
> # 参数：
>     # name，redis的name
>     # start，索引的起始位置
>     # end，索引结束位置
> ```
>
> rpoplpush(src, dst)
>
> ```
> # 从一个列表取出最右边的元素，同时将其添加至另一个列表的最左边
> # 参数：
>     # src，要取数据的列表的name
>     # dst，要添加数据的列表的name
> ```
>
> blpop(keys, timeout)
>
> ```python
> # 将多个列表排列，按照从左到右去pop对应列表的元素
>  
> # 参数：
>     # keys，redis的name的集合
>     # timeout，超时时间，当元素所有列表的元素获取完之后，阻塞等待列表内有数据的时间（秒）, 0 表示永远阻塞
>  
> # 更多：
>     # r.brpop(keys, timeout)，从右向左获取数据
> ```
>
> brpoplpush(src, dst, timeout=0)
>
>
>
> ```python
> # 从一个列表的右侧移除一个元素并将其添加到另一个列表的左侧
>  
> # 参数：
>     # src，取出并要移除元素的列表对应的name
>     # dst，要插入元素的列表对应的name
>     # timeout，当src对应的列表中没有数据时，阻塞等待其有数据的超时时间（秒），0 表示永远阻塞
> ```
>
> 自定义增量迭代
>
> ```python
> # 由于redis类库中没有提供对列表元素的增量迭代，如果想要循环name对应的列表的所有元素，那么就需要：
>     # 1、获取name对应的所有列表
>     # 2、循环列表
> # 但是，如果列表非常大，那么就有可能在第一步时就将程序的内容撑爆，所有有必要自定义一个增量迭代的功能：
>  
> def list_iter(name):
>     """
>     自定义redis列表增量迭代
>     :param name: redis中的name，即：迭代name对应的列表
>     :return: yield 返回 列表元素
>     """
>     list_count = r.llen(name)
>     for index in xrange(list_count):
>         yield r.lindex(name, index)
>  
> # 使用
> for item in list_iter('pp'):
>     print item
> ```

**Set** 操作，Set 集合就是不允许重复的列表

> sadd(name,values)
>
> ```
> # name对应的集合中添加元素
> ```
>
> scard(name)
>
> ```
> # 获取name对应的集合中元素个数
> ```
>
> sdiff(keys, *args)
>
> ```
> # 在第一个name对应的集合中且不在其他name对应的集合的元素集合
> ```
>
> sdiffstore(dest, keys, *args)
>
> ```
> # 获取第一个name对应的集合中且不在其他name对应的集合，再将其新加入到dest对应的集合中
> ```
>
> sinter(keys, *args)
>
> ```
> # 获取多一个name对应集合的并集
> ```
>
> sinterstore(dest, keys, *args)
>
> ```
> # 获取多一个name对应集合的并集，再讲其加入到dest对应的集合中
> ```
>
> sismember(name, value)
>
> ```
> # 检查value是否是name对应的集合的成员
> ```
>
> smembers(name)
>
> ```
> # 获取name对应的集合的所有成员
> ```
>
> smove(src, dst, value)
>
> ```
> # 将某个成员从一个集合中移动到另外一个集合
> ```
>
> spop(name)
>
> ```
> # 从集合的右侧（尾部）移除一个成员，并将其返回
> ```
>
> srandmember(name, numbers)
>
> ```
> # 从name对应的集合中随机获取 numbers 个元素
> ```
>
> srem(name, values)
>
> ```
> # 在name对应的集合中删除某些值
> ```
>
> sunion(keys, *args)
>
> ```
> # 获取多一个name对应的集合的并集
> ```
>
> sunionstore(dest,keys, *args)
>
> ```
> # 获取多一个name对应的集合的并集，并将结果保存到dest对应的集合中
> ```
>
> sscan(name, cursor=0, match=None, count=None)
> sscan_iter(name, match=None, count=None)
>
> ```
> # 同字符串的操作，用于增量迭代分批获取元素，避免内存消耗太大
> ```

**有序集合**，在集合的基础上，为每个元素排序；元素的排序需要根据另外一个值来进行比较，所以对于有序集合，每一个元素有两个值：值和分数，分数是专门来做排序的。

> zadd(name, *args, **kwargs)
>
> ```python
> # 在name对应的有序集合中添加元素
> # 如：
>      # zadd('zz', 'n1', 1, 'n2', 2)
>      # 或
>      # zadd('zz', n1=11, n2=22)
> ```
>
>  zcard(name)
>
> ```
> # 获取name对应的有序集合元素的数量
> ```
>
> zcount(name, min, max)
>
> ```
> # 获取name对应的有序集合中分数 在 [min,max] 之间的个数
> ```
>
> zincrby(name, value, amount)
>
> ```
> # 自增name对应的有序集合的 name 对应的分数
> ```
>
> r.zrange( name, start, end, desc=False, withscores=False, score_cast_func=float)
>
> ```python
> # 按照索引范围获取name对应的有序集合的元素
>  
> # 参数：
>     # name，redis的name
>     # start，有序集合索引起始位置（非分数）
>     # end，有序集合索引结束位置（非分数）
>     # desc，排序规则，默认按照分数从小到大排序
>     # withscores，是否获取元素的分数，默认只获取元素的值
>     # score_cast_func，对分数进行数据转换的函数
>  
> # 更多：
>     # 从大到小排序
>     # zrevrange(name, start, end, withscores=False, score_cast_func=float)
>  
>     # 按照分数范围获取name对应的有序集合的元素
>     # zrangebyscore(name, min, max, start=None, num=None, withscores=False, score_cast_func=float)
>     # 从大到小排序
>     # zrevrangebyscore(name, max, min, start=None, num=None, withscores=False, score_cast_func=float)
> ```
>
> zrank(name, value)
>
> ```
> # 获取某个值在 name对应的有序集合中的排行（从 0 开始）
>  
> # 更多：
>     # zrevrank(name, value)，从大到小排序
> ```
>
> zrangebylex(name, min, max, start=None, num=None)
>
> ```python
> # 当有序集合的所有成员都具有相同的分值时，有序集合的元素会根据成员的 值 （lexicographical ordering）来进行排序，而这个命令则可以返回给定的有序集合键 key 中， 元素的值介于 min 和 max 之间的成员
> # 对集合中的每个成员进行逐个字节的对比（byte-by-byte compare）， 并按照从低到高的顺序， 返回排序后的集合成员。 如果两个字符串有一部分内容是相同的话， 那么命令会认为较长的字符串比较短的字符串要大
>  
> # 参数：
>     # name，redis的name
>     # min，左区间（值）。 + 表示正无限； - 表示负无限； ( 表示开区间； [ 则表示闭区间
>     # min，右区间（值）
>     # start，对结果进行分片处理，索引位置
>     # num，对结果进行分片处理，索引后面的num个元素
>  
> # 如：
>     # ZADD myzset 0 aa 0 ba 0 ca 0 da 0 ea 0 fa 0 ga
>     # r.zrangebylex('myzset', "-", "[ca") 结果为：['aa', 'ba', 'ca']
>  
> # 更多：
>     # 从大到小排序
>     # zrevrangebylex(name, max, min, start=None, num=None)
> ```
>
> zrem(name, values)
>
> ```
> # 删除name对应的有序集合中值是values的成员
>  
> # 如：zrem('zz', ['s1', 's2'])
> ```
>
> zremrangebyrank(name, min, max)
>
> ```
> # 根据排行范围删除
> ```
>
> zremrangebyscore(name, min, max)
>
> ```
> # 根据分数范围删除
> ```
>
> zremrangebylex(name, min, max)
>
> ```
> # 根据值返回删除
> ```
>
> zscore(name, value)
>
> ```
> # 获取name对应有序集合中 value 对应的分数
> ```
>
> zinterstore(dest, keys, aggregate=None)
>
> ```
> # 获取两个有序集合的交集，如果遇到相同值不同分数，则按照aggregate进行操作
> # aggregate的值为:  SUM  MIN  MAX
> ```
>
> zunionstore(dest, keys, aggregate=None)
>
> ```
> # 获取两个有序集合的并集，如果遇到相同值不同分数，则按照aggregate进行操作
> # aggregate的值为:  SUM  MIN  MAX
> ```
>
> zscan(name, cursor=0, match=None, count=None, score_cast_func=float)
> zscan_iter(name, match=None, count=None,score_cast_func=float)
>
> ```
> # 同字符串相似，相较于字符串新增score_cast_func，用来对分数进行操作
> ```

**其它** 常用操作

> delete(*names)
>
> ```
> # 根据删除redis中的任意数据类型
> ```
>
>  exists(name)
>
> ```
> # 检测redis的name是否存在
> ```
>
> keys(pattern='*')
>
> ```
> # 根据模型获取redis的name
>  
> # 更多：
>     # KEYS * 匹配数据库中所有 key 。
>     # KEYS h?llo 匹配 hello ， hallo 和 hxllo 等。
>     # KEYS h*llo 匹配 hllo 和 heeeeello 等。
>     # KEYS h[ae]llo 匹配 hello 和 hallo ，但不匹配 hillo
> ```
>
> expire(name ,time)
>
> ```
> # 为某个redis的某个name设置超时时间
> ```
>
> rename(src, dst)
>
> ```
> # 对redis的name重命名为
> ```
>
> move(name, db))
>
> ```
> # 将redis的某个值移动到指定的db下
> ```
>
> randomkey()
>
> ```
> # 随机获取一个redis的name（不删除）
> ```
>
> type(name)
>
> ```
> # 获取name对应值的类型
> ```
>
> scan(cursor=0, match=None, count=None)
> scan_iter(match=None, count=None)
>
> ```
> # 同字符串操作，用于增量迭代获取key
> ```

# 管道

默认情况下，redis-py 每次在执行请求时都会创建和断开一次连接操作（连接池申请连接，归还连接池），如果想要在一次请求中执行多个命令，则可以使用 pipline 实现一次请求执行多个命令，并且默认情况下 pipline 是原子性操作。

```python
import redis
 
pool = redis.ConnectionPool(host='10.211.55.4', port=6379)
 
r = redis.Redis(connection_pool=pool)
 
# pipe = r.pipeline(transaction=False)
pipe = r.pipeline(transaction=True)
 
r.set('name', 'nick')
r.set('age', '18')
 
pipe.execute()
```

