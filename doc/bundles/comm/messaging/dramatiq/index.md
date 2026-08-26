---
type: bundle
title: "Dramatiq：Python 分布式任务队列"
okf_version: "0.2"
---

# Dramatiq 知识库

本知识库基于 [dramatiq v2.2.0](https://github.com/Bogdanp/dramatiq) 源码深度分析生成，采用 OKF v0.2 格式组织。dramatiq 是一个 Python 分布式任务队列库，以 Actor 装饰器为核心抽象，支持 Redis 和 RabbitMQ 两种消息后端，提供多进程 × 多线程的 Worker 模型和基于洋葱模型的中间件管道。

## 概念文档

9 篇概念文档按学习路径编号，从整体架构到各核心组件逐层深入：

| 编号 | 文档 | 简介 |
|------|------|------|
| 00 | [整体架构](concepts/00-overall-architecture.md) | Actor/Broker/Worker/Middleware/Message 五大组件关系与数据流 |
| 01 | [Actor 装饰器](concepts/01-actor-decorator.md) | 注册机制、send/\_\_call\_\_ 双模态、GenericActor 类式 actor |
| 02 | [Broker 抽象基类](concepts/02-broker-abstraction.md) | 模板方法、emit 信号、Consumer/MessageProxy 抽象 |
| 03 | [Worker 线程模型](concepts/03-worker-threading-model.md) | ConsumerThread + WorkerThread + PriorityQueue、优雅关闭 |
| 04 | [Message 与序列化](concepts/04-message-and-serialization.md) | frozen dataclass 不可变信封、encode/decode、options 总线 |
| 05 | [Middleware 中间件管道](concepts/05-middleware-pipeline.md) | 洋葱模型、默认中间件顺序、SkipMessage 机制 |
| 06 | [Encoder 编码层](concepts/06-encoder.md) | JSON/Pickle 编码器、全局编码器管理 |
| 07 | [Results 结果后端](concepts/07-results-backend.md) | ResultBackend 抽象、Redis/Stub 实现、Results 中间件 |
| 08 | [CLI 与 Watcher](concepts/08-cli-and-watcher.md) | 多进程 fork、信号处理、watchdog 热重载 |

完整概念索引见 [concepts/index.md](concepts/index.md)。

## 实战示例

| 文档 | 简介 |
|------|------|
| [基础 Actor 与 Worker](examples/basic-actor-and-worker.md) | 定义 actor、配置 broker、send 消息、启动 Worker 的完整代码与流程追踪 |
| [重试与管道](examples/retry-and-pipeline.md) | max_retries/throws 配置、pipeline 组合、Results 获取结果、group 并行 |

完整示例索引见 [examples/index.md](examples/index.md)。

## 信源登记簿

| 文档 | 简介 |
|------|------|
| [RedisBroker 内部结构](references/redis-broker-internals.md) | Lua 脚本全量解析、Redis key 命名空间、ack/nack/maintenance 机制 |
| [RabbitmqBroker 内部结构](references/rabbitmq-broker-internals.md) | 线程局部 Channel、dead-letter exchange、confirm_delivery、consumer 模型 |
| [内置中间件详解](references/built-in-middleware.md) | AgeLimit/TimeLimit/Retries/Pipelines/Callbacks 等中间件的参数与钩子逻辑 |
| [异常类层次结构](references/error-hierarchy.md) | DramatiqError 继承树、各异常触发场景与处理方式 |

完整信源索引见 [references/index.md](references/index.md)。

## 信任说明

- **R 阶段**：从 dramatiq v2.2.0 源码提取 96 条编号事实（F-001 ~ F-096），每条标注源文件与行号，零推测
- **I 阶段**：基于事实提炼 5 个核心洞察四元组与知识地图
- **E 阶段**：生成 9 篇概念文档 + 4 篇信源文档 + 2 篇示例文档，每篇 frontmatter 的 `sources.facts` 字段标注支撑该文档的事实编号
- 所有 API、类名、方法签名均经过源码 Grep 级验证
- 文档当前验证状态为 `v-pending`（待独立 V 阶段验证）

```{toctree}
:maxdepth: 7

concepts/index
examples/index
references/index
spec/index
log
```
