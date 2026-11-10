---
okf_version: "0.2"
type: Example
title: "示例：用 6 条检索命令走通源码请求链"
description: "从 Agent.run 到中间件、上下文、聊天客户端、工作流与检查点的源码定位命令，含每步预期命中文件与判读方法"
tags: [示例, 源码阅读, 检索, Agent, 工作流, 检查点]
generated: { by: "source-code-to-okf-wiki", at: "2026-11-10T16:42:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-11-10T16:42:00+08:00" }
status: stable
stale_after: 2027-05-31
sources:
  - id: source-map
    resource: /references/source-code-map.md
  - id: src-agents
    resource: https://github.com/microsoft/agent-framework/blob/098214127/python/packages/core/agent_framework/_agents.py
---

# 示例：用 6 条检索命令走通源码请求链

> 本示例的路径与命令基于 commit `098214127` 的本地检出。命令使用 PowerShell 的 `Select-String`；换成 `rg` 同理。

## 目标

不靠猜，按“请求从哪进、经过谁、状态存哪”定位代码。每一步都给出预期命中文件，命中不到说明版本或路径不对。

## 第 1 步：入口

```powershell
cd python/packages/core/agent_framework
Select-String -Path _agents.py -Pattern '^class (Agent|RawAgent|BaseAgent)'
```

预期命中 `class BaseAgent`、`class RawAgent`、`class Agent`（F-129）。

判读：`Agent` 是推荐入口，`RawAgent` 是最小实现。先看 `Agent` 的基类列表，确认它混入了中间件层与遥测层（F-130）。

## 第 2 步：运行参数

```powershell
Select-String -Path _agents.py -Pattern 'compaction_strategy|function_invocation_kwargs' | Select-Object -First 10
```

预期看到 `Agent.run` 重载里的 `compaction_strategy`、`tokenizer`、`function_invocation_kwargs`（F-131）。

判读：这些是运行级参数，不是构造参数；可以在单次调用覆盖。

## 第 3 步：中间件

```powershell
Select-String -Path _middleware.py -Pattern '^class (AgentMiddlewarePipeline|FunctionMiddlewarePipeline|ChatMiddlewarePipeline|AgentMiddlewareLayer)'
```

预期四个类全部命中（F-132）。

判读：三条 pipeline 分别对应代理运行、函数调用、模型调用。不要把它们当成一条链的三个阶段。

## 第 4 步：上下文与会话

```powershell
Select-String -Path _sessions.py -Pattern '^class (SessionContext|ContextProvider|HistoryProvider)|def extend_(messages|instructions|tools|middleware)'
```

预期命中 `SessionContext`、`ContextProvider`、`HistoryProvider` 与四个 `extend_*` 方法（F-134、F-135）。

判读：上下文提供程序靠 `before_run`/`after_run` 钩子工作；历史提供程序是它的子类。

## 第 5 步：Harness 装配

```powershell
Select-String -Path _harness/_agent.py -Pattern 'def create_harness_agent' -Context 0,60
```

预期看到 `max_context_window_tokens`、`disable_compaction`、`disable_file_memory`、`shell_executor` 等参数（F-139）。

判读：`shell_executor` 的存在说明 Python 侧有 Shell 能力（依赖预发布 `agent-framework-tools`，F-145、F-146）。

## 第 6 步：工作流与检查点

```powershell
Select-String -Path _workflows/_workflow_builder.py -Pattern '^    def (add_edge|add_fan_out_edges|add_fan_in_edges|add_chain)'
Select-String -Path _workflows/_checkpoint.py -Pattern '^class (CheckpointStorage|InMemoryCheckpointStorage|FileCheckpointStorage)'
```

预期命中 builder 的四类连边方法与三个检查点类型（F-148、F-151）。

判读：检查点协议只有 `save`/`load`/`list_checkpoints`；换存储不改工作流。

## 验证清单

- [ ] 六步都能在预期文件命中。
- [ ] 命中的类名与本文一致，没有“看起来像”的替代品。
- [ ] 版本为 1.25.0；若为 1.21，部分符号可能不存在。
- [ ] 不把 main 分支行为当成已发布行为（F-164）。

## 常见错误

| 现象 | 原因 | 处理 |
|------|------|------|
| 找不到 `AgentMiddlewarePipeline` | 路径不对或版本过旧 | 确认在 `python/packages/core/agent_framework` 下检索 |
| `shell_executor` 找不到 | 版本早于该特性 | 升级到含该参数的 commit |
| 检查点类只命中两个 | 检索了错误目录 | `_checkpoint.py` 在 `_workflows/` 下 |
| 把 `RawAgent` 当推荐入口 | 忽略类文档 | 先读 `Agent` 的 docstring |
