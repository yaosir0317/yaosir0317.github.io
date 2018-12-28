---
title: Linux环境配置
date: 2018-12-28 11:12:25
tags: Linux
categories: Linux
---

# Linux编译安装

此处以python3.6为例

### 下载python3的源码

> cd /opt
> wget https://www.python.org/ftp/python/3.6.2/Python-3.6.2.tgz
>
> <!---more-->
>
> 安装python3之前，环境依赖解决
> 通过yum安装工具包，自动处理依赖关系，每个软件包通过空格分割
> 提前安装好这些软件包，日后就不会出现很多问题
> yum install gcc patch libffi-devel python-devel  zlib-devel bzip2-devel openssl-devel ncurses-devel sqlite-devel readline-devel tk-devel gdbm-devel db4-devel libpcap-devel xz-devel -y
> ​	

### 解压缩源码包

> 下载好python3源码包之后
> `Python-3.6.2.tgz`
> 解压缩:	tar命令可以解压缩 tgz格式
> ​		`tar -xvf  Python-3.6.2.tgz`

### 切换源码包目录

> cd Python-3.6.2

### 编译且安装

> 1. 释放编译文件makefile，这makefile就是用来编译且安装的
>     ​			`./configure --prefix=/opt/python36/`
>     ​				--prefix  指定软件的安装路径 
>
>   2. 开始编译python3
>      ​		`make`
>
>   3. 编译且安装  (只有在这一步，才会生成/opt/python36)
>      ​		`make install `
>
>   4. 配置python3.6的环境变量
>      ​	1.配置软连接
>      ​	2.配置path环境变量 (二选一即可)
>      ​		echo $PATH查看环境变量
>      ​		`/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/root/bin`
>      		# 这个变量赋值操作，只是临时生效，需要写入到文件，永久生效
>      ​		      PATH=/opt/python36/bin/:usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/root/bin:
>      ​		#linux有一个全局个人配置文件
>      ​		编辑这个文件，在最底行写入PATH
>      ​		vim /etc/profile 
>      ​		写入
>      ​		`PATH=/opt/python36/bin/:usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/root/bin:`
>      ​		保存退出
>      ​		
>
> ​		读一下这个/etc/profile 使得生效
> ​		source /etc/profile

# python的虚拟环境配置

### 安装virtualevn

> 通过物理环境的pip工具安装
> `pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple virtualenv`

### 创建虚拟环境

> `virtualenv --no-site-packages --python=python3   /myenv/venv1`
>
> 调用虚拟环境的命令 
> --no-site-packages  这是构建干净，隔离的模块的参数 
> --python=python3	这个参数是指定虚拟环境以哪一个物理解释器为基础的
> 最后一个是虚拟环境的名字  会创建这么一个文件夹

### 激活虚拟环境

> 找到你的虚拟环境目录bin地下的activate文件
> ​	`source myenv/s15venv1/bin/activate`
> ​	-
> ​	激活虚拟环境，原理就是修改了PATH变量，path是有顺序执行的
> ​	echo $PATH 检查环境变量
> ​	which python3 
> ​	which  pip3  检查虚拟环境是否正常

### 退出虚拟环境

> `deactivate `



# 虚拟环境管理

### 安装

> `pip3 install virtualenvwrapper`

将物理解释器的python，放在path最前面

> `echo $PATH`
> `/opt/python36/bin`:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/root/bin:/root/bin

### 修改环境变量

每次开机就加载这个virtualenvwrapper工具

> `vim ~/.bashrc`   #vim编辑用户家目录下的.bashrc文件，这个文件是用户在登录的时候，就读取这个文件
> `export WORKON_HOME=~/Envs`   #设置virtualenv的统一管理目录
>
> ​	# export 是读取shell命令的作用
>
> 	# 这些变量根据你自己的绝对路径环境修改	
>
> `export VIRTUALENVWRAPPER_VIRTUALENV_ARGS='--no-site-packages' `  #添加virtualenvwrapper的参数，生成干净隔绝的环境
> `export VIRTUALENVWRAPPER_PYTHON=/opt/python36/bin/python3`     #指定python解释器
> `source /opt/python36/bin/virtualenvwrapper.sh `     #执行virtualenvwrapper安装脚本 

### 重新登录会话，使得这个配置生效

> `mkvirtualenv  虚拟环境名`   #自动下载虚拟环境，且激活虚拟环境
>
> `workon  虚拟环境名`   #激活虚拟环境
>
> `deactivate` 退出虚拟环境 
>
> `rmvirtualenv`	删除虚拟环境 
>
> `cdvirtualenv`  进入当前已激活的虚拟环境所在的目录
>
> `cdsitepackages` 进入当前激活的虚拟环境的，python包的目录

# 环境一致

通过命令保证环境的一致性

> 导出当前python环境的包
> `pip3 freeze > requirements.txt   `

在服务器下创建virtualenv，在venv中导入项目所需的模块依赖

> `pip3 install -r requirements.txt`

# 提示yum进程被锁定，无法使用 问题

> 解决办法： ps -ef|grep yum 进程，这是说 有另一个进程也在用yum
> yum只能有一个进程使用 