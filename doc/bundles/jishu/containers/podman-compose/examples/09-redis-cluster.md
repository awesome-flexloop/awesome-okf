---
type: Example
title: hello-app-redis：6 节点 Redis 集群
description: 官方 hello-app-redis 示例详解：5 数据节点 + 1 集群创建者的 Bitnami Redis 集群拓扑、REDIS_NODES 成员发现、两层 depends_on 启动顺序
tags: [podman, compose, example, redis, cluster, bitnami, depends-on, multi-container]
generated: { by: "source-code-to-okf-wiki", at: "2026-09-10T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-09-10T00:00:00Z" }
status: stable
stale_after: "2027-09-10"
sources:
  - id: examples
    resource: /references/examples-source.md
    title: podman-compose examples/ 目录信源登记
---

# hello-app-redis：6 节点 Redis 集群

`hello-app-redis/` 是规模最大的官方示例：一个 Web 计数器 + **6 节点 Bitnami Redis Cluster**（5 个数据节点 + 1 个集群创建者）。它演示了如何用 podman-compose 表达有明确启动拓扑的中等规模服务集群。

> 本束 [02-multi-container.md](02-multi-container.md) 是同一架构的教学化讲解（自建 Redis 配置、自定义网络、健康检查）；本文聚焦**官方原始示例**的配置手法。

## 架构拓扑

```text
                    浏览器
                      │ :8080
                 ┌────┴────┐
                 │   web   │  hello-app-redis:1.0（计数器）
                 └────┬────┘
                      │ depends_on
                 ┌────┴────────────┐
                 │ redis-cluster   │  REDIS_CLUSTER_CREATOR=yes（初始化者）
                 └────┬────────────┘
                      │ depends_on（5 个节点先就绪）
     ┌────────┬───────┼───────┬────────┐
 redis-node1 node2   node3   node4   node5   （bitnami/redis-cluster:6.2）
```

共 **7 个服务**：web、redis-node1-5、redis-cluster。每个 redis 节点有独立命名卷。

## compose 结构拆解

### 顶层：6 个命名卷

```yaml
volumes:
  redis-node1-data:
  redis-node2-data:
  redis-node3-data:
  redis-node4-data:
  redis-node5-data:
  redis-data:          # 给 creator 节点
```

### web 服务

```yaml
web:
  image: gcr.io/google-samples/hello-app-redis:1.0
  depends_on:
    - redis-cluster
  ports:
      - "${HOST_PORT:-8080}:8080"
```

- 列表式 `depends_on`（默认条件 `service_started`）：web 在 redis-cluster 容器启动后启动；
- 镜像内置 Redis 集群客户端，默认连接 `<服务名>:6379` 的集群。

### 5 个数据节点（同构）

以 node1 为例（node2-5 仅名字与卷不同）：

```yaml
redis-node1:
  image: docker.io/bitnami/redis-cluster:6.2
  volumes:
    - redis-node1-data:/bitnami/redis/data
  environment:
    - ALLOW_EMPTY_PASSWORD=yes
    - REDIS_NODES=redis-node1 redis-node2 redis-node3 redis-node4 redis-node5 redis-cluster
```

两个环境变量：

- `ALLOW_EMPTY_PASSWORD=yes`：Bitnami 镜像约定，演示环境允许空密码；
- `REDIS_NODES=<空格分隔的全部服务名>`：Bitnami 集群发现机制——每个节点都知道全部成员的主机名。这里**直接利用 podman-compose 的服务名 DNS**：`redis-node2` 等名字在默认网络中可解析（见[CLI 翻译层](../concepts/05-cli-translation-layer.md)的 alias 生成）。

每个节点挂载独立卷到 Bitnami 的数据目录 `/bitnami/redis/data`，节点身份与数据各自持久化。

### 集群创建者

```yaml
redis-cluster:
  image: docker.io/bitnami/redis-cluster:6.2
  volumes:
    - redis-data:/bitnami/redis/data
  depends_on:
    - redis-node1
    - redis-node2
    - redis-node3
    - redis-node4
    - redis-node5
  environment:
    - ALLOW_EMPTY_PASSWORD=yes
    - REDIS_NODES=redis-node1 redis-node2 redis-node3 redis-node4 redis-node5 redis-cluster
    - REDIS_CLUSTER_CREATOR=yes
```

关键差异：多了 `REDIS_CLUSTER_CREATOR=yes`。Bitnami 镜像在该变量下执行集群初始化：等待 5 个节点可连后，向它们发送 `CLUSTER MEET` 与槽位分配命令，把 6 个独立节点组成真正的 Redis Cluster（16384 个槽分片）。

## 启动顺序如何被保证

两层 depends_on 形成拓扑（源码归一化与执行见[依赖图与 up/down 生命周期](../concepts/07-dependency-lifecycle.md)）：

```text
redis-node1..5 ──(depends_on)──▶ redis-cluster ──(depends_on)──▶ web
```

需要清醒认识的边界（源码事实）：

- 列表式 depends_on 的默认条件是 **`service_started`**——只保证"容器已启动"，不保证"集群已初始化完成"；
- 集群初始化（meet + 槽分配）需要数秒，web 若立刻连集群可能遇到集群尚未 ready；
- 本示例靠**镜像自身重试**消化这个窗口；生产中可用 Compose v3 的 `depends_on: {condition: service_healthy}` 配合 healthcheck（podman ≥ 4.6.0 支持 healthy 条件等待）。

## 运行（README 原始步骤）

```bash
cd examples/hello-app-redis
podman-compose up
# 浏览器打开 http://localhost:8080/
# 每次刷新计数 +1，计数写入 Redis 集群（键按槽分布到不同节点）
```

验证集群形态：

```bash
podman-compose exec redis-cluster redis-cli -c cluster nodes
# 列出 6 个节点、主从角色与槽位范围
podman-compose exec redis-cluster redis-cli -c get mycounter
# -c 表示集群模式跟随 MOVED 重定向
```

清理：

```bash
podman-compose down          # 停止删除容器与网络；6 个卷保留
podman-compose down -v       # 连同集群数据卷一起删除（下次 up 是全新集群）
```

## 规模手法小结

| 手法 | 本例用法 |
|------|---------|
| 同构服务复制 | 5 个节点配置仅名字/卷不同，靠服务名枚举组成员 |
| 服务名即发现 | REDIS_NODES 直接写服务名，无需 IP |
| 每服务独立卷 | 卷名与服务名对应（redis-node1-data），持久化互不干扰 |
| 专门的初始化服务 | creator 角色用环境变量区分，承载一次性集群组建逻辑 |
| 两层 depends_on | 表达"节点→创建者→客户端"拓扑 |

> 这种"N 个同构 worker + 1 个 creator/init 协调者"的结构是编排有状态集群的通用模式，与 nodeproj 的 init 服务（[10](10-nodeproj.md)）思路一致：用一个特殊角色的服务承载一次性初始化，而不是在编排器里写脚本。

## 相关示例与概念

- [多容器应用编排](02-multi-container.md)：同架构的教学化详解（自定义网络/健康检查）
- [官方示例图鉴](03-official-examples-gallery.md)
- [依赖图与 up/down 生命周期](../concepts/07-dependency-lifecycle.md)：depends_on 条件语义与 4.6.0 版本门槛
- [CLI 翻译层与标签状态](../concepts/05-cli-translation-layer.md)：每服务独立卷与服务别名
