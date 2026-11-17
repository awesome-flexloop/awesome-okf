---
okf_version: "0.2"
type: Concept
title: "源码地图：monorepo 结构、版本快照与构建入口"
description: "agent-framework 仓库的 python/dotnet/go 三端布局、44 个 Python 包与 38 个 .NET 项目、1.25.0/1.28.0 版本快照、uv/poe 与 dotnet build 入口"
tags: [源码, monorepo, 构建, 版本, Python, .NET]
generated: { by: "source-code-to-okf-wiki", at: "2026-11-10T16:25:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-11-10T16:25:00+08:00" }
status: stable
stale_after: 2027-05-31
sources:
  - id: source-map
    resource: /references/source-code-map.md
  - id: src
    resource: https://github.com/microsoft/agent-framework/commit/098214127
---

# 源码地图：monorepo 结构、版本快照与构建入口

前 10 篇概念基于官方文档与公告；从本篇开始，信源切换为**本地源码检出**。这不是重复劳动：文档告诉你“怎么用”，源码告诉你“它到底怎么实现、哪些默认值是真的”。

本次检出的锚点：commit `098214127`，`git describe` = `dotnet-1.28.0-19-g098214127`，Python core `1.25.0`，.NET `1.28.0`（F-121、F-124、F-125）。它比 GitHub Releases 最新的 `python-1.21.0` 更靠前（F-164），所以后文描述的是 **main 分支快照**，不是已发布包的行为。

## 顶层：三端 SDK + 两个资产目录

```text
agent-framework/
├── python/                 # Python SDK（44 个包目录）
├── dotnet/                 # .NET SDK（38 个项目）
├── go/                     # 仅 README，指向独立 Go 仓库
├── declarative-agents/     # 声明性代理
├── skills/                 # 技能
├── docs/                   # 设计决策与仓库文档
└── .github/ .devcontainer/ .vscode/
```

（F-122、F-123、F-126、F-127、F-170）

`go/` 只有一份 README，正文指向 `microsoft/agent-framework-go`（F-127）。这与文档“Go 为独立仓库、公共预览”的说法一致（F-005）——至少在这个 commit 上，Go 没有被并入主仓。

## Python 侧：44 个包，core 是心脏

`python/packages/` 有 44 个目录（F-123）。它们可以分成五类：

| 类别 | 代表包 | 作用 |
|------|--------|------|
| 核心 | `core` | Agent、中间件、会话、工作流、Harness、安全 |
| 模型 provider | `openai`、`anthropic`、`gemini`、`bedrock`、`ollama`、`mistral` | 接不同推理服务 |
| 协议/托管 | `a2a`、`ag-ui`、`hosting`、`hosting-a2a`、`hosting-mcp`、`hosting-responses`、`hosting-telegram` | 把代理暴露出去 |
| 能力扩展 | `tools`、`hyperlight`、`monty`、`orchestrations`、`declarative`、`devui` | Shell、CodeAct、编排、声明式、开发 UI |
| 存储/检索 | `azure-ai-search`、`azure-cosmos`、`mem0`、`mongodb`、`postgres`、`redis`、`qdrant` | 向量库、记忆、检查点 |

（F-169；分类为本文归纳，不是仓库官方分类）

核心包 `agent_framework/` 顶层有 24 个 `.py` 文件（F-128），其中最重要的五个：

1. `_agents.py`：`BaseAgent` / `RawAgent` / `Agent`（F-129）。
2. `_middleware.py`：三类中间件与三条 pipeline（F-132）。
3. `_sessions.py`：`SessionContext` / `ContextProvider` / `HistoryProvider`（F-134）。
4. `_compaction.py`：9 种压缩策略（F-136）。
5. `security.py`：FIDES（F-153）。

外加两个子包：`_harness/`（8 个实现文件 + 空 `__init__.py`）与 `_workflows/`（运行时、检查点、函数式 API）（F-144、F-147）。

## .NET 侧：38 个项目，按职责拆分

`dotnet/src/` 有 38 个项目目录（F-126）。与 Python 的单包多模块不同，.NET 把每个能力拆成独立 NuGet 项目：

| 层 | 项目 |
|----|------|
| 抽象 | `Microsoft.Agents.AI.Abstractions` |
| 核心 | `Microsoft.Agents.AI` |
| Harness | `Microsoft.Agents.AI.Harness` |
| 工作流 | `Microsoft.Agents.AI.Workflows`、`.Workflows.Declarative` |
| CodeAct | `Microsoft.Agents.AI.Hyperlight`、`.LocalCodeAct` |
| Shell | `Microsoft.Agents.AI.Tools.Shell` |
| 托管 | `Microsoft.Agents.AI.Hosting`、`.Hosting.*`、`.Foundry.Hosting` |
| Provider | `Microsoft.Agents.AI.OpenAI`、`.Anthropic`、`.GitHub.Copilot`、`.AzureAI.Persistent`、`.Mcp` 等 |

（F-168、F-159、F-161、F-162）

这种拆分方式影响你的依赖管理：Python 装一个 `agent-framework` 元包就带很多集成；.NET 要按需装多个包，包之间通过 `Microsoft.Agents.AI.Abstractions` 的接口解耦。

## 版本快照：源码领先发布

| 维度 | 源码检出 | 最新 Release（2026-11-10） |
|------|---------|---------------------------|
| Python core | 1.25.0 | `python-1.21.0`（2026-10-08） |
| .NET | 1.28.0 | `dotnet-1.21.0`（2026-09-11） |

（F-124、F-125、F-008、F-164）

读源码时最容易犯的错，是把 main 的行为当成已发布行为。两个版本之间可能有 API 增删（本 commit 的提交标题就是 “[BREAKING] Reduce Foundry Hosting API surface”）。**写代码前先看你装的包版本**。

## 构建与测试入口

Python（仓库 `python/` 目录）：

```bash
uv run poe build
uv run poe test -A -m "not integration"
uv run poe syntax
uv run poe check
```

.NET（仓库 `dotnet/` 目录）：

```bash
dotnet build
```

以上命令来自 `CONTRIBUTING.md` 的构建说明，不是推测。集成测试需要 API key/endpoint；单元测试默认排除 integration 标记。

## 怎么读这份源码

建议按“请求生命周期”读，而不是按目录字母序：

1. 从 `_agents.py` 的 `Agent.run` 进入，看它如何组合中间件层与 `RawAgent`（F-130、F-131）。
2. 跳到 `_middleware.py`，看 `AgentMiddlewareLayer` 如何缓存并执行 pipeline（F-132）。
3. 回到 `_sessions.py`，看 `ContextProvider.before_run/after_run` 如何注入历史与上下文（F-135）。
4. 需要长任务时读 `_harness/_agent.py` 的 `create_harness_agent`，对照参数与默认值（F-138、F-139）。
5. 需要编排时读 `_workflows/_workflow_builder.py` 与 `_runner.py`（F-148、F-150）。
6. 需要安全时读 `security.py`（F-153）。

## 与文档篇的关系

| 文档篇 | 源码篇 | 关系 |
|--------|--------|------|
| 02 代理管道 | 11 核心运行时 | 文档给分层图，源码给类与顺序 |
| 03 Harness | 12 Harness 实现 | 文档给能力矩阵，源码给参数与默认值 |
| 06 FIDES | 14 FIDES 实现 | 文档给威胁模型，源码给类与状态绑定 |
| 07 工作流 | 13 工作流运行时 | 文档给概念，源码给 builder/runner/checkpoint |
| 09 CodeAct | 15 CodeAct 与 .NET | 文档给公告，源码给 provider 与沙箱接口 |

## 已知边界

1. 本快照为 main 分支，可能含未发布变更。
2. 44/38/24 是目录/文件计数，不是 PyPI/NuGet 包数或 API 数。
3. 未运行测试套件；构建命令来自 CONTRIBUTING，未在本机执行。
4. Go 仅登记 README 指向，未读 Go 仓库源码。
