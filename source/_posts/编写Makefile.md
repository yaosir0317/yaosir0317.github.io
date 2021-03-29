---
title: 编写Makefile
date: 2020-05-30 15:36:03
tags: Linux
categories: Linux
---

# make

`make`是一个构建自动化工具，会在当前目录下寻找`Makefile`或`makefile`文件。如果存在相应的文件，它就会依据其中定义好的规则完成构建任务。

我们可以把`Makefile`简单理解为它定义了一个项目文件的编译规则。借助`Makefile`我们在编译过程中不再需要每次手动输入编译的命令和编译的参数，可以极大简化项目编译过程。同时使用`Makefile`也可以在项目中确定具体的编译规则和流程，很多开源项目中都会定义`Makefile`文件。

本文不会详细介绍`Makefile`的各种规则，只会给出项目中常用的`Makefile`示例。关于`Makefile`的详细内容推荐阅读[Makefile教程](http://c.biancheng.net/view/7097.html)。

<!--more-->

# 规则概述

`Makefile`由多条规则组成，每条规则主要由两个部分组成，分别是依赖的关系和执行的命令。

其结构如下所示：

```makefile
[target] ... : [prerequisites] ...
<tab>[command]
    ...
    ...
```

其中：

- targets：规则的目标
- prerequisites：可选的要生成 targets 需要的文件或者是目标。
- command：make 需要执行的命令（任意的 shell 命令）。可以有多条命令，每一条命令占一行。

举个例子：

```makefile
build:
	CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -o xx
```

## 示例

```makefile
TEST_SERVERS="127.0.0.1" "localhost" 
PROD_SERVERS="127.0.0.1" "localhost" 
SERVICE_NAME="test"

define funcDeploy
	@for server in ${1}; \
    do \
    sh deploy.sh  $${server} ;\
    done;
endef

.PHONY: fmt  # .PHONY是指伪目标并不是真正的文件名
fmt:
	@find . -name "*.go" | xargs goimports -w -l --local $(SERVICE_NAME) 
	
.PHONY: build
build:
	@go build -o .build/${BIN} main.go

.PHONY: lint
lint:
	@golangci-lint -v run ./...

.PHONY: test
test:
	@go test -cover ./...
	
.PHONY: deploy_test
deploy_test:
	$(call funcDeploy, ${TEST_SERVERS})

.PHONY: deploy_prod
deploy_prod:
	$(call funcDeploy, ${PROD_SERVERS})
```

