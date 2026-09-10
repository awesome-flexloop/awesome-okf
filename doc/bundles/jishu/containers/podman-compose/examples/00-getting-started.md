---
type: Example
title: podman-compose 入门教程（从零到第一个应用）
description: 面向零基础用户的 podman-compose 15 分钟上手指南：安装、单服务起步、数据库+命名卷、端口参数化、常用命令与 5 个新手坑
tags: [podman, compose, tutorial, getting-started, beginner, install, named-volume]
generated: { by: "source-code-to-okf-wiki", at: "2026-09-10T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-09-10T00:00:00Z" }
status: stable
stale_after: "2027-09-10"
sources:
  - id: readme
    resource: /references/readme-source.md
    title: podman-compose 官方 README（安装与依赖）
  - id: examples
    resource: /references/examples-source.md
    title: podman-compose examples/ 目录信源登记
---

# podman-compose 入门教程（从零到第一个应用）

面向零基础用户，约 15 分钟跑通。本教程基于 podman-compose v1.6.0；命令与行为均以源码与官方示例为准。

## 1. 它是什么

podman-compose 是 Docker Compose 的 **Podman 实现**：用一份 `compose.yaml` 描述多个容器（Web、数据库、缓存……）如何组网、用什么镜像、暴露哪些端口、数据存哪里，然后一条 `podman-compose up` 全部拉起。

与 Docker Compose 的根本差异：**没有守护进程**。podman-compose 只是个 Python 脚本，把 YAML 翻译成 `podman` 命令行并调用，进程退出后不残留——安全、轻量、天然支持 rootless（普通用户运行容器）。架构细节见 [daemon-less 架构](../concepts/01-daemonless-arch.md)。

## 2. 前置条件

| 依赖 | 要求 | 检查命令 |
|------|------|---------|
| podman | ≥ 3.4（推荐 5.x） | `podman --version` |
| Python | ≥ 3.9 | `python3 --version` |
| PyYAML、python-dotenv | pip 安装时自动带上 | — |
| DNS 插件 | 旧版 CNI 网络需要 dnsname；netavark 新版自带 | 现代 podman 无需关心 |

Linux 安装 podman：

```bash
# Fedora/RHEL 系
sudo dnf install -y podman
# Debian/Ubuntu
sudo apt install -y podman podman-plugins
```

macOS：`brew install podman-compose`（会带上 podman）。Windows：使用 WSL2 内的 Linux podman。rootless 背景见 [rootless 模式下的网络与卷](../concepts/02-rootless.md)。

## 3. 安装

```bash
pip3 install --user podman-compose
podman-compose --version    # 应显示 1.6.0 或更高
```

也可直接下载单文件脚本放入 PATH，完整安装方式见[官方 README 信源](../references/readme-source.md)。

## 4. 第一个应用（3 分钟）

新建一个空目录，创建 `compose.yaml`：

```yaml
services:
  web:
    image: docker.io/library/nginx:stable
    ports:
      - "8080:80"
```

启动：

```bash
podman-compose up
```

浏览器打开 <http://localhost:8080>，看到 nginx 欢迎页即成功。前台运行时日志直接打印；按 `Ctrl+C` 停止并清理。

后台运行与查看：

```bash
podman-compose up -d        # 后台运行
podman-compose ps           # 查看状态
podman-compose logs -f web  # 跟踪日志
podman-compose down         # 停止并删除容器、网络
```

端口被占用时换一个：把映射改成 `"9090:80"`。同样的最小用例还有官方 [echo/hello-app 逐例详解](04-echo-hello-app.md)。

## 5. 加一个数据库 + 数据持久化

真实应用至少两层。把 `compose.yaml` 改成：

```yaml
volumes:
  db_data:                    # 声明命名卷，数据不随容器删除

services:
  web:
    image: docker.io/library/nginx:stable
    ports:
      - "8080:80"

  db:
    image: docker.io/library/mariadb:10.6
    environment:
      MARIADB_ROOT_PASSWORD: secret
      MARIADB_DATABASE: appdb
    volumes:
      - db_data:/var/lib/mysql
```

三个关键认知：

- **服务名即主机名**：web 容器里直接用主机名 `db` 就能访问数据库，无需配置 IP 或 links——默认网络自动提供 DNS 解析（翻译层会把服务名注册为网络别名）。
- **命名卷持久化**：`db_data` 实际卷名为 `<项目目录名>_db_data`，`down` 后数据保留；`down -v` 才会删除卷。
- **环境变量**两种语法等价：`- KEY=VALUE` 列表或 `KEY: VALUE` 字典。

```bash
podman-compose up -d
podman-compose exec db mariadb -uroot -psecret -e "SHOW DATABASES;"
podman-compose down         # 容器删除，数据仍在；再 up 数据还在
```

完整的 Web+数据库教学示例见 [01-wordpress.md](01-wordpress.md)，双服务标准形态见 [06-azure-vote.md](06-azure-vote.md)。

## 6. 参数化：不把端口写死

```yaml
services:
  web:
    image: docker.io/library/nginx:stable
    ports:
      - "${HOST_PORT:-8080}:80"
```

`${HOST_PORT:-8080}` 表示：环境变量 `HOST_PORT` 有值就用它，否则默认 8080。

```bash
HOST_PORT=9090 podman-compose up -d
# 或写进同目录 .env 文件（项目级，podman-compose 自动读取）：
# echo "HOST_PORT=9090" > .env
```

支持的 bash 风格插值：`${VAR:-默认值}`、`${VAR:?报错信息}`、`${VAR:+替代值}` 等；完整规则见[配置加载管线](../concepts/06-config-pipeline.md)。

## 7. 常用命令速查

| 操作 | 命令 |
|------|------|
| 启动（前台 / 后台） | `podman-compose up` / `podman-compose up -d` |
| 停止并清理容器与网络 | `podman-compose down`（加 `-v` 连卷一起删） |
| 查看运行状态 | `podman-compose ps` |
| 查看日志 | `podman-compose logs -f [服务名]` |
| 在容器里执行命令 | `podman-compose exec web sh` |
| 构建本地镜像 | `podman-compose build` |
| 拉取 / 推送镜像 | `podman-compose pull` / `push` |
| 只校验配置 | `podman-compose config`（输出合并后的完整 YAML） |
| 模拟运行看翻译出的命令 | `podman-compose --dry-run --verbose up` |
| 停止 / 启动 / 重启指定服务 | `podman-compose stop web` / `start` / `restart` |
| 注册为 systemd 用户服务 | `podman-compose systemd -a register` |

完整命令清单见 [快速上手与 Compose Spec 兼容](../concepts/00-introduction.md)。

## 8. 用本地 Dockerfile 构建

目录里放一个 `Dockerfile`，compose 同时写 `build` 和 `image`：

```yaml
services:
  app:
    build:
      context: .
    image: myapp:dev        # 构建产物打的标签
    ports:
      - "8080:8080"
```

```bash
podman-compose up --build -d   # up 前强制重新构建
```

`build` + `image` 双轨的语义（本地镜像默认不参与 pull）见 [hello-python 示例](08-hello-python.md)；不想维护 Dockerfile 时可用 `dockerfile_inline` 内联，见 [05-docker-inline-gpu.md](05-docker-inline-gpu.md)。

## 9. 新手最常踩的 5 个坑

1. **以为 down 会删数据**：`down` 保留命名卷，数据不丢；想彻底清空用 `down -v`。
2. **容器间用 localhost 互连**：错。容器之间要用**服务名**（如 `db:3306`）；容器内的 localhost 指容器自己。
3. **override 文件列表"翻倍"**：多 compose 文件合并时，ports/volumes 等列表默认**追加**而非替换；整体替换用 `!override`，清空用 `!reset`。
4. **depends_on 当成健康保证**：默认只保证容器"已启动"，不保证服务就绪；严格等待用 `depends_on: {condition: service_healthy}`（需 podman ≥ 4.6.0）。
5. **rootless bind mount 权限不对**：开发场景可在服务上设 `user: ${UID:-1000}` 让容器进程以宿主 UID 写挂载目录；进阶手法见 [nodeproj 示例](10-nodeproj.md)。

## 10. 下一步学习路径

| 目标 | 推荐文档 |
|------|---------|
| 理解配置字段写法 | [Compose 文件常见模式](../concepts/03-compose-patterns.md) |
| 掌握更多官方示例 | [示例索引](index.md)：从 echo/hello-app 到 Redis 集群、nodeproj、awx |
| 理解内部原理 | [单文件架构](../concepts/04-source-architecture.md) → [CLI 翻译层](../concepts/05-cli-translation-layer.md) → [配置加载管线](../concepts/06-config-pipeline.md) |
| 需要在 Python 代码里管容器 | [podman-compose 与 podman-py 对比](../concepts/10-compose-vs-podman-py.md) |

## 相关示例

- [WordPress 部署示例](01-wordpress.md)：双服务 + 命名卷完整教学
- [echo 与 hello-app](04-echo-hello-app.md)：单服务最小用例逐行详解
- [azure-vote 前后端](06-azure-vote.md)：服务发现与两种 env 语法
