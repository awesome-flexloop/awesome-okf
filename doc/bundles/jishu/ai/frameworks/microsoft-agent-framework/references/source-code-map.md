---
okf_version: "0.2"
type: Reference
title: "源码信源登记：agent-framework 本地检出与模块地图"
description: "本地源码检出的 commit、版本、目录结构与模块地图，F-121~F-170 的核验路径与计数口径"
tags: [源码信源, 模块地图, commit, 计数口径, Microsoft Agent Framework]
generated: { by: "source-code-to-okf-wiki", at: "2026-11-10T16:20:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-11-10T16:20:00+08:00" }
status: stable
stale_after: 2027-05-31
sources:
  - id: src
    resource: https://github.com/microsoft/agent-framework/commit/098214127
    title: "microsoft/agent-framework commit 098214127（本地检出核验）"
  - id: local
    resource: /references/source-code-map.md
    title: "本地检出说明（env-bound，按 commit 固定）"
---

# 源码信源登记：agent-framework 本地检出

## 1. 信源固定信息

| 项 | 值 |
|----|----|
| 本地路径 | `D:\spaces\SpecWeave\external\dao\action\agent-framework` |
| 远程 | `https://github.com/microsoft/agent-framework` |
| commit | `098214127` |
| `git describe` | `dotnet-1.28.0-19-g098214127` |
| 提交时间 | 2026-11-10 00:31:58 +0000 |
| Python core 版本 | `1.25.0` |
| .NET `VersionPrefix` | `1.28.0` |

**稳定性说明**：本地路径属于 env-bound 信源。本文档与 facts 只用 commit hash 作为可复现锚点，正文引用一律用**仓库相对路径**（如 `python/packages/core/agent_framework/_agents.py`），不写 `file:///` 绝对路径。检出目录被移动或删除后，按同一 commit 重新 clone 即可复现。

**与已发布版本的差异**：commit 位于 `dotnet-1.28.0` 之后 19 个提交，Python core 为 1.25.0，高于 GitHub Releases 最新的 `python-1.21.0`（F-008、F-164）。因此源码事实描述的是 **main 分支快照**，不是 1.21 发布版。

## 2. 顶层目录

| 目录 | 内容 |
|------|------|
| `python/` | Python SDK；`python/packages/` 下 44 个包（F-123） |
| `dotnet/` | .NET SDK；`dotnet/src/` 下 38 个项目（F-126） |
| `go/` | 仅 `README.md`，指向 `microsoft/agent-framework-go`（F-127） |
| `declarative-agents/` | 声明性代理目录（F-170） |
| `skills/` | 技能目录（F-170） |
| `docs/` | 设计决策与仓库内文档 |
| `.github/`、`.devcontainer/`、`.vscode/` | CI、开发容器与编辑器配置 |

## 3. Python 模块地图

### 3.1 核心包 `python/packages/core/agent_framework/`

| 文件/目录 | 关键定义 | 事实 |
|-----------|---------|------|
| `_agents.py` | `SupportsAgentRun`、`BaseAgent`、`RawAgent`、`Agent` | F-129、F-130 |
| `_middleware.py` | `AgentMiddleware`、`FunctionMiddleware`、`ChatMiddleware`、三条 pipeline、`AgentMiddlewareLayer` | F-132 |
| `_sessions.py` | `SessionContext`、`ContextProvider`、`HistoryProvider`、`_RunPersistenceGate` | F-134、F-135 |
| `_compaction.py` | `CompactionStrategy` 协议 + 9 个策略 + `CompactionProvider` | F-136、F-137 |
| `_clients.py` | 聊天客户端抽象与函数调用层 | F-128 |
| `_tools.py` | 工具定义与调用 | F-128 |
| `_skills.py` | 技能加载与渐进式披露 | F-128 |
| `security.py` | FIDES：标签、策略中间件、`SecureAgentConfig` | F-153、F-154 |
| `observability.py` | OpenTelemetry 接入 | F-128 |
| `_harness/` | Harness 的 8 个实现文件 | F-144 |
| `_workflows/` | 图与函数式工作流运行时 | F-147 |

### 3.2 Harness `_harness/`

| 文件 | 关键定义 |
|------|---------|
| `_agent.py` | `create_harness_agent`、`DEFAULT_HARNESS_INSTRUCTIONS` |
| `_loop.py` | `AgentLoopMiddleware`、`DEFAULT_MAX_ITERATIONS = 10` |
| `_background_agents.py` | `BackgroundAgentsProvider`、默认等待 300 秒 |
| `_file_memory.py` / `_file_access.py` | 文件记忆与文件访问 |
| `_todo.py` / `_mode.py` | 待办与计划/执行模式 |
| `_tool_approval.py` | 审批规则与自动审批 |
| `_memory.py` | 记忆提供程序 |

### 3.3 工作流 `_workflows/`

| 文件 | 关键定义 |
|------|---------|
| `_workflow.py` | `Workflow`、`WorkflowRunResult`、输出指定 |
| `_workflow_builder.py` | `WorkflowBuilder`（边、扇出/扇入、分支、链） |
| `_executor.py` | `Executor` |
| `_runner.py` | `RunnerImpl`（迭代、检查点、恢复） |
| `_checkpoint.py` | `WorkflowCheckpoint`、`CheckpointStorage`、内存/文件实现 |
| `_functional.py` | `FunctionalWorkflow`、`FunctionalWorkflowAgent` |

### 3.4 其它 Python 包

`python/packages/` 同时包含 provider（`openai`、`anthropic`、`gemini`、`bedrock`、`ollama`、`mistral` 等）、集成（`a2a`、`ag-ui`、`chatkit`、`devui`、`declarative`、`lab`、`orchestrations`、`hosting-*`）与 `tools`、`hyperlight`、`monty`（F-169）。

## 4. .NET 模块地图

| 项目 | 角色 |
|------|------|
| `Microsoft.Agents.AI.Abstractions` | 抽象与接口 |
| `Microsoft.Agents.AI` | 核心实现：`AIAgent`、`ChatClientAgent`、middleware、`TextSearchProvider` |
| `Microsoft.Agents.AI.Harness` | `HarnessAgent`、`HarnessAgentOptions`、`ChatClientHarnessExtensions` |
| `Microsoft.Agents.AI.Workflows` | `Executor`、`Edge`、`CheckpointManager`、`AgentWorkflowBuilder` |
| `Microsoft.Agents.AI.Hyperlight` / `.LocalCodeAct` | CodeAct 两种执行后端 |
| `Microsoft.Agents.AI.Tools.Shell` | Shell 工具 |
| `Microsoft.Agents.AI.Hosting` / `.Hosting.*` | 自托管与协议端点 |
| `Microsoft.Agents.AI.Foundry.Hosting` | Foundry 托管入口 |
| provider 项目 | OpenAI、Anthropic、GitHub Copilot、Azure AI、MCP 等 |

（F-126、F-159、F-161、F-162、F-168）

## 5. 计数口径

本文与 concepts 中出现的数量陈述，均按下列口径脚本计数：

| 陈述 | 口径 | 结果 |
|------|------|------|
| Python 包数 | `Get-ChildItem python/packages -Directory` | 44 |
| .NET 项目数 | `Get-ChildItem dotnet/src -Directory` | 38 |
| core 顶层 py 文件 | `Get-ChildItem .../core/agent_framework -File -Filter *.py` | 24 |
| Harness 实现文件 | `_harness/*.py`，含空 `__init__.py` | 9 |
| 工作流运行时文件 | `_workflows/*.py` | 见目录（不在此断言总数） |

**注意**：目录数 ≠ 包发布数 ≠ 知识包数；`python/packages` 含测试/示例相邻目录，44 是目录计数，不是 PyPI 包计数。

## 6. 核验方式

1. 类名/方法名：`Select-String` 在对应文件中检索 `^class` / `^def` / `^    def`。
2. 版本：读取 `pyproject.toml`、`nuget-package.props`。
3. 数量：脚本 `Get-ChildItem ... | Measure-Object`，不靠目测。
4. 文档-源码差异：以源码为准记录到 [verification.md](verification.md)，并保留文档口径。

## 7. 已知边界

1. 本地检出为 env-bound；复现需同一 commit。
2. main 分支快照可能领先发布版；本文不把源码行为等同于已发布行为。
3. 未执行 Python/.NET 测试套件；结论来自静态阅读与符号检索。
4. 计数为目录/文件级，不是 API 级；不声称“完整覆盖所有类”。
