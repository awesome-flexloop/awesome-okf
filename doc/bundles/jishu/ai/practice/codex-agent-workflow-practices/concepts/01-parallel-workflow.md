---
okf_version: "0.2"
type: concept
title: "并行工作流：多 Session 与 Sub-Agent 协同模式"
description: "Codex Agent 并行工作的三种模式——多项目并行、sub-agent 分工并行、背景任务定时扫描，及配套架构要求"
tags: [codex, parallel, sub-agent, worktree, background-task]
sources:
  - id: blog
    url: https://zhuanlan.zhihu.com/p/2040748661567710711
generated:
  by: "agent:agnes"
  at: "2026-09-09T04:25:00+08:00"
verified:
  by: "process:seven-concepts-v"
  at: "2026-09-09T04:30:00+08:00"
status: stable
stale_after: "2026-11-21"
---

# 并行工作流：多 Session 与 Sub-Agent 协同模式

> 本节内容均来自作者实践描述 [F-010~F-013](../article-source.md)，属个人经验，非通用规范。

## 并行层级结构

```
多项目并行（2-3 个产品）
  └─ 每项目多 worktree（多个任务目录）
       └─ 每 worktree 多 Codex session（3-5 个并发）
            └─ 每 session 内 sub-agent 并行（如 3 个 review agent）
```

## 模式一：多项目 + 多 Worktree 并行

**做法**：日常保持 2-3 个产品项目并行，每个项目开多个目录/worktree 做不同任务 [F-011](../article-source.md#F-011)。

**效果**：token 消耗量不会低——只要保持 3-5 个 Codex session 持续工作产出 [F-013](../article-source.md#F-013)。

## 模式二：Sub-Agent 分工并行

### Code Review 并行

在 code review 时，并行启动 3 个 sub-agent，每个 agent 针对一个特定角度进行 review [F-012](../article-source.md#F-012)：

- 优点：agent 专注力更高，找到有效问题的概率提升
- 代价：总体消耗 token 更多

### 原型方案并行

使用多个 agent 出方案，开拓思路（探索性任务尤其适用）。

### 子任务并行分解

将一个 feature 拆分为多个子任务，无依赖关系的子任务启用 sub-agent 并行执行。

**架构要求**：模块之间边界相对清晰，耦合度低 [作者观点]。

## 模式三：背景任务（Background Tasks）

定时启动 agent 任务，自动执行以下工作：

| 任务类型 | 说明 |
|---------|------|
| 技术债务扫描 | 定期扫描项目技术债 |
| PR 监控与处理 | 跟踪 pull request 状态 |
| Bug 修复 | 识别并修复潜在 bug |
| 依赖升级 | 自动更新依赖版本 |

## 并行 vs 串行的权衡

| 维度 | 并行 | 串行 |
|------|------|------|
| Token 消耗 | 高 | 低 |
| 单位时间产出 | 高 | 低 |
| Context switch 成本 | 低（agent 内部处理） | 高（人类介入） |
| 架构要求 | 模块边界清晰、低耦合 | 无特殊要求 |
| 适合场景 | 无依赖子任务、独立模块 | 有强依赖关系的任务 |

## 主题关联

- 与 [02-large-closed-loop](02-large-closed-loop.md) 互补：并行提升吞吐量，大闭环提升单个任务完整性
- 与 [06-spec-and-plan](06-spec-and-plan.md) 中的"任务切分"呼应：垂直切片拆分后更适合并行执行

```{toctree}
:hidden:
:maxdepth: 1
```
