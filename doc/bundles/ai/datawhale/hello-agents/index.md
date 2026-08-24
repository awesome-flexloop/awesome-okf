---
title: Hello-Agents 从零开始构建智能体
type: index
bundle: /datawhale/hello-agents
description: Datawhale社区系统性智能体学习教程，从基础理论到实际应用，全面掌握智能体系统的设计与实现。涵盖Agent经典范式（ReAct/Plan-and-Solve/Reflection）、低代码平台（Coze/Dify/n8n）、框架开发（AutoGen/AgentScope/CAMEL/LangGraph）、自研HelloAgents框架、记忆与检索系统、上下文工程、通信协议（MCP/A2A/ANP）、Agentic-RL训练（SFT/GRPO）、性能评估（BFCL/GAIA）及综合实战案例。
concepts:
  - /datawhale/hello-agents/concepts/agent-paradigms-react
  - /datawhale/hello-agents/concepts/agent-framework-development
  - /datawhale/hello-agents/concepts/memory-systems
  - /datawhale/hello-agents/concepts/context-engineering
  - /datawhale/hello-agents/concepts/communication-protocols
  - /datawhale/hello-agents/concepts/multi-agent-collaboration
  - /datawhale/hello-agents/concepts/agentic-rl
  - /datawhale/hello-agents/concepts/evaluation-methods
references:
  - /datawhale/hello-agents/references/chapter01-introduction
  - /datawhale/hello-agents/references/chapter02-history
  - /datawhale/hello-agents/references/chapter03-llm-fundamentals
  - /datawhale/hello-agents/references/chapter04-classic-paradigms
  - /datawhale/hello-agents/references/chapter05-lowcode-platforms
  - /datawhale/hello-agents/references/chapter06-framework-practice
  - /datawhale/hello-agents/references/chapter07-build-framework
  - /datawhale/hello-agents/references/chapter08-memory-retrieval
  - /datawhale/hello-agents/references/chapter09-context-engineering
  - /datawhale/hello-agents/references/chapter10-communication-protocols
  - /datawhale/hello-agents/references/chapter11-agentic-rl
  - /datawhale/hello-agents/references/chapter12-evaluation
  - /datawhale/hello-agents/references/chapter13-travel-assistant
  - /datawhale/hello-agents/references/chapter14-deep-research
  - /datawhale/hello-agents/references/chapter15-cyber-town
  - /datawhale/hello-agents/references/chapter16-graduation
  - /datawhale/hello-agents/references/extra-chapters
examples:
  - /datawhale/hello-agents/examples/react-implementation
  - /datawhale/hello-agents/examples/helloagents-framework
  - /datawhale/hello-agents/examples/mcp-integration
  - /datawhale/hello-agents/examples/agentic-rl-training
sources:
  - https://github.com/datawhalechina/hello-agents
---

# Hello-Agents：从零开始构建智能体

> **Datawhale 社区系统性智能体学习教程** | 从基础理论到实际应用，全面掌握智能体系统的设计与实现

Hello-Agents 是一本理论与实战并重的智能体系统构建指南。教程穿透框架表象，从智能体核心原理出发，深入经典范式，最终引导读者亲手构建多智能体应用。

## 知识地图

教程分为五大部分，共16章，另含13篇社区精选文章：

```
第一部分：智能体与语言模型基础（第1-3章）
  └─ 智能体定义 → 发展史 → LLM基础

第二部分：构建你的大语言模型智能体（第4-7章）
  └─ ReAct/Plan-Solve/Reflection → 低代码平台 → 主流框架 → 自建HelloAgents

第三部分：高级知识扩展（第8-12章）
  └─ 记忆与RAG → 上下文工程 → 通信协议(MCP/A2A/ANP) → Agentic-RL → 评估

第四部分：综合案例进阶（第13-15章）
  └─ 智能旅行助手 → 深度研究Agent → 赛博小镇

第五部分：毕业设计及未来展望（第16章）
  └─ 开源共创毕业设计
```

## 核心概念

| 概念 | 说明 |
|------|------|
| [智能体范式与ReAct](/ai/datawhale/hello-agents/concepts/agent-paradigms-react) | ReAct、Plan-and-Solve、Reflection三大经典范式的原理与实现 |
| [Agent框架开发](/ai/datawhale/hello-agents/concepts/agent-framework-development) | 从手动实现到框架抽象，AutoGen/AgentScope/CAMEL/LangGraph对比与HelloAgents自建 |
| [记忆系统](/ai/datawhale/hello-agents/concepts/memory-systems) | 四层记忆架构（工作/情景/语义/感知）与RAG检索增强生成 |
| [上下文工程](/ai/datawhale/hello-agents/concepts/context-engineering) | GSSC流水线、上下文腐蚀、JIT检索、长时程任务管理 |
| [通信协议](/ai/datawhale/hello-agents/concepts/communication-protocols) | MCP（Agent-工具）、A2A（Agent-Agent）、ANP（Agent网络）三层协议栈 |
| [多Agent协作](/ai/datawhale/hello-agents/concepts/multi-agent-collaboration) | 对话驱动、角色扮演、图结构工作流等协作模式 |
| [Agentic-RL](/ai/datawhale/hello-agents/concepts/agentic-rl) | 从SFT到GRPO，将LLM作为可学习策略的多步决策优化 |
| [评估方法](/ai/datawhale/hello-agents/concepts/evaluation-methods) | BFCL工具调用评估、GAIA通用能力评估、LLM Judge与数据生成质量评估 |

## 实战示例

- [ReAct范式从零实现](/ai/datawhale/hello-agents/examples/react-implementation)：Thought→Action→Observation循环的完整代码
- [HelloAgents框架架构](/ai/datawhale/hello-agents/examples/helloagents-framework)："万物皆工具"的轻量级框架设计
- [MCP协议集成](/ai/datawhale/hello-agents/examples/mcp-integration)：天气MCP服务器与多Agent文档助手
- [Agentic-RL训练Pipeline](/ai/datawhale/hello-agents/examples/agentic-rl-training)：SFT+GRPO全流程训练代码

## 配套资源

- **开源框架**: [HelloAgents](https://github.com/jjyaoao/helloagents) — 基于OpenAI原生API从零构建的教学框架
- **代码示例**: `code/` 目录包含第10-12章全部可运行代码
- **共创项目**: `Co-creation-projects/` 目录包含40+社区毕业设计
- **社区精选**: `Extra-Chapter/` 目录包含13篇扩展文章
- **在线阅读**: [国外访问](https://datawhalechina.github.io/hello-agents/) | [国内加速](https://hello-agents.datawhale.cc)

## 引用

```bibtex
@misc{hello_agents2025,
  title  = {Hello-Agents: Building an AI Agent from Scratch},
  author = {Sizhou Chen and Tao Sun and Shufan Jiang and Peilin Huang and Xinmin Zeng and Hao Hu and Xinzhong Zhu and all Hello-Agents contributors},
  year   = {2025},
  url    = {https://github.com/datawhalechina/Hello-Agents},
  note   = {GitHub repository}
}
```

```{toctree}
:hidden:

concepts/agent-framework-development
concepts/agent-paradigms-react
concepts/agentic-rl
concepts/communication-protocols
concepts/context-engineering
concepts/evaluation-methods
concepts/memory-systems
concepts/multi-agent-collaboration
examples/agentic-rl-training
examples/helloagents-framework
examples/mcp-integration
examples/react-implementation
references/chapter01-introduction
references/chapter02-history
references/chapter03-llm-fundamentals
references/chapter04-classic-paradigms
references/chapter05-lowcode-platforms
references/chapter06-framework-practice
references/chapter07-build-framework
references/chapter08-memory-retrieval
references/chapter09-context-engineering
references/chapter10-communication-protocols
references/chapter11-agentic-rl
references/chapter12-evaluation
references/chapter13-travel-assistant
references/chapter14-deep-research
references/chapter15-cyber-town
references/chapter16-graduation
references/extra-chapters
spec/facts
spec/insights
log
```
