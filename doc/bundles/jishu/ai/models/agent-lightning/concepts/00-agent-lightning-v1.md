---
okf_version: "0.2"
type: Concept
title: "Agent Lightning v1.0 概览：把真实 Agent 接进强化学习"
description: "微软开源 Agent Lightning v1.0——面向 AI Agent 的强化学习框架，约 3,500 行训练控制层，通过 agent harness 让部署侧工具调用与上下文编排直接参与 RL 训练。"
tags: [agent-lightning, agentic-rl, harness, rl, 微软开源]
generated: { by: "reference_agent/deepseek-v4", at: "2026-10-10" }
verified:
  - { by: "process:seven-concepts-v", at: "2026-10-10" }
status: stable
stale_after: 2026-12-31
sources:
  - id: blog
    url: "https://mp.weixin.qq.com/s/j9m0xBbqGrFl5WVeKHq1kg"
  - id: official-blog
    url: "https://www.microsoft.com/en-us/research/blog/agent-lightning-v1-0-a-3500-line-lightweight-agentic-rl-framework-for-training-agents-with-real-harnesses/"
  - id: github
    url: "https://github.com/microsoft/agent-lightning"
---

# Agent Lightning v1.0 概览：把真实 Agent 接进强化学习

微软在 2026 年开源了 **Agent Lightning v1.0**，一套面向 AI Agent 的强化学习（RL）训练框架 [F-001]。它的定位是：给**已经搭好 Agent、希望继续训练底层模型的开发者**使用——保留现有的工具调用、上下文管理和任务执行流程，用实际任务中的执行记录与结果反馈训练模型，减少为训练另外重写一套 Agent 的工作 [F-002][F-003]。

## 核心概念：agent harness

Agent Lightning 的核心思想围绕 **agent harness** 展开。负责执行与上下文安排的外层程序称为 harness，它决定模型能用什么工具、下一轮能看到哪些信息 [F-005]。

> 一个编码 Agent 能否修好 bug，既取决于模型，也取决于这套流程。 —— 作者观点 [F-006]

过去不少 Agent 强化学习系统要求训练框架接管交互循环，开发者得在里面重新实现调用模型、执行动作、返回结果的逻辑 [F-007]。v1.0 的核心改进是**将训练接到现成 harness 的模型接口上，省去重建这一段交互循环** [F-008]。

## 发布与时间线

- **2026 年 8 月**：Agent Lightning v1.0 及相关技术报告公开 [F-013]；在学术报告口径下，v1.0 于 2026-08 在 MIT license 下发布 [F-049]。
- **2026 年 10 月 7 日**：微软亚洲研究院博客正式介绍这套重构后的框架 [F-012]。
- **开源仓库**：[github.com/microsoft/agent-lightning](https://github.com/microsoft/agent-lightning) [F-050]
- **技术报告**：[arXiv 2608.17528](https://arxiv.org/abs/2608.17528)「Agent Lightning v1.0: Towards Harnessed Agentic RL」[F-051]

## 轻量定位与运行方式

- v1.0 约 **3,500 行代码**实现的是**训练控制层**，推理和权重更新仍依赖后端 [F-044]。
- 仓库提供**本地进程**和 **Kubernetes** 两种运行方式，以及数据准备、环境隔离、训练脚本和监控入口 [F-045]。
- 硬件需求（博文所述，待复核）：最小 Calc-X 示例可用一张 A100；公开的 Qwen3.5 编码示例使用四张 B200 [F-046]。

## 延伸阅读

- 训练范式「Harnessed Agentic RL」的完整机制见 [01-harnessed-agentic-rl](01-harnessed-agentic-rl.md)
- 实验结果、数据筛选与生态影响见 [02-training-results-ecosystem](02-training-results-ecosystem.md)
- 本束信源与核验详情见 [references/](../references/index.md)