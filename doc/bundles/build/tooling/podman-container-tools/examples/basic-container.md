---
type: Example
title: 基础容器操作实战
description: 从零开始掌握Podman基础容器操作，包括镜像拉取、容器运行、日志查看、进入容器、生命周期管理等完整流程。
tags: [podman, 容器, 入门, nginx, 基础操作]
generated: { by: "source-code-to-okf-wiki", at: "2026-08-26T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-26T00:00:00Z" }
status: stable
stale_after: 2027-08-26
sources:
  - id: podman-source
    resource: /references/podman-source.md
    title: Podman Container Tools 源码信源登记
---

## 安装验证与环境检查

在开始操作之前，首先验证Podman是否正确安装并查看系统信息：

```bash
# 验证Podman安装并查看系统信息
podman info

# 查看Podman版本
podman --version
```

`podman info` 会输出存储驱动、Cgroup版本、运行时等详细配置信息，确认环境正常后再进行后续操作。

## 镜像搜索与拉取

使用 `podman search` 搜索镜像，`podman pull` 拉取镜像到本地：

```bash
# 搜索Docker Hub上的nginx镜像
podman search nginx

# 拉取轻量级的alpine版本nginx镜像
podman pull nginx:alpine

# 查看本地已有的镜像列表
podman images
```

推荐使用带明确标签（如 `:alpine`）的镜像，避免使用 `:latest` 带来的版本不确定性。

## 运行第一个容器

使用 `podman run` 启动容器：

```bash
# 后台运行nginx容器，映射8080端口到容器80端口，命名为mynginx
podman run -d --name mynginx -p 8080:80 nginx:alpine
```

参数说明：
- `-d`：后台运行（detached模式）
- `--name mynginx`：为容器指定名称，便于后续操作
- `-p 8080:80`：端口映射，主机8080→容器80
- 最后是镜像名 `nginx:alpine`

## 查看容器状态与日志

容器启动后，查看运行状态和日志输出：

```bash
# 查看正在运行的容器
podman ps

# 查看所有容器（包括已停止的）
podman ps -a

# 查看容器日志
podman logs mynginx

# 实时跟踪日志输出（类似tail -f）
podman logs -f mynginx
```

此时可以通过浏览器访问 `http://localhost:8080` 验证nginx是否正常运行。

## 进入运行中的容器

使用 `podman exec` 在运行的容器内执行命令：

```bash
# 进入容器交互式shell（alpine使用sh，不是bash）
podman exec -it mynginx sh

# 在容器内执行单条命令（不进入交互模式）
podman exec mynginx cat /etc/os-release
podman exec mynginx ls -la /usr/share/nginx/html/
```

参数说明：
- `-i`：保持标准输入打开（interactive）
- `-t`：分配伪终端（tty）

在容器内完成操作后，输入 `exit` 退出shell回到主机。

## 容器生命周期管理

容器的停止、启动、重启操作：

```bash
# 停止运行中的容器
podman stop mynginx

# 启动已停止的容器
podman start mynginx

# 重启容器（相当于stop+start）
podman restart mynginx

# 查看容器详细信息（IP地址、挂载点、环境变量等）
podman inspect mynginx
```

## 删除容器与清理镜像

清理不需要的容器和镜像释放磁盘空间：

```bash
# 先停止容器再删除
podman stop mynginx
podman rm mynginx

# 强制删除运行中的容器（-f会先发送SIGKILL）
podman rm -f mynginx

# 删除本地镜像
podman rmi nginx:alpine

# 一键清理所有停止的容器、未使用的镜像、网络等
podman system prune -a
```

> **注意**：`podman system prune -a` 会清理所有未被运行容器使用的资源，执行前确认没有需要保留的镜像。

## 完整命令序列速查

以下是从零到运行再到清理的完整命令流程：

```bash
# 1. 验证环境
podman info

# 2. 拉取镜像
podman pull nginx:alpine

# 3. 运行容器
podman run -d --name mynginx -p 8080:80 nginx:alpine

# 4. 验证运行
podman ps
curl http://localhost:8080

# 5. 查看日志
podman logs mynginx

# 6. 进入容器调试
podman exec -it mynginx sh

# 7. 停止并清理
podman stop mynginx
podman rm mynginx
podman rmi nginx:alpine
```

## 相关概念

- [容器基础](../concepts/04-container-basics.md)
- [镜像与容器命令](../concepts/07-container-commands.md)
- [Podman CLI结构](../concepts/06-cli-structure.md)
- [入门指南](../concepts/01-getting-started.md)
