---
okf_version: "0.2"
type: bundle
title: "通用 Agent 的 Coding Harness：复用编码运行时"
description: "基于 Thoughtworks Technology Radar Vol 35 的 Trial 级 blip，系统解读 coding harness 的定义、四个编程入口、运行时能力、护栏差异、领域适配与采用路径。"
tags: [thoughtworks, technology-radar, coding-harness, agent-runtime, claude-agent-sdk, codex, opencode, pi, sandboxing]
generated: { by: "lobsterai/main", at: "2026-11-10T15:05:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-11-10T15:05:00+08:00" }
status: stable
stale_after: "2027-04-30"
sources:
  - id: article
    resource: /references/article-source.md
  - id: radar
    resource: https://www.thoughtworks.com/radar/techniques/coding-harness-for-general-purpose-agents
  - id: radar-index
    resource: https://www.thoughtworks.com/radar
  - id: claude-sdk
    resource: https://code.claude.com/docs/en/agent-sdk/overview
  - id: codex-sdk
    resource: https://github.com/openai/codex/blob/main/sdk/typescript/README.md
  - id: opencode-sdk
    resource: https://opencode.ai/docs/sdk/
  - id: pi-sdk
    resource: https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/sdk.md
  - id: agent-sandboxing
    resource: https://www.thoughtworks.com/radar/techniques/agent-sandboxing
  - id: enterprise-harness
    resource: https://www.thoughtworks.com/radar/techniques/enterprise-harness
  - id: harness-quality
    resource: https://www.thoughtworks.com/radar/techniques/harness-quality-evaluation
---

# 通用 Agent 的 Coding Harness：复用编码运行时

> **内容性质**：技术综述与行业洞察，非操作教程。源文是 Thoughtworks Technology Radar Vol 35 的一条 Trial 级 blip，没有可复现的安装/配置流程，因此按“操作可复现性两问”判定**不设 examples/**；官方 SDK 的最小调用形状放在概念文档中，仅作形态说明。

## 核心结论

Coding harness 是包在模型外面的 agent 运行时：它负责 agent loop、工具执行、上下文压缩、会话持久化与运行控制。所谓“面向通用任务的 coding harness”，就是把这层已经在编码场景大量使用的运行时，复用到文档处理、运营支持、迁移规划等非编码任务上（F-005、F-006）。

它解决的问题不是“模型不够强”，而是“自建 agent loop 太贵”。与 agent framework 相比，coding harness 用控制力换成熟度：loop、工具、压缩、会话都已有实现，团队把精力放在领域适配与治理上（F-014）。代价是编码偏向的提示与工具、较大的内置提示开销，以及需要自己补的领域评测与安全层（F-020～F-025）。

文章点名了四个编程入口：Claude Agent SDK、Codex SDK 与 app-server、OpenCode server 与 SDK、Pi SDK 与 RPC（F-007～F-010）。它们的进程模型、会话机制与护栏位置各不相同；选型时先看“边界”，再看“能力”（F-016、F-017）。

## 四个入口速查

| 入口 | 形态 | 最适合 |
|---|---|---|
| Claude Agent SDK | 库，驱动 Claude Code 子进程 | 想要与 Claude Code 一致的完整能力 |
| Codex SDK | TypeScript 库，包装 Codex CLI | 单进程脚本、批处理、快速嵌入 |
| Codex app-server | JSON-RPC 服务端 | 服务化、多客户端、统一审批 |
| OpenCode server + SDK | 无头 HTTP + OpenAPI 客户端 | 多语言接入、HTTP 边界 |
| Pi SDK | 进程内 TypeScript 库 | 最小依赖、完全可控 |
| Pi RPC | 长驻子进程 + JSONL | 进程隔离、跨语言控制 |

详细对照见 [四个编程入口](concepts/01-four-programmatic-surfaces.md)。

## 采用前先回答五个问题

1. 任务是否需要多轮工具调用与长时运行？
2. 是否需要会话恢复、分叉与审计？
3. 是否需要复用 skills、子代理与项目指令？
4. 沙箱、审批、审计分别由哪一层承担？
5. 单任务 token、轮数与延迟预算是否可接受？

如果前三个问题的答案是“否”，coding harness 很可能过度设计；如果第四个问题没有答案，先不要上线。

## 阅读路径

```{toctree}
:hidden:
:maxdepth: 2

concepts/index
references/index
log
```

1. [什么是 Coding Harness](concepts/00-what-is-a-coding-harness.md)：先建立定义与四层区分。
2. [四个编程入口](concepts/01-four-programmatic-surfaces.md)：看清 SDK、server、RPC 的边界。
3. [运行时替你做了什么](concepts/02-reused-runtime-capabilities.md)：循环、压缩、会话、无头执行。
4. [护栏与能力差异](concepts/03-guardrails-and-capability-differences.md)：沙箱、审批、扩展模型。
5. [领域适配与隐性成本](concepts/04-domain-fit-and-hidden-costs.md)：编码偏向、token、评测。
6. [采用路径](concepts/05-adoption-playbook.md)：五步落地、评分卡、迁移与治理。
7. [雷达坐标](concepts/06-radar-context-and-related-blips.md)：Vol 35 的 harness 主题簇。

## 主题关联

| 知识包 | 关系 |
|--------|------|
| [Pi Agent Harness](../../frameworks/ai-agent/pi-agent-harness/index.md) | 同为 harness 主题；该束侧重 Pi 的架构与竞品综述，本束侧重“通用任务复用”的选型与治理 |
| [OpenAI Codex](../../frameworks/ai-agent/openai-codex/index.md) | 本束的四个入口之一；该束提供 Codex 的产品与工作流背景 |
| [OpenCode](../../frameworks/ai-agent/opencode/index.md) | 本束的四个入口之一；该束提供 OpenCode 的源码与架构细节 |
| [AI Agent 基础](../../frameworks/ai-agent/ai-agent-fundamentals/index.md) | 先读基础架构模式，再读本束的运行时复用 |
| [AI 工程方法论](../ai-engineering-methodology/index.md) | Harness 工程、上下文工程与评测方法的上位方法论 |
| [Codex Agent 工作流实践](../codex-agent-workflow-practices/index.md) | 编码 agent 的成本与并行工作流实践，可与本束的成本章节对照 |

## 核验摘要

- P0 核验：发布信息、四个编程入口、会话/无头能力、沙箱与审批、相关 blip 评级，全部通过或有明确口径。
- 事实登记：F-001～F-047，共 47 条；spec 与 bundle 双份一致。
- 勘误：4 条口径细化（E-1～E-4），无源文硬错误。
- 单源边界：.NET 迁移加速器为厂商自述；token 成本与编码偏向为作者经验判断。
- 状态：stable；`stale_after` 设为 2027-04-30，下一期雷达或 SDK 破坏性变更时复核。
