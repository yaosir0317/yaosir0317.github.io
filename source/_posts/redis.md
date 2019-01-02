---
title: Redis
date: 2019-01-01 17:44:34
tags: Redis
categories: Redis
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