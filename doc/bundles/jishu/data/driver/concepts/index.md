# 概念索引（Concepts）

本目录收录 driver（Dolt Driver v2）源码深度解读的 5 篇概念文档，按"认识→架构→配置→生命周期→查询事务"递进。

## 概念列表

| 序号 | 文档 | 核心内容 | 对应 F 编号 |
|------|------|---------|------------|
| 00 | [Dolt Driver v2 概述](00-overview.md) | 产品定位、内嵌 vs 独立服务器对比、解决的核心问题 | F-001~F-008 |
| 01 | [架构分层](01-architecture.md) | Driver→Connector→Conn→Stmt→Rows 五层接口实现 | F-009~F-020 |
| 02 | [DSN 解析与 Config](02-dsn-config.md) | file:// 前缀、参数体系、LoadMultiEnvFromDir 多库模式 | F-003~F-007、F-012 |
| 03 | [连接生命周期与 BackOff 重试](03-lifecycle-and-retry.md) | Connector 共享 SqlEngine、backoff 重试模型、IsValid=false 策略 | F-010、F-016 |
| 04 | [查询执行与多语句支持](04-query-and-transaction.md) | 串行查询、Transaction、QuerySplitter RuneStack 嵌套感知 | F-013~F-015、F-017~F-021 |

## 阅读路径建议

```
00-overview（认识产品全貌）
    ↓
01-architecture（理解五层接口与数据结构）
    ↓
02-dsn-config（学会构造 DSN 和 Config）
    ↓
03-lifecycle-and-retry（理解并发安全机制）
    ↓
04-query-and-transaction（深入查询执行路径）
```

## 概念依赖关系

```
00-overview
├── 01-architecture
│   ├── 02-dsn-config
│   ├── 03-lifecycle-and-retry
│   └── 04-query-and-transaction
```

```{toctree}
:hidden:
:maxdepth: 2

00-overview
01-architecture
02-dsn-config
03-lifecycle-and-retry
04-query-and-transaction
```
