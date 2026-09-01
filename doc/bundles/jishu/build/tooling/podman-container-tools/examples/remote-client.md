---
type: Example
title: 远程连接与REST API实战
description: 配置Podman远程客户端，通过SSH/TCP连接远程Podman服务，使用REST API和Docker兼容API进行容器管理。
tags: [podman, remote, api, rest, ssh, docker-compatible, bindings]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-26T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-26T00:00:00Z" }
status: stable
stale_after: 2027-08-26
sources:
  - id: podman-source
    resource: /references/podman-source.md
    title: Podman Container Tools 源码信源登记
---

## 在远程服务器启动Podman服务

首先在远程服务器上启动Podman API服务，监听TCP端口：

```bash
# 在远程服务器上执行：启动Podman系统服务，监听所有网卡的8888端口
# --time=0 表示不超时
podman system service --time=0 tcp://0.0.0.0:8888 &

# 如果使用rootless模式，Podman默认socket位于用户运行时目录
# 查看socket路径
echo $XDG_RUNTIME_DIR/podman/podman.sock

# rootless模式也可以直接用systemd激活socket
systemctl --user enable --now podman.socket
```bash

> **安全提示**：生产环境建议使用SSH方式连接而非暴露TCP端口，避免未授权访问。TCP方式仅适用于可信内网环境。

如果使用SSH方式，无需手动启动服务——Podman客户端会通过SSH自动转发socket。

## 本地添加远程连接

在本地机器配置远程Podman连接：

```bash
# 方式一：通过SSH连接（推荐，安全）
# 将 user@remote 替换为实际的用户名和远程主机地址
# UID替换为远程服务器上用户的UID（可通过 id -u 在远程服务器查看）
podman system connection add myserver ssh://user@remote:22/run/user/1000/podman/podman.sock

# 方式二：直接TCP连接（仅内网测试）
podman system connection add myserver tcp://remote:8888

# 查看所有已配置的连接
podman system connection list
```text

输出示例：
```text
Name        Identity  URI
myserver*             ssh://user@remote:22/run/user/1000/podman/podman.sock
```bash

带 `*` 标记的是当前默认连接。

## 切换默认连接与验证

设置默认连接并验证远程操作：

```bash
# 将myserver设为默认连接
podman system connection default myserver

# 查看当前默认连接
podman system connection list

# 验证远程连接：查看远程Podman信息
podman info

# 也可以使用 -c 参数指定连接，不切换默认
podman -c myserver info
podman -c myserver images
podman -c myserver ps
```bash

此时所有不带 `-c` 参数的 `podman` 命令都会在远程服务器执行。

## 使用curl调用Podman原生REST API

Podman提供RESTful API，可以直接通过HTTP调用：

```bash
# 获取Podman系统信息（libpod API，Podman原生接口）
curl http://remote:8888/v5.0.0/libpod/info

# 列出所有容器
curl http://remote:8888/v5.0.0/libpod/containers/json

# 列出所有镜像
curl http://remote:8888/v5.0.0/libpod/images/json

# 拉取镜像
curl -X POST http://remote:8888/v5.0.0/libpod/images/pull?reference=nginx:alpine

# 创建并启动容器（简化示例）
curl -X POST http://remote:8888/v5.0.0/libpod/containers/create \
  -H "Content-Type: application/json" \
  -d '{"image":"nginx:alpine","name":"remote-nginx","portmappings":[{"container_port":80,"host_port":8080}]}'
```bash

API路径中的 `v5.0.0` 是API版本，可通过 `podman info` 查看支持的版本。

## 使用Docker兼容API

Podman兼容Docker Engine API，大部分Docker客户端工具可以直接使用：

```bash
# Docker兼容API：列出容器
curl http://remote:8888/v1.41/containers/json

# Docker兼容API：列出镜像
curl http://remote:8888/v1.41/images/json

# Docker兼容API：创建容器
curl -X POST http://remote:8888/v1.41/containers/create \
  -H "Content-Type: application/json" \
  -d '{"Image":"nginx:alpine","HostConfig":{"PortBindings":{"80/tcp":[{"HostPort":"8080"}]}}}'

# 也可以直接设置DOCKER_HOST让docker命令使用Podman服务
export DOCKER_HOST=tcp://remote:8888
docker ps
docker images
```bash

`v1.41` 是Docker API版本，对应Docker 20.10+。通过设置 `DOCKER_HOST` 环境变量，`docker` CLI可以无缝操作Podman。

## Go Bindings使用简介

Podman提供官方Go语言绑定库，可以在Go程序中直接操作Podman：

```go
package main

import (
	"context"
	"fmt"
	"log"

	"github.com/containers/podman/v5/pkg/bindings"
	"github.com/containers/podman/v5/pkg/bindings/containers"
	"github.com/containers/podman/v5/pkg/bindings/images"
)

func main() {
	// 连接到Podman服务
	ctx := context.Background()
	
	// 方式一：连接本地socket
	// connText, err := bindings.NewConnection(ctx, "unix:///run/podman/podman.sock")
	
	// 方式二：连接远程SSH
	connText, err := bindings.NewConnection(ctx, "ssh://user@remote:22/run/user/1000/podman/podman.sock")
	
	// 方式三：连接TCP
	// connText, err := bindings.NewConnection(ctx, "tcp://remote:8888")
	
	if err != nil {
		log.Fatal(err)
	}

	// 列出容器
	containerList, err := containers.List(connText, new(containers.ListOptions))
	if err != nil {
		log.Fatal(err)
	}
	for _, c := range containerList {
		fmt.Printf("容器: %s (ID: %.12s) 状态: %s\n", c.Names[0], c.ID, c.State)
	}

	// 拉取镜像
	_, err = images.Pull(connText, "nginx:alpine", new(images.PullOptions))
	if err != nil {
		log.Fatal(err)
	}

	fmt.Println("操作完成")
}
```text

初始化Go模块并安装依赖：

```bash
# 初始化模块
go mod init podman-demo

# 获取Podman bindings依赖
go get github.com/containers/podman/v5/pkg/bindings

# 编译运行
go run main.go
```bash

除了Go，Podman社区也提供Python、JavaScript等其他语言的客户端库。

## 连接管理常用命令

```bash
# 查看所有连接
podman system connection list

# 重命名连接
podman system connection rename myserver production

# 删除连接
podman system connection remove myserver

# 测试连接是否可用
podman -c myserver info

# 查看远程磁盘使用情况
podman -c myserver system df
```bash

## 完整配置流程速查

```bash
# === 远程服务器操作 ===
# 启动socket（rootless推荐方式）
ssh user@remote "systemctl --user enable --now podman.socket"

# 获取远程用户UID
REMOTE_UID=$(ssh user@remote "id -u")

# === 本地机器操作 ===
# 添加SSH连接
podman system connection add myserver ssh://user@remote:22/run/user/$REMOTE_UID/podman/podman.sock

# 设为默认
podman system connection default myserver

# 验证
podman info
podman run -d --name remote-nginx -p 8080:80 nginx:alpine
podman ps
curl http://localhost:8080

# 使用Docker兼容API
curl http://remote:8888/v1.41/containers/json
```bash

## 相关概念

- [远程API](../concepts/11-remote-api.md)
- [架构概述](../concepts/02-architecture-overview.md)
- [CLI结构](../concepts/06-cli-structure.md)
- [生态系统](../concepts/14-ecosystem.md)
