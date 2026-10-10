---
type: Concept
title: "配对 Holdout 协议"
description: "说明 Warmup、Holdout、Base、Loaded 与状态隔离如何组成 LIFT 的最终任务评测。"
status: stable
stale_after: 2026-12-31
generated: { by: "reference_agent", at: 2026-10-10T11:38:56+08:00 }
verified: { by: "process:seven-concepts-v", at: 2026-10-10T11:38:56+08:00 }
sources:
  - id: benchmark
    resource: "https://raw.githubusercontent.com/FeiZhuNiU-INFJA/LIFT/9d282e415c5e3b0f65b82c8758a013b269583d93/docs/benchmark-intro.md"
  - id: eval-flow
    resource: "https://raw.githubusercontent.com/FeiZhuNiU-INFJA/LIFT/9d282e415c5e3b0f65b82c8758a013b269583d93/docs/eval-flow.md"
  - id: suite
    resource: "https://raw.githubusercontent.com/FeiZhuNiU-INFJA/LIFT/9d282e415c5e3b0f65b82c8758a013b269583d93/assets/suite_requirement.md"
  - id: article-facts
    resource: "../references/article-source.md"
---

# 配对 Holdout 协议

评估“学习后是否更好”时，关键不是只跑一次 Loaded Agent，而是为加载前后建立可比较的对照。LIFT 文档把任务划分为 Warmup 与 Holdout，并在最终评估中分别运行 Base 和 Loaded 条件（F-013、F-014）。

## 评测对象

任务描述包含 `query`、`requirements` 和 `trajectory requirements` 等字段。工作 Agent 执行任务，Judge 按要求对过程或结果作出评定；官方流程中存在多轮 Agent/Judge 交互（F-016、F-017）。

Holdout 是任务划分中的保留集，但其 requirements 并非与 Warmup 完全不相交：官方 suite 文档称两者约有 75% 重合，其余为变体或矛盾要求（F-028）。因此，不能把这里的 Holdout 简化成“完全未见过任何相关要求”；它评估的是该基准所定义的保留任务及要求组合。

Warmup 阶段形成的演化状态会被保存，再用于 Loaded 条件。官方流程使用 Docker 容器和 Delta 镜像/状态管理，以控制阶段间的运行边界（F-015）。这使“加载了什么状态、在哪个环境运行”成为评测定义的一部分，而不是无关的部署细节。

## 为什么要配对

Base 与 Loaded 应面对相同的 Holdout 任务。这样观测差异才更接近“加载状态”这个变量的影响；如果两条件任务不同，题目难度差异会与加载效果混在一起。这个解释是对官方配对协议的分析，不表示已对 LIFT 代码进行独立复现。

评测设计至少要明确四件事：

1. 哪些任务属于 Warmup，哪些任务严格保留给 Holdout。
2. Base 与 Loaded 是否使用同一组 Holdout 输入及判分要求。
3. 演化产物如何保存，如何避免 Holdout 获得不应有的训练信息。
4. Agent、工具、Judge、容器镜像和任务版本如何记录。

## 解释边界

容器隔离有助于控制状态，但不自动证明环境与生产环境等价。Judge 的评分规则也会影响观测值。官方论文将 Judge 偏差和环境保真度列为限制（F-022），因此结果应绑定到具体任务、Judge 和执行环境。

详细字段和来源定位见[事实索引](../references/article-source.md)与[核验报告](../references/verification.md)。
