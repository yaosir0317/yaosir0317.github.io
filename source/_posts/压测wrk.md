---
title: 压测工具wrk
date: 2021-03-29 14:49:24
tags: Web
categories: Web
---

[wrk](https://github.com/wg/wrk)是一款开源的HTTP性能测试工具，它和`Apache Bench`同属于HTTP性能测试工具，它比`Apache Bench`功能更加强大，可以通过编写lua脚本来支持更加复杂的测试场景。

<!--more-->

# 常用参数

```
-c --conections：保持的连接数，连接数量不能少于线程数
-d --duration：压测持续时间(s)
-t --threads：使用的线程总数
-s --script：加载lua脚本
-H --header：在请求头部添加一些参数
--latency 打印详细的延迟统计信息
--timeout 请求的最大超时时间(s)
```

# 使用

## get请求

```
wrk -t 8 -c 100 -d 30 --latency http://127.0.0.1
```

## post请求发送form-data

发送`post`请求我们需要借用`lua`脚本

```lua
wrk.method = "POST"
wrk.body = "a=1&b=2"
wrk.headers["Content-Type"] = "application/x-www-form-urlencoded"
```

上面通过设置了`请求的方式`，`请求体`和`请求头`，再指定我们需要使用的`lua`脚本就可以了

```
 wrk -t 8 -c 100 -d 30 -s form.lua --latency http://127.0.0.1
```

## post请求发送json

同理通过`lua`脚本设置`请求的方式`，`请求体`和`请求头`

```
wrk.method = "POST"
wrk.body = '{"user": "test", "pwd": "test"}'
wrk.headers["Content-Type"] = "application/json"
```

再像上面那样指定我们需要使用的`lua`脚本就可以了

## 结果分析

```
Running 30s test @ http://127.0.0.1
  8 threads and 100 connections
  Thread Stats         Avg(均值)    Stdev(标准差)     Max(最大值)   +/- Stdev(正负一个标准差占比)
    Latency(响应延迟)   14.55ms      2.02ms           31.59ms      76.70%
    Req/Sec(每秒请求)   828.16       85.69            0.97k        60.46%
  Latency Distribution(延迟分布)
     50%   14.44ms
     75%   15.76ms
     90%   16.63ms
     99%   21.07ms
  198091 requests in 30.05s, 29.66MB read
Requests/sec:   6592.29
Transfer/sec:   0.99MB
```

