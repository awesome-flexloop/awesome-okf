---
type: Concept
title: "从聊天生成到类型化决策"
description: "解释 System One、state、Noul、Choice、Score，以及类型约束与业务正确性的区别"
tags: [Jev, System One, Noul, Choice, Score]
generated: { by: "process:seven-concepts-e", at: "2026-09-20" }
verified: { by: "process:seven-concepts-v", at: "2026-09-20" }
status: flagged
stale_after: 2026-10-20
sources:
  - { id: article, resource: "/references/article-source.md" }
  - { id: intro, resource: "https://docs.typesafe.ai/introduction" }
  - { id: system-one, resource: "https://docs.typesafe.ai/concepts/system-one" }
  - { id: quickstart, resource: "https://docs.typesafe.ai/introduction/quickstart" }
---

# 从聊天生成到类型化决策

## 1. Jev 解决的接口错位

普通 LLM 主要生成给人阅读的文本；软件却需要一个可以直接分支、排序或路由的值。文章把 Jev 描述为“不会说话的 AI”，这个比喻抓住了接口差异，但不能理解成模型没有自然语言理解能力。[F-002、F-016](../references/article-source.md)

System One 的核心接口是：

```text
state + typed questions -> typed answers + probabilities
```

`state` 是待判断的内容，可以是消息、记录或应用状态；问题定义答案空间；外围代码把答案接入业务流程。[F-016～F-019](../references/article-source.md)

## 2. 三种原语

| 原语 | 适合的问题 | 主要输出 | 设计提醒 |
| --- | --- | --- | --- |
| Noul | 是/否或真假 | `noul`，表示 yes 的概率 | 0.5 是边界不确定，不是“中等分数” |
| Choice | 有限选项中选一个 | `choice`、概率分布、`confidence` | 选项不穷尽时保留 `other/none` |
| Score | 有序等级或连续倾向 | `score`、概率分布、`confidence` | 先定义等级语义，再解释数值 |

三种问题可以在同一请求中混用并独立评估。[F-007、F-017、F-021～F-022](../references/article-source.md)

## 3. 类型安全不等于事实正确

类型约束可以保证返回结构符合约定，例如 `choice` 属于某个枚举；它不能证明状态被正确理解，也不能替代权限、规则和人工复核。文章的“几乎不可能产生幻觉”应收敛为：**减少自由文本解析错误，不消除业务判断错误**。[F-005、F-021](../references/article-source.md)

因此，任何自动动作至少需要三层检查：

1. 结构检查：字段和答案空间是否有效。
2. 业务检查：状态是否完整、版本是否匹配、动作是否有权限。
3. 风险检查：置信度和策略阈值是否允许自动执行，否则回退。

## 4. 工程含义

Jev 更像一个高频判断组件，而不是完整 Agent。它适合把一个大问题拆成几个窄问题，再由确定性代码组合；不适合要求长篇解释、开放式创作或隐藏多轮上下文的单次问题。[F-022](../references/article-source.md)

**本节洞察（I-1）**：决策系统的关键不是“模型会不会说话”，而是答案空间是否足够窄、状态是否足够完整、执行权限是否仍掌握在代码中。这个结论是基于官方契约的工程推导，不是厂商性能承诺。

## 自测

- 为什么看到游戏画面不代表 Jev 接收了图像？
- 什么时候应使用 Score 而不是 Noul？
- 一个合法的 Choice 结果为什么仍可能触发错误业务动作？
