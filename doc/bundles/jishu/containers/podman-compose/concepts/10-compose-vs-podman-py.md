---
type: Concept
title: podman-compose 与 podman-py 对比：编排器与 SDK 的选型
description: 全面对比 Podman 生态两大自动化工具：CLI 编排器 podman-compose（声明式 YAML→子进程）与 Python SDK podman-py（命令式代码→REST 客户端），覆盖架构、抽象级别、状态模型、远程能力、错误处理与选型决策
tags: [podman, podman-compose, podman-py, comparison, orchestration, sdk, declarative, imperative]
generated: { by: "source-code-to-okf-wiki", at: "2026-09-10T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-09-10T00:00:00Z" }
status: stable
stale_after: "2027-09-10"
sources:
  - id: compose-bundle
    resource: /index.md
    title: podman-compose 知识束（v1.6.0 / commit e3df104）
  - id: py-bundle
    resource: ../../podman-py/index.md
    title: podman-py Python SDK 知识束（v5.8.0）
  - id: source-code
    resource: /references/source-code-map.md
    title: podman_compose.py 源码信源登记
---

# podman-compose 与 podman-py 对比：编排器与 SDK 的选型

Podman 生态有两个官方自动化工具，都面向"不用手工敲 podman 命令"，但处在完全不同的抽象层：

- **podman-compose**：命令行**编排器**——读声明式 YAML，把整个多服务应用翻译成并执行 podman CLI；
- **podman-py**：Python **SDK**——在代码里以面向对象方式调用 Podman 的 libpod REST API。

本文基于两束源码精读（compose 侧 v1.6.0 / commit e3df104，py 侧 v5.8.0）做系统对比，回答"我的场景该用哪个"。

## 一句话定位

| | podman-compose | podman-py |
|---|---|---|
| 形态 | 单文件 CLI 工具（`pip install podman-compose`） | Python 库（`pip install podman`，PyPI 包名 `podman`） |
| 许可证 | GPL-2.0 | Apache-2.0 |
| 一句话 | Compose Spec YAML → podman 子进程的**声明式编排器** | docker-py API 兼容的**命令式 REST 客户端** |
| 主要用户 | 运维/部署人员，面向"应用栈" | Python 开发者，面向"资源操作" |
| 版本基线 | podman-compose 1.6.0（podman ≥ 3.4） | podman-py 5.8.0（Python ≥ 3.9） |

## 架构对照

两者最终都驱动同一个 podman 引擎，但控制路径完全不同：

```text
podman-compose 的路径：                         podman-py 的路径：

compose.yaml                                  your_script.py
   │ 插值/合并/归一化                            │ Python 方法调用
   ▼                                            ▼
service dict                                  PodmanClient（薄门面）
   │ container_to_args 翻译                     │ containers.run(...)
   ▼                                            ▼
podman argv 列表                              domain Manager/Mixin
   │ asyncio.create_subprocess_exec             │ HTTP 请求构造
   ▼                                            ▼
podman CLI（子进程）                          APIClient（requests.Session）
   │ fork/exec                                  │ HTTP over UDS / SSH 隧道 / TCP
   ▼                                            ▼
podman 引擎 ────────────────────────────────► libpod REST API（podman system service / socket）
```

关键事实：**podman-compose 不依赖 podman-py**。compose 的 imports 只有 asyncio/subprocess/yaml/dotenv 等标准与少量三方库——它直接 `exec` podman 二进制；而 podman-py 根本不 fork 子进程，直接打 REST 接口。两者是平行的两条接入路径。

## 十维对比

| 维度 | podman-compose | podman-py |
|------|---------------|-----------|
| 范式 | **声明式**：描述"栈应该长什么样" | **命令式**：描述"执行什么操作" |
| 输入 | YAML 文件（+ .env/环境变量/CLI 旗标） | Python 函数参数（**kwargs dict） |
| 执行机制 | asyncio 子进程，shell out 到 podman CLI | requests.Session HTTP 客户端，调 libpod REST |
| 抽象边界 | **应用栈**：多服务/网络/卷/pod/依赖的整体生命周期 | **资源对象**：容器/镜像/网络/卷/pod/secret/quadlet 等 9 类 Manager 的 CRUD+操作 |
| 多服务编排 | 内建：依赖图（12 条件）、重建判定、up/down 拓扑、并行 gather | 无内建：需要自己写循环/依赖逻辑（Manager 只提供单资源操作） |
| 状态模型 | **标签即数据库**：身份与 config-hash 存容器标签，进程无状态 | **资源对象 + 实时 API**：Container/Image 对象 attrs，需要时 `reload()` 查服务端 |
| 配置能力 | bash 风格插值、`!override/!reset` 深合并、extends/include/profiles、x-podman 扩展 | 纯函数参数；无合并/插值/继承——组合逻辑由 Python 代码承担 |
| 远程能力 | 间接：依赖 podman CLI 自身的 system connection/SSH 上下文 | 原生：四级连接优先级（命名连接/base_url/active_service/本地 socket），内置 UDS/SSH/TCP 六方案，SSH 自建 `ssh -N -L` 隧道 |
| 错误处理 | 退出码 + 日志（`--verbose` 看命令行）；进程级失败 | Python 异常体系：APIError→NotFound/ImageNotFound、ContainerError、BuildError 等可捕获 |
| 可测试性 | `--dry-run` 打印将执行的 argv；黑盒 | requests-mock mock HTTP 做单元测试；integration 测试 + skipif/pnext 版本门控 |

## 配置与参数：YAML 声明 vs kwargs 调用

同样"起一个带端口映射的 nginx"，两边的表达：

**podman-compose**（compose.yaml，声明意图，翻译与执行交给工具）：

```yaml
services:
  web:
    image: docker.io/library/nginx:stable
    ports:
      - "${HOST_PORT:-8080}:80"
```

**podman-py**（Python 代码，显式控制每一步）：

```python
from podman import PodmanClient

with PodmanClient() as client:
    client.containers.run(
        "docker.io/library/nginx:stable",
        ports={"80/tcp": 8080},
        detach=True,
        name="web",
    )
```

差异的本质：

- compose 擅长"这套配置在任何环境里 `up` 就能复现整个栈"，并免费得到 down/重建/日志聚合/依赖顺序；
- SDK 擅长"根据运行时条件决定做什么"——比如遍历带某标签的容器批量检查、对失败容器做自定义重试逻辑、把容器操作嵌入更大的 Python 工作流。

## 与 Docker 生态的兼容路径

两者都以 Docker 用户为迁移目标，但兼容的是 Docker 世界的**不同层**：

| | podman-compose | podman-py |
|---|---|---|
| 兼容对象 | docker-compose（工具/文件格式） | docker-py（SDK/API 签名） |
| 迁移成本 | 大部分 compose.yaml 直接可用；差异靠 `x-podman.docker_compose_compat` 等开关或直接改文件 | `pip` 换包 + `DockerClient = PodmanClient` 别名导入（三行改动）；差异为 Swarm 不支持、sparse 默认值、socket 路径等 |
| 不支持面 | Compose Spec 之外的复杂编排仍需扩展字段 | Swarm 三端点 NotImplementedError、无 `docker.types.*` 对象、无 BuildKit buildx |

## 生命周期管理的边界

这是最容易选错的维度：

- **应用栈生命周期**（多服务依赖顺序、滚动重建、配置漂移检测、down 联动清理网络/卷）是 compose 的核心资产——它维护 `_deps/_dependents` 图、config-hash 变更判定、标签化资源发现（见[依赖图与 up/down 生命周期](07-dependency-lifecycle.md)）；用 SDK 重写这些等于自己写一个编排器。
- **单资源/交互式操作**（"给这个容器发个信号""抓这台主机上所有镜像的列表""在容器里执行命令并拿返回码""构建镜像并实时渲染进度条"）是 SDK 的舒适区：`container.kill(signal=...)`、`client.images.list()`、`container.exec_run()` 返回三元组、`images.build(stream=...)` 配合 Rich 进度条。

## 选型决策表

| 场景 | 选择 | 理由 |
|------|------|------|
| 部署/管理一个多服务应用（Web+DB+缓存） | **podman-compose** | 声明式栈、依赖顺序、重建/清理一条龙 |
| 把现有 docker-compose.yaml 迁到 Podman | **podman-compose** | 文件直接复用，兼容开关兜底 |
| CI/CD 流水线里部署整套环境 | **podman-compose** | `up -d`/`down` 是为流水线准备的命令面，systemd 单元还能常驻 |
| 编写测试脚手架/测试容器编排 | **podman-py** | 可在测试代码里起停容器、断言状态、mock 错误 |
| 运维巡检/批量操作（按标签清理、批量重启） | **podman-py** | 列表过滤 + 循环 + 条件逻辑，比 shell 解析 podman 输出可靠 |
| 远程主机上操作容器（SSH/TCP） | **podman-py** 更顺手 | 原生连接抽象与 SSH 隧道；compose 需依赖 podman CLI 的 remote 上下文 |
| 平台/自研系统集成容器能力 | **podman-py** | 库形式嵌入进程，异常可捕获，无 shell 依赖 |
| 需要构建镜像并拿编程化进度/产物对象 | **podman-py** | build/pull 返回对象与流；compose 构建只是生命周期一环 |
| rootless 单机应用常驻、开机自启 | **podman-compose** | systemd register 工作流开箱即用 |

## 组合使用：不是二选一

生产实践中两者互补：

- **compose 负责声明与部署**：compose.yaml 作为应用栈的单一事实来源，`up -d` 完成部署；
- **podman-py 负责编程化运维与验证**：部署后用 SDK 跑健康断言（`client.containers.list(filters=...)`、`exec_run` 做服务就绪探测）、做定时巡检、生成报表，或在测试套件里管理测试容器。

两者的资源视图通过同一套标签体系对齐：podman-compose 给资源打的 `io.podman.compose.*` / `com.docker.compose.*` 标签（见[CLI 翻译层与标签状态](05-cli-translation-layer.md)），podman-py 侧 `containers.list(filters={"label": "..."})` 可以直接按这些标签筛选——编排器写标签、SDK 读标签，是两条路径天然的接缝。

## 共同点（容易被忽视）

- **都 daemonless**：compose 进程退出后无状态（状态在标签）；podman-py 也不连任何专用 daemon，只打 podman 自己的 REST socket；
- **都原生 rootless 友好**：compose 侧见 [rootless 模式](02-rootless.md)；podman-py 默认 socket 就是 `$XDG_RUNTIME_DIR/podman/podman.sock`（rootless）；
- **都是 Python 3.9+**，都把 podman 当作外部能力边界，自己保持薄；
- **都以兼容 Docker 为迁移策略**：一个兼容 docker-compose 文件格式，一个兼容 docker-py API。

## 相关概念

- podman-compose 侧：[单文件架构与 asyncio 执行模型](04-source-architecture.md)、[CLI 翻译层与标签状态](05-cli-translation-layer.md)、[依赖图与 up/down 生命周期](07-dependency-lifecycle.md)
- podman-py 侧：[Docker SDK 兼容性与三层代码架构](../../podman-py/concepts/00-introduction.md)、[连接配置与远程传输适配器](../../podman-py/concepts/01-connection.md)、[资源管理器架构 Mixin+Manager](../../podman-py/concepts/02-managers.md)、[高级资源、异常体系与工程治理](../../podman-py/concepts/05-advanced.md)
- 分组视角：[容器生态域索引](../../index.md)（13 个容器技术束导航）
