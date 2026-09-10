---
type: Example
title: hello-python：本地构建 + 只读根文件系统
description: 官方 hello-python 示例详解：build 与 image 双轨、read_only 安全加固、命名卷持久化、aiohttp+aioredis 计数器应用
tags: [podman, compose, example, python, build, read-only, redis, named-volume]
generated: { by: "source-code-to-okf-wiki", at: "2026-09-10T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-09-10T00:00:00Z" }
status: stable
stale_after: "2027-09-10"
sources:
  - id: examples
    resource: /references/examples-source.md
    title: podman-compose examples/ 目录信源登记
  - id: source-code
    resource: /references/source-code-map.md
    title: podman_compose.py 源码信源登记（v1.6.0 / commit e3df104）
---

# hello-python：本地构建 + 只读根文件系统

`hello-python/` 是一个自带应用代码的完整示例：aiohttp Web 服务 + Redis 计数器，镜像由本地 Dockerfile 构建。它演示了生产式 compose 的三个关键实践：**build/image 双轨**、**read_only 根文件系统**、**命名卷承接写路径**。

## 文件构成

```text
hello-python/
├── docker-compose.yaml    # 编排文件
├── Dockerfile             # 镜像构建定义
├── requirements.txt       # Python 依赖（aiohttp、aioredis）
├── README.md
└── app/
    ├── __init__.py
    └── web.py             # 应用代码：aiohttp + aioredis 计数器
```

## compose 全文

```yaml
---
version: '3'
volumes:
  redis:
services:
  redis:
    read_only: true
    image: docker.io/redis:alpine
    command: ["redis-server", "--appendonly", "yes", "--notify-keyspace-events", "Ex"]
    volumes:
    - redis:/data
  web:
    read_only: true
    build:
      context: .
    image: hello-py-aioweb
    ports:
    - 8080:8080
    environment:
      REDIS_HOST: redis
```

## Dockerfile

```dockerfile
FROM python:3.9-alpine
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD [ "python", "-m", "app.web" ]
EXPOSE 8080
```

标准分层：先 COPY requirements 再装依赖（利用构建缓存，依赖不变时不重装），最后 COPY 应用代码。

## 应用代码如何使用 Redis

`app/web.py` 的核心逻辑：

```python
REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
# ...
redis = aioredis.from_url(f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}")

@routes.get("/")
async def hello(request):
    counter = await redis.incr("mycounter")
    return web.Response(text=f"counter={counter}")

@routes.get("/hello.json")
async def hello_json(request):
    counter = await redis.incr("mycounter")
    return web.json_response({"counter": counter})
```

两个路由都对 Redis 的 `mycounter` 键执行 `INCR`：每访问一次计数器加一。连接地址来自 `REDIS_HOST` 环境变量——compose 里注入的是服务名 `redis`，与 azure-vote（见[06](06-azure-vote.md)）同一套零配置服务发现。

## 三个关键实践

### 1. build 与 image 双轨

web 服务同时写了 `build.context: .` 和 `image: hello-py-aioweb`：

```yaml
web:
  build:
    context: .
  image: hello-py-aioweb
```

语义（对应源码 `is_local()` 与 build/pull 调度，见[依赖图与 up/down 生命周期](../concepts/07-dependency-lifecycle.md)）：

- 从本地 Dockerfile 构建，构建产物打成 `hello-py-aioweb` 标签；
- 镜像名不含 `/` 且服务有 build 段 → `is_local()` 判定为**本地镜像**，默认不参与 `podman pull`（避免去远程仓库找一个只存在于本地的名字）；
- 同时声明 build 和 image 时，拉取失败会被忽略（pull 后 build 兜底）。

### 2. read_only：只读根文件系统

两个服务都设了 `read_only: true`：容器根文件系统挂载为只读，任何写根分区的操作都会失败。这是最小权限原则的容器化实践——应用被攻破后无法往系统目录写 webshell 或篡改二进制。

但只读不等于不需要写：

### 3. 用命名卷显式承接写路径

Redis 需要持久化数据到 `/data`：

```yaml
volumes:
  redis:
services:
  redis:
    read_only: true
    volumes:
      - redis:/data       # 唯一可写路径：命名卷
```

- 顶层 `volumes.redis` 声明命名卷，实际卷名为 `<项目>_redis`，首次使用自动 `podman volume create`；
- redis 的 `--appendonly yes` 开启 AOF 持久化，数据写入卷挂载的 /data，容器删除后数据保留；
- `--notify-keyspace-events Ex` 配置键空间通知（键过期事件），是应用需要的 Redis 功能开关。

> 对照 nodeproj（[10](10-nodeproj.md)）：Node 服务还需要写 /tmp、/run 这类临时目录，它在 read_only 之外用 tmpfs 承接——read_only + 命名卷/tmpfs 组合是一套完整方案。

## 运行（README 原始步骤）

```bash
cd examples/hello-python
podman-compose up -d
curl localhost:8080/             # counter=1
curl localhost:8080/             # counter=2
curl localhost:8080/hello.json   # {"counter":3}
```

完整生命周期：

```bash
podman-compose build    # 单独构建（可选，up 会自动构建）
podman-compose up -d    # 构建（若缺）+ 起 redis + 起 web
curl localhost:8080/    # 计数递增，验证 web→redis 连通
podman-compose down     # 停止删除容器与网络；卷 <项目>_redis 保留
podman-compose down -v  # 连同卷一起清理（计数归零）
```

## 排障要点

| 现象 | 原因 | 处理 |
|------|------|------|
| web 启动报连不上 redis | redis 未就绪 | redis 镜像启动很快；需要严格保证可加 depends_on + healthcheck |
| read_only 下应用写文件报错 | 应用往工作目录写缓存 | 写路径改挂卷或 tmpfs（参考 nodeproj 的 tmpfs 写法） |
| up 后计数从旧值继续 | 命名卷数据保留 | `down -v` 或 `podman volume rm <项目>_redis` |
| 构建慢 | pip 走公网 | 配置 pip 镜像源或在 Dockerfile 加内部 wheel 源 |

## 相关示例与概念

- [nodeproj Node 开发环境](10-nodeproj.md)：read_only + tmpfs + extends 的更复杂组合
- [WordPress 部署示例](01-wordpress.md)：命名卷的入门讲解
- [CLI 翻译层与标签状态](../concepts/05-cli-translation-layer.md)：is_local 与卷挂载参数生成
- [Compose 文件常见模式](../concepts/03-compose-patterns.md)
