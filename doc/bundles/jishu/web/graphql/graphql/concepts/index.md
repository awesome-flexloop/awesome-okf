# GraphQL 核心概念

本目录包含 GraphQL 核心规范的 15 个概念文档，按学习路径排列：从语言概览到类型系统、验证执行，再到生态、AI 集成与工程实践逐步深入。

## 入门篇

* [00-overview](00-overview.md) — GraphQL 概览与五大设计原则
* [01-query-language-basics](01-query-language-basics.md) — 查询语言基础：文档、操作与选择集
* [02-schema-and-types](02-schema-and-types.md) — Schema 与类型系统入门
* [03-composite-types](03-composite-types.md) — 复合类型：对象、接口、联合与枚举
* [04-directives-and-wrapping-types](04-directives-and-wrapping-types.md) — 指令、包装类型与输入系统

## 核心篇

* [05-validation](05-validation.md) — 验证管线与规则体系
* [06-execution](06-execution.md) — 执行引擎：字段解析与值完成
* [07-response-and-errors](07-response-and-errors.md) — 响应格式、错误冒泡与序列化
* [08-introspection](08-introspection.md) — 内省系统：GraphQL 的自描述机制

## 高级篇

* [09-fragments-and-advanced-syntax](09-fragments-and-advanced-syntax.md) — 片段、变量作用域与 Schema Coordinates
* [10-python-ecosystem](10-python-ecosystem.md) — Python 生态：客户端与服务端实践
* [11-graphql-and-ai](11-graphql-and-ai.md) — GraphQL 与 AI：MCP、语义内省与 Agent

## 工程实践篇

* [12-client-engineering](12-client-engineering.md) — 前端客户端工程：库选型、HTTP 协议与缓存
* [13-server-engineering](13-server-engineering.md) — 服务端工程：Schema 开发模式、Context 与 DataLoader
* [14-best-practices](14-best-practices.md) — 最佳实践与反模式

```{toctree}
:hidden:
:maxdepth: 7

00-overview
01-query-language-basics
02-schema-and-types
03-composite-types
04-directives-and-wrapping-types
05-validation
06-execution
07-response-and-errors
08-introspection
09-fragments-and-advanced-syntax
10-python-ecosystem
11-graphql-and-ai
12-client-engineering
13-server-engineering
14-best-practices
```
