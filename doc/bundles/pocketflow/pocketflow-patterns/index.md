---
title: PocketFlow 设计模式
type: index
bundle: pocketflow-patterns
version: 0.1.0
description: |
  基于 PocketFlow cookbook 40+ 示例提炼的 6 大设计模式：Agent 循环、
  多智能体协作、RAG 检索增强、MapReduce 分治、Workflow/HITL 人机交互、
  Tool Use 工具调用。每种模式包含流程图、节点结构和代码骨架。
concepts:
  - agent-loop: Agent 循环模式（ReAct循环）
  - multi-agent: 多智能体协作模式
  - rag: RAG 检索增强生成模式
  - map-reduce: MapReduce 分治模式
  - workflow-hitl: 工作流与人机交互模式
  - tool-use: 工具调用模式
references:
  - pattern-catalog: 模式目录与cookbook映射
examples:
  - agent-research: 研究Agent完整示例
  - rag-qa: RAG问答完整示例
---

# PocketFlow 设计模式

基于 PocketFlow 官方 cookbook 的 40+ 示例应用，提炼出 6 种核心设计模式。每种模式都展示了如何用 Node + Flow 的极简抽象构建复杂的 LLM 应用。

## 模式一览

| 模式 | 核心结构 | 典型Cookbook | 适用场景 |
|------|---------|-------------|---------|
| [Agent循环](concepts/agent-loop.md) | 决策→行动→观察→循环 | pocketflow-agent, pocketflow-deep-research | 自主决策、工具调用循环 |
| [多智能体](concepts/multi-agent.md) | 多Flow并发+队列通信 | pocketflow-multi-agent, pocketflow-supervisor, pocketflow-debate | 角色分工、对抗/协作、监督 |
| [RAG](concepts/rag.md) | 离线索引+在线检索→生成 | pocketflow-rag, pocketflow-agentic-rag, pocketflow-chat-memory | 文档问答、知识库 |
| [MapReduce](concepts/map-reduce.md) | BatchNode拆分→处理→汇总 | pocketflow-map-reduce, pocketflow-batch-node, pocketflow-nested-batch | 批量文档处理、分块摘要 |
| [Workflow/HITL](concepts/workflow-hitl.md) | 线性流+条件分支+人工节点 | pocketflow-cli-hitl, pocketflow-gradio-hitl, pocketflow-fastapi-hitl | 表单填写、审批流、交互式对话 |
| [Tool Use](concepts/tool-use.md) | 决策节点→工具节点→回到决策 | pocketflow-code-generator, pocketflow-google-calendar, pocketflow-mcp | 代码执行、API调用、外部服务 |

## 快速导航

- [概念文档](concepts/) — 6种模式的详细说明
- [API参考](references/) — 模式目录与cookbook映射
- [示例代码](examples/) — 完整可运行示例
