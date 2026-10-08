---
okf_version: "0.2"
type: concept
title: "质量保障体系：技术债控制、High Level 视角注入与 Skill 开发原则"
description: "AI 写出高质量代码的三大保障——基础代码质量规则、DDD+ADR 注入 high level 视角、Skill 开发的纪律与 eval 意识"
tags: [codex, tech-debt, ddd, adr, skill-development, code-quality]
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

# 质量保障体系：技术债控制、High Level 视角注入与 Skill 开发原则

## 技术债控制：应对"AI Slop"

### 问题本质

> "AI 是可以写出高质量的代码的，只不过目前的局限在于它的注意力有限（其实人也一样），以及它太想完成用户指定的任务了，容易忽视其它目标。" [作者观点]

### 解决方案：利用 agent 的两大特性

| 特性 | 应对策略 |
|------|---------|
| 注意力有限 | 把质量规则前置到项目 setup 阶段，让 agent 在执行时自然兼顾 |
| 任务导向易忽视其他目标 | 专门建立技术债清理任务，让 agent 只做质量优化 |

### Setup 阶段的基础保障

| 措施 | 说明 |
|------|------|
| 代码 lint | 从架构、代码复杂度等角度给模型即时反馈 |
| 单文件 ≤ 500 行 | 最简单的软约束 [F-013](../article-source.md#F-013) |
| AGENTS.md 强制验证 | 强调写完代码后必须跑 typecheck、lint、test 等自动化验证 |

### 运行时问题处理

- **可规则化检查的 slop**：统一用规则脚本做，不放 prompt 浪费注意力
- **其它问题**：写入 AGENTS.md 或专项文档，通过 prompt 软约束

### 专用技术债清理任务

既然 agent 注意力有限，可以专门建立任务让它只做技术债清理 [作者实践]：

- 启动 agent 专门扫描问题并修复
- 寻找潜在 bug、优化测试覆盖、降低代码复杂度、优化架构
- 人类只需简单 review，快速决定是否合并

> "整体这么操作下来，AI 写出来项目的质量还是可以的。很多时候最后一道要过的坎是放下自己作为人类程序员的骄傲……" [作者感受]

## High Level 视角注入：DDD + ADR

### 问题：Agent 缺乏全局视野

之前发现 agent 做 code review 时几乎从不会从 high level 设计角度提出问题，这也是很多人诟病 agent 缺少全局视角、设计不够优雅的原因 [作者观察]。

在做技术债扫描时也发现，模型倾向于做小修小补，忽视 high level 设计明显有问题、概念分化后强行糅合形成的 god module 等问题。

### 解决方案：DDD 统一术语 + ADR 记录决策

#### DDD（领域驱动设计）的选用

只选取 DDD 中的 **ubiquitous language（统一语言）** 部分，与 agent 统一术语和理解 [作者实践]：

- 项目比较大时可拓展出 context map
- 暂时未引入 C4 架构视图（目录结构已能基本了解基础架构）

#### ADR（Architecture Decision Records）

引入 ADR 主要是记录演进过程中的决策，这些信息只看代码当前状态无法感知 [作者观点]。

### DDD + ADR 的三重效果

| 场景 | 效果 |
|------|------|
| 基于文档做设计 | Agent 天然更有 high level 视野，不易作出领域不一致的设计；新设计自动进文档 |
| Code review 时 | Agent 会关注新功能如何融入原有术语体系，检测潜在歧义、冲突 |
| 架构优化时 | Agent 能从概念模型角度思考，找出更有"战略意义"的优化项，而非小修小补 |

### 文档本身的维护

文档内容也使用 agent 做定期精简、清理，保持信息有效性和高密度 [F-030](../article-source.md#F-030)。

## Skill 开发原则

### 原则一：Skill 是"纪律"，智能由模型提供

- 避免在 skill 中写非常具体、死板的细节
- 限制模型发挥或导致 skill 缺乏泛化能力
- 因此 skill 篇幅通常较短，很少超过 100 行 [作者实践]

### 原则二：有做 Eval 的意识

- 测试有 skill 和没有 skill 的产出效果差别
- 模型和 agent 升级后，某些 skill 可能可简化或去掉
- 结合 eval 判断是否需要保留 [作者观点]

### 原则三：Skill 触发优化

- 经常直接把 skill 当快捷指令用
- 只有意外触发了不需要用的 skill 时，才调整 description [作者实践]

### 原则四：持续优化已有 Skill

- 让 Codex 自己分析 `~/.codex/sessions` 下的对话记录
- 判断是否有新增、修改、精简 skill 的需要
- "这时候你就会有点怀念 Claude 模型的书写表达能力了……" [作者感受]

## 为何不开源自己的 Skill

| 原因 | 说明 |
|------|------|
| 已有不错开源 skill repo | 推荐 Superpowers、Skills For Real Engineers [F-006](../article-source.md#F-006) |
| **Skill 爆破半径大** | skill 极大影响 agent 工作方式，比纯功能依赖的"爆破半径"大得多，轻易不敢装 |
| 使用方式不固定 | bugfix 时是否需要 plan？纯 UI 改动是否要 tdd？需充分了解细节才好灵活组合 |
| 更推荐的学习方式 | 让 agent 学习别人写的 skill，结合自己的工作习惯和已有 skill 逐渐添加和测试 |

> "既然这篇文章已经把背后的逻辑讲清楚了，相信读者要定制一个符合自己工作习惯的 skill set 应该不难。" [作者结语]

## 主题关联

- 与 [05-review-challenges](05-review-challenges.md) 衔接：TDD 是解决无用测试问题的方法论基础
- 与 [07-quality-assurance](07-quality-assurance.md) 互为补充：本篇讲 quality assurance 体系，上篇讲 review 具体挑战
- 与 [02-large-closed-loop](02-large-closed-loop.md) 衔接：文档维护（DDD+ADR）是大闭环基础设施的一部分

```{toctree}
:hidden:
:maxdepth: 1
```
