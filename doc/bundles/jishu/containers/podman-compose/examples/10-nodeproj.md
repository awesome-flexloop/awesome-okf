---
type: Example
title: nodeproj：Node.js 开发环境与 extends 继承
description: 官方 nodeproj 示例详解：extends 服务继承、env_file 分层、tmpfs 配合 read_only、UID 传递的 rootless 开发环境、run --rm 一次性初始化工作流
tags: [podman, compose, example, nodejs, extends, env-file, tmpfs, development-workflow]
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

# nodeproj：Node.js 开发环境与 extends 继承

`nodeproj/` 是模式密度最高的官方示例，也是**全仓库唯一使用 `extends` 服务继承**的 compose。它模拟一个真实的 Node.js 容器化开发场景：源码 bind mount 进容器、容器内以当前用户 UID 运行、用一次性容器安装依赖、多个服务共享同一份基础配置。

## 文件构成

```text
nodeproj/
├── docker-compose.yml            # 编排（4 服务：redis/init/task/web）
├── Dockerfile（在 containers/node16-runtime/）
├── package.json / index.js       # Express + redis 应用，nodemon 热重载
├── example.env                   # 项目级 .env 模板（REDIS_HOST=redis）
├── example.local.env             # 服务级 env_file 模板（WEB_LISTEN_PORT、UID 提示）
└── README.md
```

## compose 全文

```yaml
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
    tmpfs:
    - /tmp
    - /var/run
    - /run
  init:
    read_only: true
    #userns_mode: keep-id
    user: ${UID:-1000}
    build:
      context: ./containers/${NODE_IMG:-node16-runtime}
    image: ${NODE_IMG:-node16-runtime}
    env_file:
    - local.env
    volumes:
    - .:/app/code
    command: ["/bin/sh", "-c", "mkdir -p ~/; [ -d ./node_modules ] && echo '** node_modules exists' || npm install"]
    tmpfs:
    - /tmp
    - /run
  task:
    extends:
        service: init
    command: ["npm", "run", "cli", "--", "task"]
    links:
    - redis
    depends_on:
    - redis
  web:
    extends:
        service: init
    command: ["npm", "run", "cli", "--", "web"]
    ports:
    - ${WEB_LISTEN_PORT:-3000}:3000
    depends_on:
    - redis
    links:
    - mongo
```

## 模式逐个拆解

### 1. extends：基服务承载公共配置

`init` 是基服务，`task` 与 `web` 各自继承它：

```yaml
task:
  extends:
    service: init
  command: ["npm", "run", "cli", "--", "task"]
web:
  extends:
    service: init
  command: ["npm", "run", "cli", "--", "web"]
  ports:
    - ${WEB_LISTEN_PORT:-3000}:3000
```

`resolve_extends`（见[配置加载管线](../concepts/06-config-pipeline.md)）以 `rec_merge({}, 基服务, 当前服务)` 合并：当前服务字段覆盖基类。结果是 task/web 自动获得 init 的全部配置——read_only、user、build、image、env_file、bind mount、tmpfs——然后只覆写自己的 command，web 再追加端口。

继承层级上 task/web 也继承了 init 对 redis 的依赖（init 本身不连 redis，但它的配置被复用）；示例显式给 task/web 补了 `links/depends_on: redis`。

> `links: - mongo` 是示例里留的一个"指向未定义服务"的演示性写法（compose 中没有 mongo 服务），实际使用应删除或定义该服务。

### 2. 两层 env：项目 .env 与服务 env_file

README 的启动步骤把两层分得很清楚：

```bash
cp example.local.env local.env   # → 服务级 env_file（被 init 的 env_file: local.env 引用）
cp example.env .env              # → 项目级 .env（podman-compose 自动读取，驱动插值）
echo "UID=$UID" >> .env          # 把当前登录用户 UID 写进项目 .env
```

两个模板的内容：

- `example.env`：`REDIS_HOST=redis`（项目级）
- `example.local.env`：`WEB_LISTEN_PORT=3000` + 注释"pass UID= your IDE user"（服务级，经 env_file 注入容器）

职责区别（见[配置加载管线](../concepts/06-config-pipeline.md)）：

| 层 | 文件 | 读取者 | 用途 |
|----|------|--------|------|
| 项目级 | `.env` | podman-compose | compose 插值变量（`${UID}`、`${WEB_LISTEN_PORT}`）与 COMPOSE_* |
| 服务级 | `local.env`（env_file） | 注入容器进程 | 容器应用的环境变量 |

### 3. UID 传递：rootless 开发环境的关键

```yaml
user: ${UID:-1000}
```

容器内进程以宿主当前用户 UID 运行（`.env` 里 `UID=$UID` 注入）。配合 bind mount 源码卷 `.:/app/code`，容器里 npm 写的 node_modules 文件属主就是宿主用户——不会在 rootless 环境生成 root 属主的垃圾文件。

配套的 Dockerfile（`containers/node16-runtime/Dockerfile`）做了相应准备：

```dockerfile
FROM registry.fedoraproject.org/fedora-minimal:35
RUN microdnf -y install shadow-utils nodejs ... && \
    adduser -d /app app && mkdir -p /app/code/.home && chown app:app -R /app/code
ENV XDG_CONFIG_HOME=/app/code/.home
ENV HOME=/app/code/.home
WORKDIR /app/code
```

把 HOME 指到 bind mount 的代码目录下（.home），使容器内非 root 用户的家目录可写且落在宿主工程目录里。注释掉的 `userns_mode: keep-id` 是更彻底的 rootless ID 映射方案（与默认 pod 冲突时需 `x-podman.in_pod: false`，见[x-podman 扩展](../concepts/08-x-podman-extensions.md)）。

### 4. read_only + tmpfs + bind mount 的写路径设计

init/web/task 都 `read_only: true`，写路径有三个去处：

| 写路径 | 机制 | 目的 |
|--------|------|------|
| `/app/code`（=宿主工程目录） | bind mount `.:/app/code` | 源码与 node_modules 持久化到宿主 |
| `/tmp`、`/run` | tmpfs（内存盘） | npm/nodemon 运行时临时文件，不落盘、随容器消失 |
| `~`（HOME=/app/code/.home） | bind mount 子目录 | 非 root 用户的家目录可写 |

build context 也用了插值：`context: ./containers/${NODE_IMG:-node16-runtime}` + `image: ${NODE_IMG:-node16-runtime}`——切换 Node 版本只需 `NODE_IMG=node18-runtime`（对应准备好的构建目录与镜像标签）。

### 5. 一次性初始化容器

init 服务的 command 是幂等的依赖安装：

```yaml
command: ["/bin/sh", "-c", "mkdir -p ~/; [ -d ./node_modules ] && echo '** node_modules exists' || npm install"]
```

README 工作流：

```bash
podman-compose build
podman-compose run --rm --no-deps init   # 一次性跑 init：装依赖后容器删除
podman-compose up                         # 起常驻服务
```

`run --rm`：命令退出即删除该容器；`--no-deps`：不联动启动依赖服务（init 阶段不需要 redis）。这是"初始化逻辑用一个特殊服务承载，用 run 一次性执行"的标准手法——与 Redis 集群的 creator 角色（[09](09-redis-cluster.md)）、awx17 的 migrate 命令（[11](11-awx-large-app.md)）同构。

### 6. 开发热重载

package.json 中 cli 脚本为 `nodemon -w lib -w index.js ...`：nodemon 监视 bind mount 进来的源码文件，宿主改代码、容器内自动重启——容器只提供运行时，代码在宿主编辑，这是开发环境 compose 的典型形态。

## 排障要点

| 现象 | 原因 | 处理 |
|------|------|------|
| node_modules 文件属主为 root/容器用户 | UID 未传或不匹配 | `.env` 确保 `UID=<宿主uid>`；必要时启用 userns keep-id |
| npm 报无权写 HOME | 家目录不可写（read_only + 未挂载 HOME） | Dockerfile 已把 HOME 设到 /app/code/.home，确保 bind mount 含该目录 |
| `run init` 顺带启动了 redis | 默认会带依赖 | 加 `--no-deps` |
| 切 Node 版本失败 | NODE_IMG 对应的构建目录不存在 | 在 containers/ 下准备对应 runtime 目录 |

## 相关示例与概念

- [hello-python 本地构建](08-hello-python.md)：read_only + 命名卷的基础形态
- [awx 大型应用](11-awx-large-app.md)：`run --rm` 一次性管理命令的另一个实例
- [配置加载管线](../concepts/06-config-pipeline.md)：extends 合并与 env_file/env 分层
- [x-podman 扩展字段全解](../concepts/08-x-podman-extensions.md)：userns keep-id 与 in_pod 冲突处理
