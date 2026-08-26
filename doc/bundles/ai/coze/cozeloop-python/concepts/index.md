# 概念文档

本目录包含 CozeLoop Python SDK 的概念文档，按学习路径从基础到高级排列。

## 基础篇

- [00 CozeLoop 概述与架构](/concepts/00-overview-architecture.md) — 三大功能域（Tracing/Prompt Hub/PTaaS）、分层架构、设计原则、框架支持

## 核心篇

- [01 Tracing 模型](/concepts/01-tracing-model.md) — Span/Trace/SpanContext 模型、标签系统（系统标签/自定义标签/Baggage）、标准数据模型、Span 生命周期、上报数据格式
- [02 LLM 埋点模式](/concepts/02-llm-instrumentation.md) — @observe 装饰器、OpenAI 自动 Instrumentation、手动 Span 创建、LangChain 集成、三种方式对比与最佳实践
- [03 上下文传播](/concepts/03-context-propagation.md) — ContextVar 隐式传播、双向链表、跨线程 child_of 传播、跨服务 header 传播（X-Cozeloop-Traceparent/Tracestate）、Baggage 详解

## 高级篇

- [04 配置、批量上报与性能](/concepts/04-configuration-batching.md) — 四队列批量上报引擎、数据截断与超大数据上报、客户端生命周期管理、超时配置、队列配置、生产环境性能优化

```{toctree}
:maxdepth: 7

00-overview-architecture
01-tracing-model
02-llm-instrumentation
03-context-propagation
04-configuration-batching
```
