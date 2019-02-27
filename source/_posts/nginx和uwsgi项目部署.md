---
title: nginx+uwsgi
date: 2019-01-07 19:49:05
tags:
	- nginx
	- uwsgi
	- Vue
	- Django
	- Linux
categories: Linux
---

# 部署准备

- uwsgi    wsgi(web服务网关接口，就是一个实现了python web应用的协议)
- virtualenvwrapper
- 后端项目代码
- 前端项目代码
- nginx (一个是nginx对静态文件处理的优秀性能，一个是nginx的反向代理功能，以及nginx的默认80端口，访问nginx的80端口，就能反向代理到应用的8000端口)
- mysql 
- redis   
- supervisor 进程管理工具 

<!--more-->

**将linux进程运行在后台的方法**

> 第一个，命令后面加上 &  符号
> `python  manage.py  runserver & `
> 第二个 使用`nohup`命令
> 第三个使用进程管理工具

# 项目部署

## 新建一个虚拟环境

`mkvirtualenv`

## 准备前后端代码

> 下载代码
>
> 解压代码

## 前端项目部署

- 准备node打包环境

    `wget https://nodejs.org/download/release/v8.6.0/node-v8.6.0-linux-x64.tar.gz`

- 解压缩node包，配置环境变量，使用npm和node命令
- 检测node和npm
    ​	`node -v `
    ​	`npm  -v `

- 安装vue项目所需的包

    `npm install  `

- 生成静态文件

    `npm run build  `

## 后端项目部署

- 激活虚拟环境

    `workon env `

- 安装所有的软件包

    `pip3 install -r  requirements.txt `

## uwsgi部署

- 安装uwsgi 

    `pip3 install -i https://pypi.douban.com/simple uwsgi`

- 配置uwsgi.ini

    > touch uwsgi.ini 
    > ​					
    >
    > [uwsgi]
    > #Django-related settings
    > #the base directory (full path)
    > #指定项目的绝对路径的第一层路径,例如Django项目manage.py的上层
    > chdir           = /opt/项目/
    >
    > #Django's wsgi file
    > #指定项目的 wsgi.py文件
    > #写入相对路径即可，这个参数是以  chdir参数为相对路径
    > module          = 项目.wsgi
    >
    > #the virtualenv (full path)
    > #写入虚拟环境解释器的 绝对路径
    > home            = /root/Envs/onepiece
    >
    > #process-related settings
    >
    > #master
    >
    > master          = true
    >
    > #maximum number of worker processes
    >
    > #指定uwsgi启动的进程个数				
    > processes       = 1
    >
    >
    > #这个参数及其重要！！！！！！
    > #the socket (use the full path to be safe)
    > #socket指的是，uwsgi启动一个socket连接，当你使用nginx+uwsgi的时候，使用socket参数
    > socket          = 0.0.0.0:9000
    >
    >
    > #这个参数是uwsgi启动一个http连接，当你不用nginx只用uwsgi的时候，使用这个参数
    > #http  =  0.0.0.0:9000
    >
    > #... with appropriate permissions - may be needed
    > #chmod-socket    = 664
    > #clear environment on exit
    > vacuum          = true

- 使用uwsgi配置文件启动项目

    `uwsgi --ini  uwsgi.ini `

- tips

    > 通过uwsgi启动一个python web文件
    > ​	uwsgi --http :8000 --wsgi-file   testuwsgi.py
    > ​					--http 指定http协议 
    > ​					--wsgi-file  指定一个python文件
    > ​			
    >
    > 通过uwsgi启动django项目，并且支持热加载项目，不重启项目，自动生效 新的 后端代码
    > ​		
    > ​	uwsgi --http  :8000 --module testdrf.wsgi    --py-autoreload=1
    > ​	
    > ​				      --module 指定找到django项目的wsgi.py文件

## supervisor进程管理

- 安装supervisor

    使用python2的包管理工具 easy_install ，注意，此时要退出虚拟环境！

    如果没有命令，使用以下命令，安装
    `yum install python-setuptools
    easy_install supervisor`

- 生成配置文件

    这个文件就是写入你要管理的进程任务
    `echo_supervisord_conf > /etc/supervisor.conf`

- 编辑配置文件

    > vim /etc/supervisor.conf  
    > 直接到最底行，写入以下配置
    > [program:项目名称]
    > command=/root/Envs/onepiece/bin/uwsgi  - -ini  /opt/uwsgi.ini
    >
    > command=uwsgi绝对路径 - -ini uwsgi.ini的绝对路径

- 启动

    启动supervisord服务端，指定配置文件启动
    `supervisord -c  /etc/supervisor.conf`

- 管理

    通过supervisorctl管理任务
    `supervisorctl -c /etc/supervisor.conf `

    >  start 项目
    >
    >  restart 项目
    >
    >  stop 项目

## nginx部署

配置`nginx.conf`

> #第一个server虚拟主机是为了找到前端的dist文件， 找到index.html
> server {
> ​        listen       80;
> ​        server_name  192.168.13.79;	
>
> ​	#当请求来自于 192.168.13.79/的时候，直接进入以下location，然后找到前端项目的dist/index.html 
> ​        location / {
> ​       		 root   /opt/dist;
>
> ​       		 index  index.html;
>    	 }
> ​	
> }
>
> #由于vue发送的接口数据地址是 192.168.13.79:8000  我们还得再准备一个入口server
> server {
> ​	listen 8000;
> ​	server_name  192.168.13.79;
>
> ​	#当接收到接口数据时，请求url是 192.168.13.79:8000 就进入如下location
> ​	location /  {
> ​		#这里是nginx将请求转发给  uwsgi启动的 9000端口
> ​		uwsgi_pass  192.168.13.79:9000;
>
> ​	include  就是一个“引入的作用”，就是将外部一个文件的参数，导入到当前的nginx.conf中生效
>
> ​		include /opt/nginx/conf/uwsgi_params;
> ​	}
>
> }