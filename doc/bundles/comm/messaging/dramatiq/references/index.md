# 信源登记簿

以下 4 篇信源文档登记 dramatiq v2.2.0 各核心模块的源码级分析。

| 文档 | 简介 |
|------|------|
| [RedisBroker 内部结构](redis-broker-internals.md) | Lua 脚本 dispatch.lua 全量解析、Redis key 命名空间、ack/nack/requeue/maintenance 机制 |
| [RabbitmqBroker 内部结构](rabbitmq-broker-internals.md) | 线程局部 Channel、dead-letter exchange、confirm_delivery、consumer 线程模型 |
| [内置中间件详解](built-in-middleware.md) | AgeLimit/TimeLimit/ShutdownNotifications/Callbacks/Pipelines/Retries 的参数与钩子逻辑 |
| [异常类层次结构](error-hierarchy.md) | DramatiqError/BrokerError/Retry/DecodeError 等异常的继承关系与触发场景 |

```{toctree}
:hidden:

built-in-middleware
error-hierarchy
rabbitmq-broker-internals
redis-broker-internals
```
