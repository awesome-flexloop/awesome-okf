# 概念文档

本目录按“先定位、再上手、再深入机制、最后落地”的顺序组织 10 篇概念文档。

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
```
