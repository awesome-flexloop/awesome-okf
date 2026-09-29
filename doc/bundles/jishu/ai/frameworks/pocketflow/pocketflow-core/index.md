---
title: PocketFlow 核心框架
type: index
bundle: pocketflow-core
version: 0.1.0
description: |
  PocketFlow 是一个仅100行代码的极简 LLM Agent 框架。本知识包覆盖核心 API：
  12 个类、节点三阶段生命周期、Flow 编排引擎、运算符 DSL、重试降级、
  批量处理（BatchNode/BatchFlow）、异步并行（AsyncNode/AsyncFlow）。
concepts:
  - node-lifecycle: 节点三阶段生命周期（prep→exec→post）
  - flow-orchestration: Flow 编排引擎与四种流程模式
  - operator-chaining: 运算符 DSL（>> 和 -）
  - retry-fallback: 重试与降级机制
  - batch-processing: 批量处理（BatchNode/BatchFlow）
  - async-parallel: 异步与并行（AsyncNode/AsyncFlow族）
references:
  - base-node: BaseNode 基类（params/successors/next/run）
  - node: Node 同步节点（重试/fallback）
  - flow: Flow 同步编排引擎
  - batch-node: BatchNode 单节点批量
  - batch-flow: BatchFlow 子流程级批量
  - async-node: AsyncNode 及异步类族（含并行批量）
examples:
  - getting-started: 快速开始（线性/分支/循环/重试）
---

# PocketFlow 核心框架

PocketFlow 是一个极简的 LLM Agent 框架，核心代码仅约 100 行。它将 Agent 抽象为**节点（Node）+ 流程（Flow）**两个核心概念，通过运算符重载提供声明式 DSL，支持线性管道、条件分支、循环、嵌套、重试降级、批量处理和异步并行。

## 核心设计哲学

- **极简抽象**：Node 只有 prep/exec/post 三方法，Flow 只有一个编排循环
- **零依赖**：仅使用 Python 标准库（copy/warnings/asyncio）
- **图结构**：节点通过运算符连接成有向图，支持任意拓扑
- **Shared 存储**：节点间通过字典通信，简单直接

## 快速导航

### 核心概念
- [节点生命周期](concepts/node-lifecycle.md) — prep→exec→post 三阶段模型
- [流程编排](concepts/flow-orchestration.md) — Flow 的 while 循环与四种模式
- [运算符 DSL](concepts/operator-chaining.md) — `>>` 默认边和 `- "action" >>` 条件边
- [重试与降级](concepts/retry-fallback.md) — max_retries 和 exec_fallback
- [批量处理](concepts/batch-processing.md) — BatchNode 与 BatchFlow
- [异步与并行](concepts/async-parallel.md) — AsyncNode 族与 asyncio.gather

### API 参考
- [BaseNode](references/base-node.md) — 基类：params、successors、next、run、运算符
- [Node](references/node.md) — 同步节点：max_retries、exec_fallback、_exec 重试循环
- [Flow](references/flow.md) — 流程编排：start、run、_orch、get_next_node、嵌套
- [BatchNode](references/batch-node.md) — 单节点批量：_exec 遍历 items
- [BatchFlow](references/batch-flow.md) — 子流程批量：prep 返回 params 列表
- [AsyncNode](references/async-node.md) — 异步类族：6个异步类速查

### 示例
- [快速开始](examples/getting-started.md) — 线性管道、条件分支、循环、重试

## 12 个核心类一览

| 类名 | 类型 | 关键特性 |
|------|------|---------|
| BaseNode | 基类 | params/successors/三方法/运算符 |
| Node | 同步节点 | max_retries + exec_fallback |
| BatchNode | 同步批量节点 | prep→[exec×N]→post |
| Flow | 同步流程 | 图编排/分支/循环/嵌套 |
| BatchFlow | 同步批量流程 | 多参数驱动子流程 |
| AsyncNode | 异步节点 | async 三方法 + 重试 |
| AsyncBatchNode | 异步串行批量 | 顺序 await 每个 item |
| AsyncParallelBatchNode | 异步并行批量 | asyncio.gather 并发 |
| AsyncFlow | 异步流程 | await 驱动节点流转 |
| AsyncBatchFlow | 异步串行批量流程 | 顺序 await 子流程 |
| AsyncParallelBatchFlow | 异步并行批量流程 | gather 并发子流程 |

## 源码

- 核心：pocketflow/\_\_init\_\_.py
- 测试：tests/

```{toctree}
:hidden:
:maxdepth: 7

concepts/async-parallel
concepts/batch-processing
concepts/flow-orchestration
concepts/node-lifecycle
concepts/operator-chaining
concepts/retry-fallback
examples/getting-started
references/async-node
references/base-node
references/batch-flow
references/batch-node
references/flow
references/node
spec/facts
```
