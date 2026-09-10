---
okf_version: "0.2"
type: concept
title: "对抗提升范式：Review Fix Loop 与 Best-of-N"
description: "通过多 agent 对抗迭代提升输出质量的两种核心模式——Review/Test Fix Loop 与 Best-of-N 并行采样"
tags: [codex, adversarial, review-loop, best-of-n, agent-prompting]
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

# 对抗提升范式：Review Fix Loop 与 Best-of-N

## 核心原理

> "通过消耗更多的 token，来提升 agent 完成工作的质量，从而减少人类注意力的投入" [作者观点]

**为什么需要分角色（独立 context）对抗**：训练一个模型拥有批评能力，比训练它拥有自我批评能力容易得多 [作者洞察]。

## 模式一：生成-验证迭代（Fix Loop）

一个 agent 做生成，另一个 agent 做验证，不断迭代：

| Loop 类型 | 用途 | 说明 |
|----------|------|------|
| Review Fix Loop | 代码质量提升 | 生成 agent 写代码，验证 agent review，迭代修复 |
| Test Fix Loop | 测试覆盖提升 | 生成 agent 写实现，验证 agent 检查测试覆盖，迭代补充 |

### 作者的 Review Fix Loop 实践

**初始问题**：在 GitLab MR review 环节做双 agent 对抗，导致两位研发需要反复触发各自 agent 提出意见、做修改，消耗不少注意力，且常达 10 多轮 [F-022~F-023](../article-source.md)。

**解决方案**：增加 `review-change-loop` skill，让 agent 在提交代码给别人 review **之前**，先自己做多轮对抗，力求首次提交的 MR 质量较高，大多数情况下不会找出 P0/P1 级别问题 [作者实践]。

**深化策略**：
- 使用 sub-agent 开启干净 context 进行 review
- 利用多个 sub-agent，每个专注一个方面的 review
- Agent 数量根据修改复杂程度、涉及面动态调整 [作者实践]
- 让 agent 做端到端测试，把验证过程与结果证据贴到 MR 中 [作者实践]

### Best-of-N 模式

多个 agent 并行生成方案，再由 agent/人来选一个最好的：

- 尤其适合**探索性任务** [作者观点]
- 消耗更多 token，但提升找到优质方案概率

## 两种模式对比

| 维度 | Fix Loop | Best-of-N |
|------|----------|-----------|
| 执行方式 | 串行迭代 | 并行采样 |
| 适合场景 | 有明确质量标准（如 review） | 探索性、多种可行方案 |
| Token 效率 | 较高（逐步收敛） | 较低（N 倍消耗） |
| 质量提升 | 渐进式修复 | 多选最优 |
| 人类介入点 | 最终验收 | 方案选择 |

## 实际应用中的问题

作者在应用中碰到不少问题，包括但不限于：

- Agent 数量需要权衡：过多消耗 token，过少效果有限
- 对抗质量取决于验证 agent 的能力：验证能力不足则 loop 无效
- Best-of-N 的选择标准本身需要明确定义

> 这些问题属于作者实践中的探索性发现，具体解决方案因项目而异 [作者观点]。

## 主题关联

- 与 [05-review-challenges](05-review-challenges.md) 深度关联：Review Fix Loop 是解决 review 多轮耗时问题的核心手段
- 与 [02-large-closed-loop](02-large-closed-loop.md) 衔接：对抗提升是大闭环中的质量保障机制

```{toctree}
:hidden:
:maxdepth: 1
```
