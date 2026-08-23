---
title: Agent Harness——从框架到运行时外壳
type: concept
bundle: /datawhale/deepagents-in-action
description: Deep Agents 的核心定位——不是又一个 Agent 框架，而是构建在 LangChain/LangGraph 之上的运行时外壳，提供虚拟文件系统、任务规划、子Agent编排、记忆、权限、沙箱、HITL、MCP等生产级横切能力。
related:
  - /datawhale/deepagents-in-action/concepts/virtual-filesystem-context-engineering
  - /datawhale/deepagents-in-action/references/readme-source
sources:
  - id: github-repo
    resource: /references/readme-source.md
    title: deepagents-in-action GitHub 仓库
---

# Agent Harness——从框架到运行时外壳

Deep Agents 的核心命题在课程第1章标题中即被点明："从 Agent Framework 到 Agent Harness"。理解这一定位跃迁，是掌握整个 Deep Agents 生态的认知前提。

## 三层边界

课程第1章的实验目标是让学习者从最小 `create_deep_agent` 项目中识别三层边界：

| 层次 | 职责 | 代表 |
|------|------|------|
| Runtime | 模型推理、工具调用的底层运行时 | LLM API、模型服务 |
| Framework | Agent 执行循环、状态图编排 | LangChain、LangGraph |
| Harness | 生产级横切能力外壳 | Deep Agents |

Harness 层不重新发明 Agent 执行循环，而是包裹在 Framework 之外，解决"Agent 写完之后怎么办"的工程问题。

## Harness 层的能力域

课程14章覆盖的能力几乎全部属于 Harness 层横切关注点：

- **上下文工程**：虚拟文件系统（第3章）作为 Context Engineering 的核心底座
- **任务管理**：write_todos 任务规划与分解（第4章）
- **协作编排**：子Agent委派（第5章）、异步子Agent（第6章）
- **能力复用**：Skills 可复用能力包（第7章）
- **状态持久化**：长期记忆与 namespace（第8章）
- **安全管控**：HITL 中断（第9章）、沙箱执行（第10章）、文件系统权限（第11章）
- **生态扩展**：MCP 标准协议工具发现（第12章）
- **质量闭环**：Grading Rubrics 评分量规自我迭代（第13章）
- **可观测性**：Event Streaming v3 流式传输（第14章）

## 设计哲学

### 生产就绪而非算法演示

副标题"系统构建生产级 AI Agent"中的"生产级"是关键词。Framework 教程关注"Agent 能不能跑"，Harness 关注：
- 上下文如何持久化与隔离？
- 副作用如何管控与审批？
- 多Agent如何协作而不互相污染？
- 输出如何按验收标准自我修正？
- 运行过程如何实时观测？

### 分层协作而非竞争

Deep Agents 与 LangChain/LangGraph 不是竞品关系。LangGraph 提供底层状态图编排，Deep Agents 在其上预置生产级模式。版本要求中 `deepagents>=0.5` 的各项功能（FilesystemPermission、interrupt、RubricMiddleware 等）均为 Harness 层增量。

### 模板化交付

Harness 能力通过 AgentSeek 模板系统交付为可运行项目脚手架，而非抽象的库API。7种模板对应不同能力组合，学习者通过增量修改理解每层能力的作用。

## 学习要点

1. 不要将 Deep Agents 视为"另一个 Agent 框架"，它是 LangGraph 的生产级外壳
2. 每学一章，问自己："这为 Framework 补充了什么生产能力？"
3. 评估其他 Agent 方案时，可用本课程14章能力域作为生产就绪度检查清单
4. 理解 Harness 边界后，能更清晰地判断何时用 Deep Agents、何时直接用 LangGraph

## 相关概念

- [虚拟文件系统与 Context Engineering](./virtual-filesystem-context-engineering.md)——Harness 层最核心的上下文工程底座
- [信源登记](../references/readme-source.md)——项目官方仓库与版本要求
