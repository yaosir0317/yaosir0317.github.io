---
title: 基于Python的爬虫之二 Scrapy爬虫框架
date: 2019-03-01 15:47:20
tags: Python
categories: Python
---

Scrapy是一个为了爬取网站数据，提取结构性数据而编写的应用框架。 可以应用在包括数据挖掘，信息处理或存储历史数据等一系列的程序中。

<!--more-->

# 使用

## Begin

创建scrapy项目:

```
scrapy startproject projectName 
```

创建爬虫文件

```python
cd projectName
scrapy genspider spiderName www.xxx.com  # 一般以域名命名
```

项目目录及文件

![](scrapy/1.png)

- items.py    设置数据存储模板，用于结构化数据，如：Django的Model
- pipelines    数据处理行为，如：一般结构化的数据持久化
- settings.py 配置文件，如：递归的层数、并发数，延迟下载等
- spiders      爬虫目录，如：创建文件，编写爬虫规则

## 解析+持久化存储

### 基于终端指令的持久化存储

spiderBoss.py

```python
# -*- coding: utf-8 -*-
import scrapy


class SpiderbossSpider(scrapy.Spider):
    # 爬虫文件的名称
    name = 'spiderBoss'
    # 允许的域名
    # allowed_domains = ['www.xxx.com']
    # 起始url列表,列表内url,依次在parse方法执行
    start_urls = ['https://www.zhipin.com/c101010100/?query=%E7%88%AC%E8%99%AB&page=1&ka=page-1']

    def parse(self, response):
        result = []
        data_list = response.xpath("//div[@class='job-list']//ul/li")

        # 单个用extract_first,多个使用extract
        for data in data_list:
            job_name = data.xpath("./div/div[1]/h3/a/div/text()").extract_first()
            salary = data.xpath("./div/div[1]/h3/a/span/text()").extract_first()
            company = data.xpath("./div/div[2]/div/h3/a/text()").extract_first()
            dic = {
                "job_name": job_name,
                "salary": salary,
                "company": company
            }
            result.append(dic)
            print(dic)
        return result
ps:
    settings配置解决中文乱码
    FEED_EXPORT_ENCODING = 'GBK'
```

项目启动

```python
scrapy crawl spiderBoss  		    # 正常启动
scrapy crawl spiderBoss --nolog 	# 启动且不显示日志
```

基于终端指令的持久化存储

```
scrapy crawl spiderBoss -o fileName  # 用此命令启动就可实现基于终端指令的持久化存储
# 支持的文件格式
# 'json', 'jsonlines', 'jl', 'csv', 'xml', 'marshal', 'pickle'
```

## 基于管道的持久化存储

spiderBoss.py

```python
# -*- coding: utf-8 -*-
import scrapy

from ..items import ProjectbossItem


class SpiderbossSpider(scrapy.Spider):
    # 爬虫文件的名称
    name = 'spiderBoss'
    # 允许的域名
    # allowed_domains = ['www.xxx.com']
    # 起始url列表,列表内url,依次在parse方法执行
    start_urls = ['https://www.zhipin.com/c101010100/?query=%E7%88%AC%E8%99%AB&page=1&ka=page-1']
    url_page = "https://www.zhipin.com/c101010100/?query=爬虫&page=%s&ka=page-2"
    page = 1

    # 解析+管道持久化存储
    def parse(self, response):
        data_list = response.xpath("//div[@class='job-list']//ul/li")

        # 单个用extract_first,多个使用extract
        for data in data_list:
            # 实例化一个item对象
            item = ProjectbossItem()
            job_name = data.xpath("./div/div[1]/h3/a/div/text()").extract_first()
            salary = data.xpath("./div/div[1]/h3/a/span/text()").extract_first()
            company = data.xpath("./div/div[2]/div/h3/a/text()").extract_first()

            # 将解析到的数据全部封装到item对象中
            item["job_name"] = job_name
            item["salary"] = salary
            item["company"] = company

            # 将item提交给管道
            yield item

        # 分页的请求
        if self.page <= 10:
            self.page += 1
            new_url = format(self.url_page % self.page)
            # 手动发起请求
            yield scrapy.Request(url=new_url, callback=self.parse)

```

items.py

```python
# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ProjectbossItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    job_name = scrapy.Field()
    salary = scrapy.Field()
    company = scrapy.Field()
```

pipelines.py

```python
# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql
from redis import Redis


# 存入txt文档
class ProjectbossPipeline(object):

    f = None

    def open_spider(self, spider):
        self.f = open("boss.txt", "w", encoding="utf-8")

    # 爬虫文件每向管道提交一次item,则该方法就会被调用一次.
    # 参数:item 就是管道接收到的item类型对象
    def process_item(self, item, spider):
        self.f.write(item["job_name"] + "----" + item["salary"] + "----" + item["company"]  + "\n")
        # 返回给下一个即将被执行的管道类
        return item

    def close_spider(self, spider):
        self.f.close()


# 存入redis
class RedisbossPipeline(object):

    redis_obj = None

    def open_spider(self, spider):
        self.redis_obj = Redis(host="127.0.0.1", port=6379)

    # 爬虫文件每向管道提交一次item,则该方法就会被调用一次.
    # 参数:item 就是管道接收到的item类型对象
    def process_item(self, item, spider):
        dic = {
            'job_name': item['job_name'],
            'salary': item['salary'],
            'company': item['company']
        }
        self.redis_obj.lpush('boss', dic)
        # 返回给下一个即将被执行的管道类
        return item

# 存入mysql
class MysqlbossPipeline(object):

    mysql_obj = None
    cursor = None

    def open_spider(self, spider):
        self.mysql_obj = pymysql.Connect(host="127.0.0.1", port=3306, user="root", password="", db="db_boss", charset="utf8")

    # 爬虫文件每向管道提交一次item,则该方法就会被调用一次.
    # 参数:item 就是管道接收到的item类型对象
    def process_item(self, item, spider):
        self.cursor = self.mysql_obj.cursor()
        try:
            self.cursor.execute(
                'insert into boss values ("%s","%s","%s")' % (item['job_name'], item['salary'], item['company']))
            self.mysql_obj.commit()
        except Exception as e:
            print(e)
            self.mysql_obj.rollback()
        return item

    def close_spider(self, spider):
        self.mysql_obj.close()
        self.cursor.close()

```

settings.py

```python
# 解决中文乱码
FEED_EXPORT_ENCODING = 'GBK'

BOT_NAME = 'projectBoss'

SPIDER_MODULES = ['projectBoss.spiders']
NEWSPIDER_MODULE = 'projectBoss.spiders'

# User-Agent请求头
# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'

# 不遵循robots.txt
# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure item pipelines 数字代表优先级,小数优先级高
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
   'projectBoss.pipelines.ProjectbossPipeline': 300,
   'projectBoss.pipelines.RedisbossPipeline': 301,
   'projectBoss.pipelines.MysqlbossPipeline': 302,
}
# 日志等级
LOG_LEVEL = 'ERROR'
# 日志文件
LOG_FILE = './log.txt'
```

启动

```
scrapy crawl spiderBoss
```

## post请求

spider

```python
import scrapy


class PostSpider(scrapy.Spider):
    name = 'post'
    # allowed_domains = ['www.xxx.com']
    start_urls = ['https://fanyi.baidu.com/sug']

    def start_requests(self):
        # post请求参数
        data = {
            'kw':'dog'
        }
        for url in self.start_urls:
            # format_data:提交参数,callback回调parse
            yield scrapy.FormRequest(url=url,formdata=data,callback=self.parse)

    def parse(self, response):
        print(response.text)
```

# scrapy的五大组件

Scrapy框架主要由五大组件组成，它们分别是调度器(Scheduler)、下载器(Downloader)、爬虫（Spider）和实体管道(Item Pipeline)、Scrapy引擎(Scrapy Engine)。

## 调度器

调度器，说白了可以想像成一个URL（抓取网页的网址或者说是链接）的优先队列，由它来决定下一个要抓取的网址是什么，同时去除重复的网址（不做无用功）。用户可以跟据自己的需求定制调度器。

## 下载器

下载器，是所有组件中负担最大的，它用于高速地下载网络上的资源。Scrapy的下载器代码不会太复杂，但效率高，主要的原因是Scrapy下载器是建立在twisted这个高效的异步模型上的(其实整个框架都在建立在这个模型上的)。

## 爬虫

爬虫，是用户最关心的部份。用户定制自己的爬虫，用于从特定的网页中提取自己需要的信息，即所谓的实体(Item)。用户也可以从中提取出链接,让Scrapy继续抓取下一个页面。

## 实体管道

实体管道，用于处理爬虫提取的实体。主要的功能是持久化实体、验证实体的有效性、清除不需要的信息。

## Scrapy引擎

Scrapy引擎是整个框架的核心。它用来控制调试器、下载器、爬虫。实际上，引擎相当于计算机的CPU,它控制着整个流程。

# Scrapy运行流程

![](scrapy/2.png)

- 首先，引擎从调度器中取出一个链接(URL)用于接下来的抓取
- 引擎把URL封装成一个请求(Request)传给下载器，下载器把资源下载下来，并封装成应答包(Response)
- 然后，爬虫解析Response
- 若是解析出实体（Item）,则交给实体管道进行进一步的处理。
- 若是解析出的是链接（URL）,则把URL交给Scheduler等待抓取

# middleware

DOWNLOADER_MIDDLEWARES的使用

settings中放开注释

```python
DOWNLOADER_MIDDLEWARES = {
   'middlePro.middlewares.MiddleproDownloaderMiddleware': 543,
}
```

middlewares.py

```python
# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
import random

class MiddleproDownloaderMiddleware(object):
    # 请求头
    user_agent_list = [
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 "
        "(KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
        "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 "
        "(KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 "
        "(KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 "
        "(KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 "
        "(KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 "
        "(KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 "
        "(KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 "
        "(KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 "
        "(KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 "
        "(KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 "
        "(KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 "
        "(KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 "
        "(KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 "
        "(KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 "
        "(KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 "
        "(KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 "
        "(KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 "
        "(KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"
    ]
    # 代理IP
    PROXY_http = [
        '153.180.102.104:80',
        '195.208.131.189:56055',
    ]
    PROXY_https = [
        '120.83.49.90:9000',
        '95.189.112.214:35508',
    ]
    
   # 拦截所有未发生异常的请求
    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called

        #使用UA池进行请求的UA伪装
        print('this is process_request')
        request.headers['User-Agent'] = random.choice(self.user_agent_list)
        print(request.headers['User-Agent'])
        
        return None
    
    # 拦截所有响应
    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response
    
    # 拦截产生异常的请求
    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        # 使用代理池进行请求代理ip的设置

        if request.url.startswith("https"):
            request.meta['proxy'] = random.choice(self.PROXY_https)
        else:
            request.meta['proxy'] = random.choice(self.PROXY_http)
```

## 以参数形式传递  item

spider

```python
import scrapy
from .. import Item

class _Spider(scrapy.Spider):
    name = 'movie'
    # allowed_domains = ['www.xxx.com']
    start_urls = ['https://www.4567tv.tv/frim/index1.html']
    # 解析详情页中的数据
    def parse_detail(self,response):
        # response.meta返回接收到的meta字典
        item = response.meta['item']
        actor = response.xpath(
            	'/html/body/div[1]/div/div/div/div[2]/p[3]/a/text()').extract_first()
        item['actor'] = actor

        yield item

    def parse(self, response):
        li_list = response.xpath('//li[@class="col-md-6 col-sm-4 col-xs-3"]')
        for li in li_list:
            item = Item()
            name = li.xpath('./div/a/@title').extract_first()
            detail_url = 'https://www.4567tv.tv'+li.xpath('./div/a/@href').extract_first()
            item['name'] = name
            # meta参数:请求传参.meta字典就会传递给回调函数的response参数
            yield scrapy.Request(url=detail_url,callback=self.parse_detail,meta={'item':item})
```

item

```python
import scrapy

class Item(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    actor = scrapy.Field()
```

# Scrapy中selenium的使用

> - 在spider的构造方法中创建一个浏览器对象(作为当前spider的一个属性)
> - 重写spider的一个方法closed(self,spider),在该方法中执行浏览器关闭的操作
> - 在下载中间件的process_response方法中,通过spider参数获取浏览器对象
> - 在中间件的process_response中定制基于浏览器自动化的操作代码(获取动态加载出来的页面源码数据)
> - 实例化一个响应对象,且将page_source返回的页面源码封装到该对象中
> - 返回该新的响应对象

sipder

```python
import scrapy
from selenium import webdriver

class WangyiSpider(scrapy.Spider):
    name = '163.com'
    # allowed_domains = ['www.xxx.com']
    start_urls = ['http://war.163.com/']
    def __init__(self):
        # 创建浏览器对象
        self.bro= webdriver.Chrome(executable_path=
                                   r'C:\Users\Administrator\Desktop\chromedriver.exe')
    def parse(self, response):
        div_list = response.xpath('//div[@class="data_row news_article clearfix "]')
        for div in div_list:
            title = div.xpath('.//div[@class="news_title"]/h3/a/text()').extract_first()
            print(title)
    # 关闭浏览器
    def closed(self,spider):
        print('关闭浏览器对象!')
        self.bro.quit()
```

middleware

```python
from scrapy import signals
from scrapy.http import HtmlResponse
from time import sleep

class WangyiproDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.
        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        # 获取动态加载出来的数据
        bro = spider.bro
        bro.get(url=request.url)
        sleep(3)
        # 包含了动态加载出来的新闻数据
        page_text = bro.page_source
        sleep(3)
        # 返回新实例化的响应对象
        return HtmlResponse(url=spider.bro.current_url,body=page_text,encoding=
                            'utf-8',request=request)
```

# 提高scrapy的效率

不考虑的并发情况下,只需在settings的配置中如下:

```python
增加并发：
    # 默认scrapy开启的并发线程为32个，可以适当进行增加,并发设置成了为100。
    CONCURRENT_REQUESTS = 100

降低日志级别：
    # 在运行scrapy时，会有大量日志信息的输出，为了减少CPU的使用率。可以设置log输出信息为INFO或者ERROR即可。
    LOG_LEVEL = ‘INFO’

禁止cookie：
    # 如果不是真的需要cookie，则在scrapy爬取数据时可以禁止cookie从而减少CPU的使用率，提升爬取效率。	
    COOKIES_ENABLED = False

禁止重试：
    # 对失败的HTTP进行重新请求（重试）会减慢爬取速度，因此可以禁止重试。
    RETRY_ENABLED = False

减少下载超时：
    # 如果对一个非常慢的链接进行爬取，减少下载超时可以能让卡住的链接快速被放弃，从而提升效率。
    DOWNLOAD_TIMEOUT = 10 超时时间为10s
```

# CrawlSpider

CrawlSpider也继承自Spider，所以具备它的所有特性.

参与过网站后台开发的应该会知道，网站的url都是有一定规则的。像django，在view中定义的urls规则就是正则表示的。那么是不是可以根据这个特性来设计爬虫，而不是每次都要用spider分析页面格式，拆解源码。回答是肯定的，scrapy提供了CrawlSpider处理此需求。

CrawlSpider类和Spider类的最大不同是CrawlSpider多了一个rules属性，其作用是定义”提取动作“。在rules中可以包含一个或多个Rule对象，在Rule对象中包含了LinkExtractor对象。

工程建立

```
scrapy startproject projectName
```

创建爬虫文件

```
scrapy genspider -t crawl spiderName www.xxx.com
```

爬虫文件如下

```python
# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule


class ChoutiSpider(CrawlSpider):
    name = 'qiubai'
    # allowed_domains = ['www.xxx.com']
    start_urls = ['起始url']

    # 连接提取器:
    # allow:表示的就是链接提取器提取连接的规则(用正则匹配分页)
    link = LinkExtractor(allow=r'/pic/page/\d+\?s=\d+')
    link1 = LinkExtractor(allow=r'/pic/$')
    rules = (
        # 规则解析器:将链接提取器提取到的连接所对应的页面数据进行指定形式的解析
        Rule(link, callback='parse_item', follow=True),
        # 让连接提取器继续作用到链接提取器提取到的连接所对应的页面中

        Rule(link1, callback='parse_item', follow=True),
    )

    def parse_item(self, response):
        print(response)

```

# 分布式爬虫

只用scrapy框架是没有办法做分布式的,因为,各个程序之间的数据是不能互通的,因此,要实现分布式爬虫,还需要使用`scrapy-redis`插件

spider爬虫文件，使用RedisCrawlSpider类替换之前的Spider类

```python
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy_redis.spiders import RedisCrawlSpider
from redisChoutiPro.items import RedischoutiproItem
class ChoutiSpider(RedisCrawlSpider):
    name = 'chouti'
    # allowed_domains = ['www.xxx.com']
    # start_urls = ['http://www.xxx.com/']
    redis_key = 'chouti'# 调度器队列的名称
    rules = (
        Rule(LinkExtractor(allow=r'/all/hot/recent/\d+'), callback='parse_item', follow=True),
    )

    def parse_item(self, response):
        div_list = response.xpath('//div[@class="item"]')
        for div in div_list:
            title = div.xpath('./div[4]/div[1]/a/text()').extract_first()
            author = div.xpath('./div[4]/div[2]/a[4]/b/text()').extract_first()
            item = RedischoutiproItem()
            item['title'] = title
            item['author'] = author

            yield item
```

settings

```python
ITEM_PIPELINES = {
    'scrapy_redis.pipelines.RedisPipeline': 400
}

# 增加了一个去重容器类的配置, 作用使用Redis的set集合来存储请求的指纹数据, 从而实现请求去重的持久化
DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"
# 使用scrapy-redis组件自己的调度器
SCHEDULER = "scrapy_redis.scheduler.Scheduler"
# 配置调度器是否要持久化, 也就是当爬虫结束了, 要不要清空Redis中请求队列和去重指纹的set。如果是True, 就表示要持久化存储, 就不清空数据, 否则清空数据
SCHEDULER_PERSIST = True  #数据指纹

REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379
```

启动

```python
scrapy runspider 爬虫文件.py # 此时启动要启动.py
```

此时在redis数据库端执行如下命令：

```python
redis-cli
> lpush spider:start_urls 起始url
```

# 增量式爬虫

要实现增量式爬虫,一是在获得页面解析的内容后判断该内容是否已经被爬取过，二是在发送请求之前判断要被请求的url是否已经被爬取过，前一种方法可以感知每个页面的内容是否发生变化，能获取页面新增或者变化的内容，但是由于要对每个url发送请求，所以速度比较慢，而对网站服务器的压力也比较大，后一种无法获得页面变化的内容，但是因为不用对已经爬取过的url发送请求，所以对服务器压力比较小，速度比较快，适用于爬取新增网页

sipder

```python
# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from redis import Redis
from increment1_Pro.items import Increment1ProItem
class MovieSpider(CrawlSpider):
    name = 'movie'
    # allowed_domains = ['www.xxx.com']
    start_urls = ['https://www.4567tv.tv/index.php/vod/show/id/7.html']

    rules = (
        Rule(LinkExtractor(allow=r'/index.php/vod/show/id/7/page/\d+\.html'), callback='parse_item', follow=True),
    )

    def parse_item(self, response):
        conn = Redis(host='127.0.0.1',port=6379)
        detail_url_list = 'https://www.4567tv.tv'+response.xpath('//li[@class="col-md-6 col-sm-4 col-xs-3"]/div/a/@href').extract()
        for url in detail_url_list:
            #ex == 1:set中没有存储url
            ex = conn.sadd('movies_url',url)
            if ex == 1:
                yield scrapy.Request(url=url,callback=self.parse_detail)
            else:
                print('网站没有更新数据,暂无新数据可爬!')

    def parse_detail(self,response):
        item = Increment1ProItem()
        item['name'] = response.xpath('/html/body/div[1]/div/div/div/div[2]/h1/text()').extract_first()
        item['actor'] = response.xpath('/html/body/div[1]/div/div/div/div[2]/p[3]/a/text()').extract_first()

        yield item
```

管道

```python
# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from redis import Redis
class Increment1ProPipeline(object):
    conn = None
    def open_spider(self,spider):
        self.conn = Redis(host='127.0.0.1',port=6379)
    def process_item(self, item, spider):
        dic = {
            'name':item['name'],
            'axtor':item['actor']
        }
        print('有新数据被爬取到')
        self.conn.lpush('movie_data',dic)
        return item

```

