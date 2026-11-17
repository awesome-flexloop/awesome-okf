---
okf_version: "0.2"
type: bundle
title: "Microsoft Agent Framework：从 1.0 到 Build 2026 的代理与工作流"
description: "微软 MAF 官方文档、Build 2026 公告与 1.25.0 源码的系统化中文教程——四支柱、代理管道、Harness、工具/技能/MCP、记忆/RAG/FIDES、工作流、托管运维、迁移、CodeAct 与源码实现"
tags: [Microsoft Agent Framework, MAF, Agent, 多代理工作流, Harness, CodeAct, Foundry, FIDES, Python, .NET]
generated: { by: "blog-article-to-okf-bundle", at: "2026-11-10T15:30:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-11-10T15:30:00+08:00" }
status: stable
stale_after: 2027-05-31
sources:
  - id: build2026
    resource: https://devblogs.microsoft.com/agent-framework/microsoft-agent-framework-at-build-2026-announce/
    title: "Microsoft Agent Framework at BUILD 2026: Agent Harness, Hosted Agents, CodeAct, and more（Shawn Henry，2026-06-03）"
  - id: learn-hub
    resource: https://learn.microsoft.com/zh-cn/agent-framework/
    title: "Agent Framework 文档（Microsoft Learn 中文版，页面更新 2026-10 ~ 2026-11）"
  - id: learn-overview
    resource: https://learn.microsoft.com/zh-cn/agent-framework/overview/
    title: "Microsoft Agent Framework 概述"
  - id: github
    resource: https://github.com/microsoft/agent-framework
    title: "microsoft/agent-framework（README、包结构与 Releases）"
  - id: verify
    resource: /references/verification.md
    title: "本知识包核验报告"
  - id: source
    resource: https://github.com/microsoft/agent-framework/commit/098214127
    title: "源码检出 commit 098214127（Python core 1.25.0 / .NET 1.28.0）"
---

# Microsoft Agent Framework：从 1.0 到 Build 2026 的代理与工作流

> **性质声明**：本 bundle 是**技术教程类知识包**，以 Microsoft Learn 官方文档为主信源、Build 2026 公告博文为事件信源、GitHub 仓库为版本信源。文中代码为最小化改写，不是官方原文；产品能力与默认值以你安装的版本为准。

Microsoft Agent Framework（MAF）在 2026-04-02 发布 1.0，把 AutoGen 与 Semantic Kernel 收敛为同一套代理与工作流编程模型（F-002、F-003）。两个月后的 Build 2026，团队又抛出四项改变“代理如何长期干活”的能力：Agent Harness、Foundry Hosted Agents、CodeAct 与 Handoff（F-099）。本知识包要回答的问题是：**这套框架由哪些层组成，每一层的边界在哪里，什么时候该用哪一层。**

## 为什么值得系统学

1. **它不是单点工具**。代理、Harness、工作流、托管、安全、可观测性在同一框架内，选型时容易只看到“能跑一个 Agent”，忽略后面的运维与安全成本。
2. **官方文档更新快、术语密**。Session、context provider、middleware、harness、workflow、orchestration 各自有明确所指，混用会导致设计错误。
3. **公告与文档存在口径差**。例如“自动压缩”在博文里像默认能力，在文档里需要配置预算（F-037）。本知识包把差异单独登记，不静默照搬。
4. **厂商自述数据需要标注**。CodeAct 的 52.4%/63.9% 提升是单源基准（F-105），不能当 SLA。

## 知识结构

```text
microsoft-agent-framework/
├── concepts/                     # 16 篇概念（10 文档 + 6 源码）
│   ├── 00-overview.md            # 定位、1.0、四支柱、语言矩阵
│   ├── 01-quickstart.md          # 安装、最小代理、会话
│   ├── 02-agent-architecture.md  # 管道、中间件、上下文、会话边界
│   ├── 03-harness.md             # Harness 能力矩阵与默认开关
│   ├── 04-tools-skills-mcp.md    # 工具、审批、MCP、Agent Skills
│   ├── 05-memory-rag.md          # 记忆三层、RAG、多用户越权
│   ├── 06-security-fides.md      # 提示注入与信息流控制
│   ├── 07-workflows.md           # 图/函数式、检查点、HITL、编排
│   ├── 08-hosting-operations.md  # Foundry/自托管、协议、Durable
│   ├── 09-build2026-migration.md # 四项公告、CodeAct、迁移
│   ├── 10-repo-map.md            # monorepo、版本与构建入口
│   ├── 11-core-agent-runtime.md  # Agent 组合、中间件、会话
│   ├── 12-harness-implementation.md # Harness 参数与默认值
│   ├── 13-workflow-runtime.md    # Builder、Runner、检查点
│   ├── 14-fides-implementation.md # FIDES 类与作用域
│   └── 15-codeact-and-dotnet.md  # Hyperlight、.NET 项目
├── examples/                     # 6 篇示例（5 演练 + 1 源码阅读）
│   ├── 00-hello-agent.md
│   ├── 01-tool-and-approval.md
│   ├── 02-harness-session.md
│   ├── 03-workflow-checkpoint.md
│   ├── 04-hosted-and-handoff.md
│   └── 05-source-reading-map.md
├── references/                   # 信源与核验
│   ├── article-source.md         # F-001 ~ F-170
│   ├── verification.md           # P0 对账与口径差异
│   └── source-code-map.md        # 源码信源、模块地图、计数口径
├── index.md
└── log.md
```

## 分层导航

### 入门路径（建议按顺序）

1. [MAF 是什么](concepts/00-overview.md)：先建立四支柱与语言矩阵，避免把 Harness 当框架全部。
2. [快速开始](concepts/01-quickstart.md)：跑通最小代理与会话。
3. [代理管道与中间件](concepts/02-agent-architecture.md)：理解“为什么我的中间件没生效”。
4. [Agent Harness](concepts/03-harness.md)：长任务代理的默认起点。

### 能力路径（按任务选读）

| 你要做 | 先读 | 再读 |
|--------|------|------|
| 给代理加工具/连 MCP | [工具、技能与 MCP](concepts/04-tools-skills-mcp.md) | [示例 01](examples/01-tool-and-approval.md) |
| 做知识库问答 | [记忆、RAG 与多用户边界](concepts/05-memory-rag.md) | [示例 00](examples/00-hello-agent.md) |
| 防提示注入/数据外泄 | [FIDES 安全](concepts/06-security-fides.md) | [核验报告](references/verification.md) |
| 多代理编排/可恢复流程 | [工作流与编排](concepts/07-workflows.md) | [示例 03](examples/03-workflow-checkpoint.md) |
| 上线与运维 | [托管与运维](concepts/08-hosting-operations.md) | [示例 04](examples/04-hosted-and-handoff.md) |
| 从 SK/AutoGen 迁移 | [Build 2026 与迁移](concepts/09-build2026-migration.md) | [工具文档](concepts/04-tools-skills-mcp.md) |

### 源码路径（第二轮新增）

1. [源码地图](concepts/10-repo-map.md)：先建立仓库与版本坐标系。
2. [核心运行时](concepts/11-core-agent-runtime.md)：跟一次 `run` 的类调用链。
3. [Harness 源码](concepts/12-harness-implementation.md) 与 [工作流源码](concepts/13-workflow-runtime.md)：看默认值与检查点协议。
4. [FIDES 源码](concepts/14-fides-implementation.md) 与 [CodeAct/.NET](concepts/15-codeact-and-dotnet.md)：看安全与执行边界。
5. [源码阅读示例](examples/05-source-reading-map.md)：用 6 条命令复现。

### 深读路径

1. 先读 [FIDES](concepts/06-security-fides.md) 再读 [CodeAct](concepts/09-build2026-migration.md)：理解“沙箱隔离 ≠ 信息流控制”。
2. 先读 [代理管道](concepts/02-agent-architecture.md) 再读 [Harness](concepts/03-harness.md)：看清 Harness 是组合而非新运行时。
3. 先读 [工作流](concepts/07-workflows.md) 再读 [托管](concepts/08-hosting-operations.md)：检查点与 Durable 的职责边界。

## 主题关联

| 知识包 | 关系 |
|--------|------|
| [AI Agent 框架](../ai-agent/index.md) | 同组框架集群；可对照工具调用、运行时与记忆的通用模式 |
| [LangChain-AI](../langchain-ai/index.md) | 另一条 LLM 应用框架路线；可对照图编排与可观测性设计 |
| [Agent 基础](../../learning/agent-fundamentals/index.md) | 先补代理/工具/记忆的基础概念，再读本包更顺 |
| [微软 MXC：Agent 执行隔离](../../practice/microsoft-mxc-agent-containment/index.md) | 操作系统层隔离视角；与本包 FIDES 的应用层信息流控制互补 |
| [Agent 平台笔记](../../practice/agent-platform-notes/index.md) | 平台化与托管视角；可与 Foundry Hosted 对照 |

## 数量与完整性

- 概念文档：**16 篇**（10 篇文档 + 6 篇源码）
- 示例：**6 篇**（5 篇演练 + 1 篇源码阅读）
- 信源文档：**3 篇**（F-001 ~ F-170，18 项 P0 核验 + 源码核验）
- 索引与日志：5 个文件
- 合计：**30 个文件**

## 信任与生命周期

- **生成方式**：官方文档与公告的检索、重构与核验；不是源码逐行解读。
- **核验**：18 项 P0 对账，5 处口径差异已单列（见 [verification.md](references/verification.md)）。
- **状态**：`stable`。核心事实有官方文档/Releases 交叉支持，源码篇另以 commit 098214127 做符号级核验；两项厂商自述数据已标注。
- **时效**：`stale_after: 2027-05-31`。Release 从 1.0 到 1.21 约六个月（F-008），源码快照已到 1.25.0/1.28.0（F-124、F-125）；半年后应复核包名、默认行为与托管状态。

## 已知边界

1. **非逐行注释**：第 10–15 篇做结构与符号级源码核验（类、方法、默认值、计数），不做逐行注释或完整调用链追踪。
2. **不覆盖 Go 全貌**：Go 为公共预览且独立仓库，本文只说明状态与能力边界（F-005、F-127）。
3. **源码为 main 快照**：commit 098214127，Python 1.25.0 / .NET 1.28.0，高于最新 Release 1.21（F-124、F-125、F-164）；源码结论不自动等同于已发布行为。
4. **CodeAct 基准为厂商自述**：52.4%/63.9% 未独立复现（F-105）。
5. **托管细节为博文单源**：缩容到零、文件系统保留、每会话 VM 隔离等细节需查 Foundry 文档（F-087）。
6. **示例非官方原文**：代码为最小化改写，版本升级后可能需调整。
7. **不构成合规认证**：安全与多用户边界建议是工程实践，不替代你的威胁建模与合规评审。

```{toctree}
:hidden:
:maxdepth: 2

concepts/index
examples/index
references/index
log
```
