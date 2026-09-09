# 概念索引（Concepts）

本目录收录 dolt-mcp（Dolt MCP Server）源码深度解读的 7 篇概念文档，按"认识→架构→部署→工具→安全→方言→内嵌模式"递进。

## 概念列表

| 序号 | 文档 | 核心内容 | 对应 F 编号 |
|------|------|---------|------------|
| 00 | [Dolt MCP Server 概述](00-overview.md) | 产品定位、解决的核心问题、三方言后端、45 工具能力版图、适用场景 | F-001~F-008、F-160~F-162 |
| 01 | [架构分层](01-architecture.md) | Server 接口→ToolSet→工具→Dialect→db 五层、请求生命周期 | F-010~F-016、F-040~F-053 |
| 02 | [部署与配置](02-deployment-configuration.md) | stdio/HTTP 模式、CLI 标志、Docker、JWT/HTTPS、环境变量 | F-020~F-035、F-080~F-085 |
| 03 | [工具全景与安全注解](03-tools-overview.md) | 45 工具十类分组、hint 安全注解四元组参考表、源码怪癖 | F-100~F-147 |
| 04 | [SQL 安全机制](04-sql-safety.md) | 读写通道分离、方言解析校验、事务隔离、注解元数据四层防线 | F-050、F-062/F-068/F-072/F-073、F-113/F-114 |
| 05 | [方言设计（三引擎适配）](05-dialect-design.md) | Dialect 接口、CALL 展开、SupportsTool 裁剪、DSN/TLS 对照 | F-040~F-043、F-060~F-074 |
| 06 | [DoltLite 内嵌模式](06-doltlite-mode.md) | 单文件内嵌、cgo 构建、事务并发模型、远程协议、本地优先 | F-090~F-095 |

## 阅读路径建议

```
00-overview（认识产品全貌）
    ↓
01-architecture（理解五层架构与请求链路）
    ↓
02-deployment-configuration（动手部署：stdio/HTTP/Docker）
    ↓
03-tools-overview（45 工具全图 + 安全注解）
    ↓
04-sql-safety（为什么 AI 拿 SQL 也安全）
    ↓
05-dialect-design（三引擎如何一套代码适配）
    ↓
06-doltlite-mode（零运维内嵌路径，宜结合 examples 体验）
```

## 概念依赖关系

```
00-overview
├── 01-architecture
│   ├── 03-tools-overview
│   │   └── 04-sql-safety
│   └── 05-dialect-design
│       └── 06-doltlite-mode
└── 02-deployment-configuration
    ├── 06-doltlite-mode
    └── 03-tools-overview
```

```{toctree}
:hidden:
:maxdepth: 2

00-overview
01-architecture
02-deployment-configuration
03-tools-overview
04-sql-safety
05-dialect-design
06-doltlite-mode
```
