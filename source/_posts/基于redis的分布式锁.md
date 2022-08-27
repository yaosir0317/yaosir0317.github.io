---
title: 基于redis的分布式锁
date: 2021-12-22 09:43:00
tags: Redis
categories: Redis
---

今天突然看到同事处理交易回调时，为了保证数据的正确，使用了基于redis的分布式锁，锁的实现和使用如下：

```python
@contextmanager
def redis_dist_lock(key, value=1, timeout=60, cli=redis_cache_default):
    """
    redis分布式锁
    @param key:键
    @param value:值
    @param nx:键不存在才设置
    @param timeout:过期时间
    @param cli: redis client
    @return:
    """
    unlock_script = """
    if redis.call("get",KEYS[1]) == ARGV[1] then
        return redis.call("del",KEYS[1])
    else
        return 0
    end
    """
    lock = cli.set(key, value, nx=True, ex=timeout)
    try:
        yield lock
    finally:
        if lock:
            unlock = cli.register_script(unlock_script)
            unlock(keys=[key], args=[value])
 
# 使用方式
with redis_dist_lock(key=webhook_id) as lock:
    ...
```

然后我和同事说这个锁加的有点问题，她说是哪里的问题呢，redis实现分布式锁主要的实现不就是通过`setnx`吗, 为防止程序宕机导致锁不成被释放，也设置了超时时间。

那下面就来看看这个锁的问题所在。

<!--more-->

# 释放了不是自己加的锁

加锁的时候`value`, 全部使用的`1`这个值，那么试想一下下面的场景

1. `订单a`的第一次回调，`线程a`加锁key=a，value=1，expire=10s，但是处理a的线程由于网络拥堵，没能在10s内处理完成，还在处理中，此时，锁自动过期，`订单a的锁`可以被其他线程获得
2. 此时`订单a`的第二次回调，`线程b`获得锁，同样的key=a，value=1，expire=10s，此时`线程a`处理完成，执行`finally`, 发现此时锁的value和加锁时一样都为1，因此释放了锁
3. 此时`订单a`的第三次回调又来了，发现没有锁，于是`线程c`获得锁，同样的key=a，value=1，expire=10s，此时出现了两个线程都获得锁的情况，如果`线程b`先处理完成又会释放 `线程b`加的锁，那么锁又可以被其他线程设置

所以要解决这个问题，需要保证加锁时value是唯一的，这也是为什么使用lua脚本来释放锁的原因。

# 正确设置锁超时

为防止加锁进程出现问题，导致锁不会被释放的问题，引入的超时时间，那么多久的超时时间合适呢，太短也会出现当前任务没处理完，锁就被释放问题，设置时间过长，一旦发生宕机重启，就意味着 1 小时内，分布式锁的服务全部节点不可用。

这时可以借鉴**Redisson**的方案，我们可以让获得锁的线程开启一个**守护线程**，用来给快要过期的锁「续航」。加锁的时候设置一个过期时间，同时客户端开启一个「守护线程」，定时去检测这个锁的失效时间。如果快要过期，但是业务逻辑还没执行完成，自动对这个锁进行续期，重新设置过期时间。

# 可重入锁

当一个线程执行一段代码成功获取锁之后，继续执行时，又遇到加锁的代码，可重入性就就保证线程能继续执行，而不可重入就是需要等待锁释放之后，再次获取锁成功，才能继续往下执行。

假设 X 线程在 a 方法获取锁之后，继续执行 b 方法，如果此时**不可重入**，线程就必须等待锁释放，再次争抢锁。锁明明是被 X 线程拥有，却还需要等待自己释放锁，然后再去抢锁，这看起来就很奇怪。

可重入锁可以使用redis的hash结构来实现

加锁

```lua
if redis.call('hexists', KEYS[1], ARGV[1]) == 1 then
    redis.call('hincrby', KEYS[1], ARGV[1], 1)
    redis.call('expire', KEYS[1], ARGV[2])
    return 1
end
if redis.call('exists', KEYS[1]) == 1 then
	return 0
else
    redis.call('hset', KEYS[1], ARGV[1], 1)
    redis.call('expire', KEYS[1], ARGV[2])
end
return 1

加锁代码首先使用 hexists判断当前 lock 对应的 hash 表中是否存在 uuid 这个键对应锁是否存在。
如果存在，则使用使用 hincrby 加 1，再次设置过期时间。
然后用exists判断锁是否存在
如果锁不存在的话，直接使用hset创建一个键为 lock hash 表，并且为 Hash 表中键为 uuid 初始化为1， 设置过期时间。

最后如果上述两个逻辑都不符合，直接返回。
```

解锁

```lua
if redis.call('hexists', KEYS[1], ARGV[1]) == 0 then
	return nil
end
local count = redis.call('hincrby', KEYS[1], ARGV[1], -1)
if (count > 0) then
	return 0
else
	redis.call('del', KEYS[1])
	return 1
end
首先使用 hexists 判断 Redis Hash 表是否存给定锁。
如果 lock 对应 Hash 表不存在，或者 Hash 表不存在 uuid 这个 key，直接返回 nil。
若存在的情况下，代表当前锁被其持有，首先使用 hincrby使可重入次数减 1 ，然后判断计算之后可重入次数，若小于等于 0，则使用 del 删除这把锁。
```

# 主从架构带来的问题

到这里，这个锁基本可以满足大部分的需求了，但是也会存在一定的安全性问题，单机情况不能保证高可用，使用主从的话也会出现下面的情况

1. 客户端 A 在 master 节点获取锁成功后，还没有把获取锁的信息同步到 slave 的时候，master 宕机。
2. slave 被选举为新 master，这时候没有客户端 A 获取锁的数据，那么其他的客户端就可以加锁了

虽然概率极低，但是的确是存在这个风险，所以有更高安全性需求的同学可以研究下redis作者提出的[Redlock](https://redis.io/docs/reference/patterns/distributed-locks/)

