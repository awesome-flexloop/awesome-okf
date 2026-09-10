---
okf_version: "0.2"
type: concept
title: "Review 挑战与解决方案：从多轮耗时到 Review 左移"
description: "四大 Review 痛点——多轮耗时、Review 左移、Scope 膨胀、无用测试——及对应的 skill 化解决方案"
tags: [codex, code-review, scope-inflation, tdd, skill]
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

# Review 挑战与解决方案：从多轮耗时到 Review 左移

## 挑战一：Review 多轮耗时

### 问题描述

去年已采用的"一个 agent 写代码，另一个 agent review"对抗方式，在 GitLab MR review 环节存在问题 [F-022~F-023](../article-source.md)：

- 两位研发需反复触发各自 agent 提出意见、做修改
- 消耗不少注意力
- 多次达 10 多轮修改仍未收敛

### 解决方案：Review-Change-Loop Skill

增加 `review-change-loop` skill，让 agent 在提交代码给别人 review **之前**，先自己做多轮对抗 [作者实践]：

- 目标：首次提交的 MR 质量较高
- 效果：大多数情况下不会找出 P0/P1 级别问题
- 深化：使用 sub-agent 开启干净 context，多 agent 各专注一个 review 方向
- Agent 数量根据修改复杂程度、涉及面动态调整

### 端到端测试证据

进一步加强 MR 质量：让 agent 做端到端测试，把验证过程与结果证据贴到 MR 中 [作者实践]：

- 对 agent 和人来做 review 都更有信心
- MR 数量爆炸后，这方面的证据提供能大大降低人类注意力投入

## 挑战二：Review 左移

### 现状

人类 review 过程尚未完全替代，创建 MR 后仍有：

- 同事的 agent/人工 review，提 comment
- 等待"昂贵"的 CI pipeline 执行

### 解决方案：Babysit-MR Skill

搞了 `babysit-mr` skill，自动处理 MR 的后续反馈和所需修改，持续跟进到 MR 被 approve/merge 为止 [作者实践]。

> 如果是项目主要负责人，还可以搞类似 `sweep-mrs` skill，根据状态逻辑批量处理每一个 open 的 MR [作者实践]。

### Review 解决方案总结

| 策略 | 作用 | 阶段 |
|------|------|------|
| Agent 做 pre-review | 首次提交即高质量，减少 P0/P1 问题 | Review 前置 |
| Agent 做测试 + 贴证据 | 增强合并信心 | Review 辅助 |
| Review 左移至 Spec/Plan | 从源头减少问题 | 最前置 |

> 顺带一提：如果用 GitHub，Codex 官方有不少 skill 可直接使用 [F-025](../article-source.md#F-025)。

## 挑战三：Scope 膨胀

### 问题模式

观察 MR 中两个 agent "魔法对轰"过程发现：

- 初始改动：500 行不到 [F-014](../article-source.md#F-014)
- 多轮迭代后：膨胀至 2000+ 行 [F-012](../article-source.md#F-012)
- 后果：引入问题的面扩大，更难收敛 review 提出的问题

### 解决方案演进

| 尝试 | 效果 |
|------|------|
| 在 AGENTS.md 中说明控制 scope | 效果不好 |
| 告诉 agent 超过 5 轮未收敛时看 high level 设计 | 效果不好 |
| **优化 PRD 和创建 MR 的 skill，必须写清楚 out of scope** | 效果不错 |

### 关键洞察

Agent 终于可以分辨：

- 需要严格审核的成熟模块迭代
- 只是想做一个原型探索的场景

不会一上来就要求做到"火箭发射级软件"的程度 [作者观点]。

## 挑战四：无用测试

### 问题

之前的 code review skill 中有"复杂业务逻辑必须有相应测试，但也不应该过度测试"的表述，但实际跑下来仍经常出现聊胜于无的测试用例，如：

- 仅测试某个 class 创建出来的各个字段内容

### 解决方案：TDD Skill

增加 `tdd` skill，让 agent **先写测试，再写实现** [作者实践]。

### TDD 的三重好处

1. **提升代码设计**：可测试性提升连带优化模块化、副作用隔离等优秀实践
2. **规避无用测试**：总体测试质量提升
3. **加快反馈速度**：Red-Green-Refactor 工作方式比全部写完再补测试更不容易挖坑或方向跑偏

### TDD 不适用场景

> "探索性的 UI 交互迭代显然不太适合" [作者观点]

### 测试验收的重要性被拔高

在 AI 生产力爆炸时代，测试验收的重要度被大大拔高，未来还有很多探索空间 [作者观点]。

## 主题关联

- 与 [03-adversarial-improvement](03-adversarial-improvement.md) 衔接：Review Fix Loop 是解决多轮耗时的核心机制
- 与 [06-spec-and-plan](06-spec-and-plan.md) 衔接：out of scope 声明是解决 scope 膨胀的关键
- 与 [07-quality-assurance](07-quality-assurance.md) 衔接：TDD 是技术债控制的底层方法论

```{toctree}
:hidden:
:maxdepth: 1
```
