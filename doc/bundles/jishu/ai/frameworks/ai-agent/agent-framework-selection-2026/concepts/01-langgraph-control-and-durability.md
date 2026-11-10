---
type: Concept
title: LangGraph：控制与持久化
description: 图状态机、checkpoint/resume 持久执行、HITL 中断、生产用户与“啰嗦换控制”的取舍
tags: [LangGraph, 图状态机, checkpoint, 持久执行, HITL]
generated: { by: "blog-article-to-okf-wiki", at: "2026-11-10T14:50:00+08:00" }
status: stable
stale_after: 2027-01-31
sources:
  - id: article-source
    resource: /references/article-source.md
  - id: verification
    resource: /references/verification.md
  - id: langgraph-release
    resource: https://github.com/langchain-ai/langgraph/releases/tag/1.0.0
---

# LangGraph：控制与持久化

LangGraph 是这五个框架里最“低层”的一个：它不替你决定 Agent 长什么样，而是给你一张图，让你自己画（F-016）。节点是计算，边是转移，状态是类型化的；路由是确定的，不靠提示词循环碰运气（F-017）。

## 核心机制：每个节点都是一次 checkpoint

它的标志性生产特性是**持久执行**（durable execution）：

1. 每次节点执行结束，运行时把状态写入后端存储，形成一个 checkpoint（F-018）。
2. LangGraph Platform 默认用 Postgres；本地运行用内存（F-019）。
3. 进程中途死亡，运行时重放事件历史，从最后一个 checkpoint 继续，而不是整单重跑（F-020）。

这解决了长运行 Agent 最贵的一类失败：不是“模型答错”，而是“跑到第 40 步进程没了，前面 39 步的钱和时间全废”。

## 为什么它在生产里常见

原文列出的用户是 Uber、Klarna、LinkedIn、Replit、Elastic、AppFolio（F-021）。LangChain 官方客户页确认了其中五家：LinkedIn 的 AI 招聘、Uber 的代码迁移与单测生成、Klarna 的客服、Elastic 的安全运营、AppFolio 的物业 copilot；Replit 未在该页出现，属于博文单源（F-075）。

这些场景的共同点不是“多 Agent 很酷”，而是**失败代价高、需要审计、需要人批准**。LangGraph 的 checkpoint 与 interrupt 正好对应这三件事（F-023）。

## Human-in-the-loop 是同一套状态机的延伸

因为状态在 checkpoint 里，HITL 不需要另起一套系统：在图中间暂停，等人审批，再从同一个 checkpoint 恢复。原文把它列为选型条件之一（F-023）。对支付、合规、运维变更这类流程，这往往比“多 Agent 协作”更值钱。

## 代价：啰嗦与学习曲线

原文没有回避缺点：同样的流程，LangGraph 比角色型框架写更多连接代码，学习曲线真实存在（F-022）。具体表现为：

1. 你要显式定义 state schema、节点输入输出与边条件。
2. 分支、循环、并行都要自己画出来，框架不会“猜”。
3. 调试时需要理解 checkpoint、thread、run 这些运行时概念。

换来的是可测试性与可解释性：每一步为什么跑、跑了什么、下一步去哪，都能从图与状态里读出来。

## 什么时候选它

按原文的判据（F-023）：

1. 一次失败运行很贵（长任务、批量处理、外部副作用）。
2. 需要人在关键节点审批或修正。
3. 审计会追问“第几步做了什么、为什么”。

如果只是两周内要验证一个角色协作想法，LangGraph 的接线成本可能反而拖慢你；这时 CrewAI 更合适（见 [CrewAI 与 MAF](02-crewai-speed-and-maf-enterprise-merge.md)）。

## 与本站其他知识包的关系

- 单框架源码/架构细节见 [langchain-ai/langgraph](../../../langchain-ai/langgraph/index.md)。
- 与 MAF 的图工作流对比，见 [CrewAI 与 MAF](02-crewai-speed-and-maf-enterprise-merge.md)。
- 运行时协议层（Thread/Run/Checkpoint）见 [agent-runtime-protocol](../../agent-runtime-protocol/index.md)。
