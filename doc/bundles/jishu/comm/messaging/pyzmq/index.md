---
type: bundle
title: "PyZMQ：ZeroMQ Python 绑定"
okf_version: "0.2"
---

# PyZMQ：ZeroMQ Python 绑定

PyZMQ 是 ZeroMQ（高性能异步消息库）的 Python 绑定。它采用"薄绑定 + 厚语法层"的双层架构：后端层提供 Cython/CFFI 两种可插拔的 C 绑定，sugar 层用纯 Python 在其上叠加上下文管理器、序列化、属性访问、异步集成等 Pythonic API。

## 快速导航

### 概念文档（Concepts）

| 编号 | 文档 | 说明 |
|------|------|------|
| 00 | [整体架构与双后端机制](concepts/00-architecture-dual-backend.md) | Cython/CFFI 后端选择、sugar 层、public_api 契约 |
| 01 | [Context 生命周期与资源管理](concepts/01-context-lifecycle.md) | 单例、shadow、term/destroy、sockopts 默认选项 |
| 02 | [Socket 与 sugar 语法层](concepts/02-socket-sugar.md) | send/recv、序列化、订阅、监控、轮询 |
| 03 | [Frame 与消息](concepts/03-frame-message.md) | zero-copy、MessageTracker、GC 回调 |
| 04 | [Poller 多路复用](concepts/04-poller.md) | 事件轮询、select 兼容、原生 fd |
| 05 | [异步与 asyncio](concepts/05-async-future-asyncio.md) | Future 状态机、asyncio/tornado 双适配 |
| 06 | [认证与 ZAP](concepts/06-auth-zap.md) | PLAIN/CURVE 认证、Authenticator、证书 |
| 07 | [生态模块](concepts/07-ecosystem-eventloop-green-devices-log.md) | eventloop、green、devices、log、utils |

### 信源参考（References）

| 文档 | 说明 |
|------|------|
| [constants-enums.md](references/constants-enums.md) | 全量枚举常量与 `_opt_type` 机制 |
| [error-hierarchy.md](references/error-hierarchy.md) | 异常类层次与 `_check_rc` 决策表 |
| [cffi-internals.md](references/cffi-internals.md) | CFFI 后端实现细节 |
| [attrsettr-options.md](references/attrsettr-options.md) | 选项访问三层模型与动态属性 |

### 示例（Examples）

| 文档 | 模式 |
|------|------|
| [sync-pubsub.md](examples/sync-pubsub.md) | 同步 PUB/SUB 发布订阅 |
| [asyncio-pushpull.md](examples/asyncio-pushpull.md) | asyncio PUSH/PULL 管道 |

## 学习路径

1. **入门**：[00 整体架构](concepts/00-architecture-dual-backend.md) → [01 Context](concepts/01-context-lifecycle.md) → [02 Socket](concepts/02-socket-sugar.md)
2. **消息模型**：[03 Frame](concepts/03-frame-message.md) → [04 Poller](concepts/04-poller.md)
3. **进阶**：[05 异步](concepts/05-async-future-asyncio.md) → [06 认证](concepts/06-auth-zap.md) → [07 生态](concepts/07-ecosystem-eventloop-green-devices-log.md)
4. **实践**：[同步 PUB/SUB 示例](examples/sync-pubsub.md) → [asyncio PUSH/PULL 示例](examples/asyncio-pushpull.md)

## 事实基础

本知识包基于 118 条源码事实（F-001~F-118）和 5 个架构洞察生成，事实清单见 [spec/facts.md](spec/facts.md)，洞察与知识地图见 [spec/insights.md](spec/insights.md)。

## 变更日志

详见 [log.md](log.md)。

```{toctree}
:hidden:
:maxdepth: 7

concepts/index
examples/index
references/index
spec/index
log
```
