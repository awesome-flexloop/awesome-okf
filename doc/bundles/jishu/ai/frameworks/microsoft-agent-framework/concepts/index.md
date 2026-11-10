# 概念文档

本目录按“先定位、再上手、再深入机制、最后读源码”的顺序组织 16 篇概念文档。前 10 篇基于官方文档与公告，后 6 篇基于 1.25.0 源码检出（commit 098214127）。

| 文档 | 核心内容 |
|------|---------|
| [00 MAF 是什么](00-overview.md) | 1.0 GA、AutoGen/SK 收敛、四支柱、.NET/Python/Go 矩阵、Agent vs Workflow |
| [01 快速开始](01-quickstart.md) | 安装、最小代理、流式、会话、`.env` 与凭据坑 |
| [02 代理管道与中间件](02-agent-architecture.md) | 三层管道、执行顺序、三类中间件、上下文提供程序、会话边界 |
| [03 Agent Harness](03-harness.md) | Harness 架构、能力矩阵、默认开关、压缩、文件记忆、语言边界 |
| [04 工具、技能与 MCP](04-tools-skills-mcp.md) | 工具类型、审批边界、代理即工具、SKILL.md 规范、渐进式披露 |
| [05 记忆、RAG 与多用户边界](05-memory-rag.md) | 会话/历史/检索三层、TextSearchProvider、服务端 ID 越权风险 |
| [06 FIDES 安全](06-security-fides.md) | 提示注入威胁模型、标签传播、四组件、策略模式、CodeAct 限制 |
| [07 工作流与编排](07-workflows.md) | 图/函数式 API、原语、检查点、HITL、五种编排 |
| [08 托管与运维](08-hosting-operations.md) | Foundry 托管、自托管、协议、Durable Extension、可观测性 |
| [09 Build 2026 与迁移](09-build2026-migration.md) | 四项公告、CodeAct 基准、SK/AutoGen 迁移、版本时间线 |
| [10 源码地图](10-repo-map.md) | monorepo、44 个 Python 包、38 个 .NET 项目、版本与构建入口 |
| [11 核心运行时](11-core-agent-runtime.md) | Agent 组合、run 参数、三条 pipeline、SessionContext、9 种压缩 |
| [12 Harness 源码](12-harness-implementation.md) | create_harness_agent 参数、循环 10 次上限、后台 300 秒、Shell 边界 |
| [13 工作流源码](13-workflow-runtime.md) | Builder 六类连边、RunnerImpl 收敛、CheckpointStorage 协议 |
| [14 FIDES 源码](14-fides-implementation.md) | 标签枚举、作用域绑定、两个策略中间件、.NET 空白 |
| [15 CodeAct 与 .NET](15-codeact-and-dotnet.md) | HyperlightProvider 参数、沙箱限制、两种 CodeAct 后端 |

```{toctree}
:hidden:
:maxdepth: 2

00-overview
01-quickstart
02-agent-architecture
03-harness
04-tools-skills-mcp
05-memory-rag
06-security-fides
07-workflows
08-hosting-operations
09-build2026-migration
10-repo-map
11-core-agent-runtime
12-harness-implementation
13-workflow-runtime
14-fides-implementation
15-codeact-and-dotnet
```
