---
type: Example
title: hello-python：本地构建 + 只读根文件系统
description: 官方 hello-python 示例详解：build 与 image 双轨、read_only 安全加固、命名卷持久化、aiohttp+aioredis 计数器应用
tags: [podman, compose, example, python, build, read-only, redis, named-volume]
generated: { by: "source-code-to-okf-wiki", at: "2026-09-12T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-09-12T00:00:00Z" }
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

`requirements.txt` 共 3 行，只声明两个顶层依赖：`aiohttp`（Web 框架）与 `aioredis`（Redis 客户端）；第三行 `# aioredis[hiredis]` 是**注释**——hiredis 是 Redis 的 C 语言解析加速器，取消注释即启用。示例默认走纯 Python 解析器（对计数这种细粒度请求，两者性能差异可忽略）。

`CMD [ "python", "-m", "app.web" ]` 以**模块方式**启动应用：`python -m app.web` 把 `app.web` 当作模块执行，要求 `app/` 是可导入的包——目录下的空 `app/__init__.py` 正是包标记文件。相比直接 `python app/web.py` 跑文件，模块方式保证包上下文完整（`import` 相对解析正确），是 Python 应用容器镜像的惯例写法。

## 应用层代码精读（app/web.py）

`web.py` 共 39 行，按功能分三块：**配置读取 → 应用与路由构建 → 服务入口**。

### 1. 三个可配置环境变量

```python
REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", "6379"))
REDIS_DB = int(os.environ.get("REDIS_DB", "0"))
```

- Redis 连接串由三者拼出：`redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}`；
- compose 的 web 服务只注入了 `REDIS_HOST: redis`（服务名即主机名，与 [azure-vote](06-azure-vote.md) 同一套零配置服务发现），`REDIS_PORT` 与 `REDIS_DB` 使用默认值 6379/0；
- 如需换端口或换库，在 compose 的 `environment:` 中加行覆盖即可，无需改代码。

### 2. 路由声明与统一注册

```python
app = web.Application()
routes = web.RouteTableDef()

@routes.get("/")
async def hello(request):
    counter = await redis.incr("mycounter")
    return web.Response(text=f"counter={counter}")

@routes.get("/hello.json")
async def hello_json(request):
    counter = await redis.incr("mycounter")
    return web.json_response({"counter": counter})

app.add_routes(routes)
```

`RouteTableDef` 是 aiohttp 的**声明式路由表**：先用 `@routes.get(...)` 装饰器收集路由，最后 `app.add_routes(routes)` 一次性注册到 `Application`。两个路由共用同一个计数器键 `mycounter`，对 Redis 执行 `INCR`——每访问一次加一；`/` 返回纯文本 `counter=N`，`/hello.json` 返回 JSON `{"counter": N}`。

### 3. 服务入口与端口

```python
def main() -> None:
    web.run_app(app, port=8080)

if __name__ == "__main__":
    main()
```

- 应用监听端口**硬编码为 8080**，与 compose 的 `ports: [8080:8080]`（容器内 8080）对应——改端口需 compose 与应用两处同步；
- Docker 启动链：`CMD ["python", "-m", "app.web"]` → 模块执行 → `__main__` 分支成立 → `main()` → `web.run_app`。

### 4. Redis 连接是模块级单例

`redis = aioredis.from_url(...)` 在**模块顶层**执行一次，进程内只有一个连接对象被两个路由共享；`aioredis` 2.x 的内部连接池由客户端自动管理，应用无需关心。

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
- `--notify-keyspace-events Ex` 配置键空间与过期事件通知——但应用代码**并未订阅任何频道**（见下节），该参数属模板性配置。

> 对照 nodeproj（[10](10-nodeproj.md)）：Node 服务还需要写 /tmp、/run 这类临时目录，它在 read_only 之外用 tmpfs 承接——read_only + 命名卷/tmpfs 组合是一套完整方案。

### 4. redis 参数与应用的消费情况

redis 服务的 command 带了两个参数，但只有一半被 hello-python 应用真正用到：

- `--appendonly yes`：开启 AOF 持久化，配合命名卷 `/data` 让计数在容器重建后保留——**数据面必需**；
- `--notify-keyspace-events Ex`：发布键空间与过期事件通知——`web.py` 只做 `INCR`，**没有任何 pub/sub 订阅**、没有 `KEYS`/`SCAN` 依赖，该参数是官方示例间的模板性配置，对纯计数器应用实际未消费，删除不影响功能。

> 照抄官方示例时应带"这段配置服务于什么"的问题核对每个参数——[busybox 语法参考卡](07-busybox-syntax.md) 的字段目录视角提供了同样的检查思路。

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

- [官方示例图鉴](03-official-examples-gallery.md)：hello-python 在 12 个示例中的模式定位（build+image 双轨、read_only）
- [nodeproj Node 开发环境](10-nodeproj.md)：read_only + tmpfs + extends 的更复杂组合
- [WordPress 部署示例](01-wordpress.md)：命名卷的入门讲解
- [CLI 翻译层与标签状态](../concepts/05-cli-translation-layer.md)：is_local 与卷挂载参数生成
- [Compose 文件常见模式](../concepts/03-compose-patterns.md)
