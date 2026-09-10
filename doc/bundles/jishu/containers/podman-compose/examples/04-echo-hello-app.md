---
type: Example
title: echo 与 hello-app：单服务最小用例
description: 官方 echo/hello-app 两个最小示例的逐行详解：端口参数化、单文件 compose、curl 回显验证
tags: [podman, compose, example, echo, hello-app, minimal, single-service]
generated: { by: "source-code-to-okf-wiki", at: "2026-09-10T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-09-10T00:00:00Z" }
status: stable
stale_after: "2027-09-10"
sources:
  - id: examples
    resource: /references/examples-source.md
    title: podman-compose examples/ 目录信源登记
---

# echo 与 hello-app：单服务最小用例

`echo/` 与 `hello-app/` 是官方示例的"第零级"：一个服务、一个镜像、一个端口映射，无卷、无网络、无依赖。适合验证 podman-compose 安装是否可用、理解最小编排单元的完整生命周期。

## 示例一：hello-app（约 2MB 的最小 Web 服务）

目录：`examples/hello-app/`，compose 全文只有 7 行：

```yaml
---
version: '3'
services:
  web:
    image: gcr.io/google-samples/hello-app:1.0
    ports:
        - "${HOST_PORT:-8080}:8080"
```

逐行解读：

| 行 | 含义 |
|----|------|
| `image: gcr.io/google-samples/hello-app:1.0` | 谷歌示例镜像，体积约 2MB，内置一个监听 8080 的 HTTP 服务 |
| `ports: "${HOST_PORT:-8080}:8080"` | 宿主 `${HOST_PORT:-8080}` → 容器 8080；冒号右侧是容器内固定端口，左侧是宿主可配置端口 |

运行与验证（README 原始步骤）：

```bash
cd examples/hello-app
podman-compose up
# 另开终端或浏览器：
# 打开 http://localhost:8080/
# 看到 "Hello, world!" 与版本/实例信息即成功
```

### 端口参数化的三种用法

`${HOST_PORT:-8080}` 是 bash 风格插值（实现见[配置加载管线](../concepts/06-config-pipeline.md)），三种等价写法：

```bash
podman-compose up                          # 默认宿主 8080
HOST_PORT=9090 podman-compose up           # 本次调用换 9090
echo "HOST_PORT=9090" > .env && podman-compose up   # 写入项目 .env 持久化
```

> 为什么示例统一用这个变量名而非硬编码端口？官方 12 个示例中有 4 个（echo/hello-app/hello-app-redis/azure-vote）共享完全相同的 `${HOST_PORT:-8080}:8080` 写法，使同一台主机上可以同时跑多个示例而不端口冲突。

## 示例二：echo（回显服务，验证请求细节）

目录：`examples/echo/`，compose 与 hello-app 同构：

```yaml
---
version: '3'
services:
  web:
    image: k8s.gcr.io/echoserver:1.4
    ports:
        - "${HOST_PORT:-8080}:8080"
```

echoserver 不返回固定页面，而是把收到的请求**原样回显**（客户端地址、请求行、全部请求头、请求体）。这让它成为调试容器网络与端口映射的探针：

```bash
podman-compose up
# 另一个终端：
curl -X POST -d "foobar" http://localhost:8080/; echo
```

README 记录的典型输出：

```text
CLIENT VALUES:
client_address=10.89.31.2
command=POST
real path=/
request_version=HTTP/1.1
request_uri=http://localhost:8080/

SERVER VALUES:
server_version=nginx: 1.10.0 - lua: 10001

HEADERS RECEIVED:
accept=*/*
content-length=6
content-type=application/x-www-form-urlencoded
host=localhost:8080
user-agent=curl/7.76.1
BODY:
foobar
```

排障用途：

- **验证端口映射**：能收到响应即宿主→容器端口链路正常；
- **验证服务间调用**：在另一个容器内 `curl web:8080`，回显中的 `client_address` 会显示调用方容器 IP，可确认容器网络连通；
- **验证请求头透传**：代理/网关链路加了什么头，回显一目了然。

## 最小用例的完整生命周期

这两个示例隐含了 podman-compose 管理单服务的全部步骤（对应源码 `compose_up`，见[依赖图与 up/down 生命周期](../concepts/07-dependency-lifecycle.md)）：

```text
podman-compose up
  ├─ 解析 compose（插值 HOST_PORT）
  ├─ 探测镜像缺失 → podman pull（policy=missing）
  ├─ 创建默认网络 <项目>_default（服务隐式接入）
  ├─ podman create <名> --network ... -p 8080:8080 ...
  └─ podman start -a <名>（前台模式聚合日志，Ctrl+C 退出）
podman-compose down
  ├─ podman stop <名>（默认 10 秒宽限）
  ├─ podman rm <名>
  └─ podman network rm <网络名>
```

要点：即使 compose 里一个字都没写网络，服务也会被接入自动创建的默认网络；down 时该网络随项目清理。容器名默认为 `<项目>_web_1`，可用 `podman ps` 直接看到。

## 常见问题

| 现象 | 原因 | 处理 |
|------|------|------|
| `bind: address already in use` | 宿主 8080 已被占用 | `HOST_PORT=9090 podman-compose up` |
| 前台运行想后台 | 默认 attach 到日志 | 加 `-d`：`podman-compose up -d`，用 `podman-compose logs -f` 看日志 |
| 镜像拉取慢 | gcr.io 网络问题 | 配置镜像加速或替换为可访问的同名镜像 |
| Ctrl+C 后容器残留 | attach 模式清理依赖信号处理 | `podman-compose down` 显式清理（Windows 平台 SIGINT 不注册，更需要手动 down） |

## 相关示例与概念

- [官方示例图鉴](03-official-examples-gallery.md)：12 个示例的模式速查
- [azure-vote 前后端示例](06-azure-vote.md)：最小双服务，从单服务跨出的下一步
- [配置加载管线](../concepts/06-config-pipeline.md)：`${HOST_PORT:-8080}` 插值实现
- [快速上手与 Compose Spec 兼容](../concepts/00-introduction.md)：up/down 命令参考
