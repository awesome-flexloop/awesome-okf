---
okf_version: "0.2"
type: Concept
title: "Harnessed Agentic RL 训练范式"
description: "Agent Lightning v1.0 的核心训练范式——分离式架构通过 OpenAI 兼容 API 代理把 Agent 与 RL 训练解耦，含 rollout 机制、样本拆分、奖励统计与 Collocated Async RL 异步训练。"
tags: [agent-lightning, harnessed-agentic-rl, rollout, collocated-async-rl, agentic-rl]
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
  - id: arxiv
    url: "https://arxiv.org/abs/2608.17528"
---

# Harnessed Agentic RL 训练范式

Agent Lightning v1.0 将这类训练方式称为 **Harnessed Agentic RL** [F-014][F-047]，其本质是：**部署时使用的 harness 直接参与模型的后训练**，而非训练框架接管交互循环。

## 分离式架构：LLM endpoint proxy

Agent Lightning 采用**分离式（disaggregated）架构**，通过一个 **OpenAI 兼容 API 代理**将任意 Agent 接入 RL 训练 [F-047]。这套设计把 agent 的执行与训练彻底解耦：

- 需要模型决定下一步时，Agent 的请求发往 Agent Lightning 的 OpenAI 兼容 API 代理 [F-019]
- 代理把请求转给训练中的模型，记录实际输入/输出 token ID 与生成 token 的对数概率，并绑定到对应 rollout [F-020]
- 模型得出的动作由 harness 执行；命令报错、文件变化、测试结果等反馈由 harness 整理进下一轮上下文 [F-021]
- 训练系统记录的，是这套 Agent **实际送给模型的输入**，以及模型据此生成的回答 [F-022]

由于架构解耦，该范式（harnessed agentic RL）后续被 verl Uni-Agent、**AReaL 2.0**、slime、Polar 等框架采纳 [F-048]。

## Rollout 执行流程

在编码示例中，训练器从 SWE-smith 数据取出任务，为 Agent 创建一次执行，称为 **rollout** [F-016]：

1. 控制器启动一个 Kubernetes Job，让 mini-SWE-agent 在对应代码仓库的隔离环境中运行 [F-017]
2. Agent 读任务、查看代码、修改文件、运行命令 [F-018]
3. 需要模型决策时经上述 API 代理中转 [F-019][F-020]
4. 接入流程需要**可训练的模型、任务环境和奖励**；harness 可以沿用，模型权重由训练后端更新 [F-025]

## 奖励与样本组装

任务结束后，专属测试检查补丁是否完成修复，并把结果作为**奖励**交回系统 [F-023]。训练器收齐同一任务的多次尝试，比较奖励，把其中的模型调用组装成训练样本，**更新模型权重** [F-024]。后续任务再用更新后的模型执行。

> 奖励来自测试，测试环境就会影响模型学到什么。 —— 作者观点 [F-026]

### 样本拆分与奖励统计问题

真实 harness 会压缩上下文、启动子 Agent、重新拼装模型输入，同一次 rollout 中后一个请求未必完整接续前一个 [F-030][F-031]。即使文本没变，重新套聊天模板、重新分词也可能改变 token 边界 [F-032]。因此：

- Agent Lightning **默认只在前后调用的 token 确实连续时才合并训练序列**，接不上就另起一条，保留模型当时实际看到的输入 [F-033]
- 由于拆分会影响奖励统计，v1.0 在 **rollout 层计算优势**，并在**损失计算中处理同一 rollout 的整体权重**，让一次执行不会因样本多而被重复计权 [F-034]

**示意（非官方实验数据）**：成功那次奖励 1 被拆成三个样本、失败那次奖励 0 只有一个样本；按四个样本平均基线 0.75，按两次真实尝试平均是 0.5——成功执行只是被拆得更碎，就在基线里多占了两份权重 [F-035]。样本数量来自 harness 怎样组织上下文，不能直接代表一次尝试该有多大的训练权重。

## Collocated Async RL：异步训练机制

真实 Agent 的任务时长很不整齐——有的很快交出补丁，有的还在查文件、等命令 [F-037]。同步训练要等整批任务结束，最慢的一组会拖住模型更新 [F-038]。

v1.0 的 **Collocated Async RL** 同时保持更多任务组执行 [F-039]：

- 收齐足够多的完整组就开始一次更新；还没结束的组留到后续轮次
- 推理和更新**共用一组 GPU**；更新前网关暂停接收新的模型请求，等正在处理的请求结束，再让 GPU 更新权重，更新后恢复推理 [F-040]
- 相比同步 RL，实测带来约 **2 倍的端到端加速**；共享 GPU 池也减少了常规异步方案分别部署推理和训练的资源需求 [F-041]

### 旧策略数据处理

跨轮次任务的记录会包含更新前模型生成的数据，训练还需处理这部分**旧策略数据** [F-042]，文档提供了相应的校正配置 [F-043]。

## 延伸阅读

- 框架概览与 agent harness 见 [00-agent-lightning-v1](00-agent-lightning-v1.md)
- 实验结果与数据筛选见 [02-training-results-ecosystem](02-training-results-ecosystem.md)
- 本束核验报告见 [references/verification.md](../references/verification.md)