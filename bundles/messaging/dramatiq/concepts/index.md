# 概念文档

以下 9 篇概念文档按学习路径编号排列，覆盖 dramatiq v2.2.0 的核心架构。

| 编号 | 文档 | 简介 |
|------|------|------|
| 00 | [整体架构](00-overall-architecture.md) | Actor/Broker/Worker/Middleware/Message 五大组件关系与数据流 |
| 01 | [Actor 装饰器](01-actor-decorator.md) | `@dramatiq.actor` 注册机制、send/\_\_call\_\_ 双模态、GenericActor |
| 02 | [Broker 抽象基类](02-broker-abstraction.md) | 模板方法模式、emit 信号机制、Consumer/MessageProxy 抽象 |
| 03 | [Worker 线程模型](03-worker-threading-model.md) | ConsumerThread + WorkerThread + PriorityQueue 流水线与优雅关闭 |
| 04 | [Message 与序列化](04-message-and-serialization.md) | frozen dataclass 不可变信封、encode/decode、copy、options 总线 |
| 05 | [Middleware 中间件管道](05-middleware-pipeline.md) | 洋葱模型钩子生命周期、默认中间件顺序、SkipMessage 机制 |
| 06 | [Encoder 编码层](06-encoder.md) | Encoder ABC、JSONEncoder/PickleEncoder、全局编码器管理 |
| 07 | [Results 结果后端](07-results-backend.md) | ResultBackend 抽象、Redis/Stub 实现、Results 中间件 |
| 08 | [CLI 与 Watcher](08-cli-and-watcher.md) | 多进程 fork、信号处理、watchdog 热重载、Canteen 共享内存 |
