---
title: ansible
date: 2019-02-19 15:16:38
tags: ansible
categories: 
	- ansible
	- Linux
---

ansible是新出现的自动化运维工具，基于Python开发，集合了众多运维工具（puppet、cfengine、chef、func、fabric）的优点，实现了批量系统配置、批量程序部署、批量运行命令等功能。

<!--more-->

ansible是基于模块工作的，本身没有批量部署的能力。真正具有批量部署的是ansible所运行的模块，ansible只是提供一种框架。主要包括：

(1)、连接插件connection plugins：负责和被监控端实现通信；

(2)、host inventory：指定操作的主机，是一个配置文件里面定义监控的主机；

(3)、各种模块核心模块、command模块、自定义模块；

(4)、借助于插件完成记录日志邮件等功能；

(5)、playbook：剧本执行多个任务时，非必需可以让节点一次性运行多个任务。

# 安装

下载epel源

```shell
wget -O /etc/yum.repos.d/epel.repo http://mirrors.aliyun.com/repo/epel-7.repo
```

安装ansible

```shell
yum install -y ansibleshell
```

控制节点需要安装: `salt-master`

被控节点需要安装: `salt-minion`

# 批量在远程主机上执行命令

ansible 是通过ssh来连接并控制被控节点,ssh 的认证方式包括:

- 密码连接

- 秘钥连接

    ```shell
    ssh-keygen # 用来生成ssh的密钥对
    ssh-copy-id 192.168.107.131 # 复制秘钥到远程主机,实现秘钥连接
    ```

## ansible 命令格式

```shell
ansible <host-pattern> [options]
	-a MODULE_ARGS/--args=MODULE_ARGS  # 模块的参数
	-C, --check 					 # 检查
	-f FORKS/--forks=FORKS 		      # 用来做高并发的
	--list-hosts 					 # 列出主机列表
 	-m MODULE_NAME 					 # 模块名称
 	--syntax-check 					 # 语法检查
 	-k 								# 输入密码
```

## ansible hosts

```
cat /etc/ansible/hosts 
```

## host-pattern

```shell
hosts中添加:
[group]
ip1
ip2
# 建立分组
# 系统自带的ping使用的是ICMP协议
- 单个的主机 # ansible 192.168.10.130 -m ping
- 全部主机 # ansible all -m ping/ansible "*" -m ping
- 多个的主机 # ansible 192.168.10.130,192.168.10.131 -m ping
- 单个组 # ansible group1 -m ping
- 多个组
    - 交集  "group1：&group2"
    - 并集
        - group1，group2
        - group1：group2
    - 差集 ‘group1：！group2’
```

## ansible-doc查看模块的帮助信息

```shell
ansible-doc [-l|-F|-s] [options] [-t <plugin type> ] [plugin]
 	-j # 以json的方式返回ansible的所有模块
    -l, --list # 列出所有的ansible的模块
   	-s # 以片段式显示ansible的帮助信息
```

## 命令相关模块

### command

```shell
ansible group -a 'useradd yao' # 通过ansible在group组中的远程主机上执行命令
ansible group -a 'chdir=/tmp pwd'# 切换目录执行命令，使用场景是编译安装时使用
ansible group -a 'creates=/tmp pwd' # 用来判断/tmp目录是否存在，存在就不执行操作,不存在则执行
ansible group -a 'removes=/tmp pwd' # 用来判断tmp目录是否存在，存在就执行操作, 不存在则不执行
# ps:
# command 不支持特殊字符 <> |!;$&
tail -1 /etc/passwd # 查看用户是否创建成功
tail -1 /etc/shadow # 查看用户是否创建成功
id yao  # 查看用户是否创建成功
echo '123' | passwd --stdin yao #设置密码

```

### shell

```shell
ansible group -m shell -a 'echo "123" | passwd --stdin yao' # 批量创建密码
ansible 192.168.10.131 -m shell -a 'bash a.sh' # 执行远程文件方式一
ansible 192.168.10.131 -m shell -a '/root/a.sh' # 执行远程文件方式二，文件必须有执行权限
ansible 192.168.10.131 -m shell -a '/root/a.py' # 执行远端的Python脚本
```

### script

```shell
ansible group -m script -a '/root/m.sh' # 执行本地/管控机上的文件
ansible group -m script -a 'removes=/root/m.sh /root/m.sh' # 用来判断 被 管控机上是不是存在文件，如果存在就执行;不存在就不执行
ansible group -m script -a 'creates=/root/a.sh /root/m.sh' # 用来判断 被 管控机上是不是存在文件，如果存在，就不执行;不存在就执行
```

## 文件相关模块

### copy

> backup  	备份，以时间戳结尾
> dest 	目的地址
> group 	文件的属组
> mode 	文件的权限 r-4; w-2; x-1
> owner 	文件的属主
> src 		源文件

```shell
# 通过md5码来判断是否需要复制
ansible group -m copy -a 'src=/root/m.sh dest=/tmp/a.sh' # 复制本地文件的到远程主机
ansible group -m copy -a 'src=/root/m.sh dest=/tmp/a.sh mode=755' # 修改文件的权限
ansible group -m copy -a 'src=/root/m.sh dest=/tmp/a.sh mode=755 owner=yao' # 修改文件的属主
ansible group -m copy -a 'src=/etc/init.d dest=/tmp/ mode=755 owner=yao' # 复制本地目录到远程主机，如果改变文件的属性，则文件夹内的文件也会被改变
ansible group -m copy -a 'src=/etc/init.d/ dest=/tmp/ mode=755 owner=yao' # 复制本地目录内的所有文件到远程主机
ansible group -m copy -a "content='萍水相逢,尽是他乡之客\n' dest=/tmp/b.txt" # 直接将文本内容注入到远程主机的文件中
```

### file

> inode 	硬盘的地址
> id 		获取到的是内存的地址
> ln -s a.py b.py 		创建软连接
> ln  a.py c.py 		创建硬链接
> 当源文件变化时，软连接和硬链接文件都会跟着变化

```shell
ansible group -m file -a 'path=/yao  state=directory' # 在远程机器上创建文件夹
ansible group -m file -a 'path=/root/q.txt  state=touch' # 用来在远程机器上创建文件
ansible group -m file -a 'path=/tmp/f src=/etc/fstab state=link' # 创建软连接src是源地址，path是目标地址
ansible group -m file -a 'path=/tmp/f state=absent' # 用来删除文件或者文件夹
```

### fetch

> dest 	目的地址
> src 		源地址

```shell
ansible web -m fetch -a 'src=/var/log/cron dest=/tmp' # 下载被控节点的文件，每台机器创建一个文件夹，并保留原来的目录结构
```

