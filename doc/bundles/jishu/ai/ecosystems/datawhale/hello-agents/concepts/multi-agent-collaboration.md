---
title: 多Agent协作
type: concept
bundle: /datawhale/hello-agents
related:
  - /datawhale/hello-agents/concepts/communication-protocols
  - /datawhale/hello-agents/concepts/agent-framework-development
  - /datawhale/hello-agents/concepts/agent-paradigms-react
  - /datawhale/hello-agents/references/chapter06-framework-practice
sources:
  - https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter6/第六章%20框架开发实践.md
---

# 多Agent协作

多智能体系统（Multi-Agent System, MAS）由多个Agent通过分工、协作甚至辩论共同完成宏大目标，被视为释放LLM全部潜能、解决真实世界复杂问题的关键。不同框架提供了不同的协作范式。

## 为何需要多Agent

单Agent在面对复杂任务时存在局限：
- **上下文窗口限制**：单一Agent需要处理所有信息，容易上下文腐蚀
- **角色冲突**：同一Agent既当运动员又当裁判员（如写代码又审代码）
- **能力边界**：不同任务需要不同专业知识和工具集
- **并行需求**：某些子任务可以并行执行以提高效率

多Agent通过**分工**、**专业化**和**相互校验**来应对这些挑战。

## 主流协作范式

### 1. 对话驱动协作（AutoGen模式）

将多Agent系统抽象为多个"可对话"Agent组成的群聊：
- 定义不同角色（Coder、ProductManager、Tester等）
- 设定交互规则（如Coder写完代码后Tester自动接管）
- 任务解决过程 = Agent在群聊中自动化消息传递、对话、协作、迭代

**典型机制**：`RoundRobinGroupChat`轮询群聊，按预定义顺序依次发言，适合流程固定的任务。

**核心组件**：
- `AssistantAgent`：LLM驱动的任务解决者
- `UserProxyAgent`：用户代言人和代码/工具执行器
- 清晰区分"思考"（Assistant）与"行动"（UserProxy）

### 2. 角色扮演协作（CAMEL模式）

只需为两个Agent设定角色和共同任务目标，它们在**初始提示（Inception Prompting）**引导下自主多轮对话：

- AI研究员 ↔ Python程序员
- 任务设定者 ↔ 任务执行者
- 相互启发、相互配合，共同完成任务

**优势**：极大降低多Agent对话流程设计复杂度，Agent自主决定对话内容和方向。

### 3. 图结构工作流（LangGraph模式）

将执行流程建模为**有向图**：
- **节点（Node）**：每个操作步骤（调用LLM、执行工具等）
- **边（Edge）**：定义节点间跳转逻辑，支持条件分支
- **循环（Cycles）**：天然支持迭代修正

**优势**：
- 可视化复杂控制流
- 条件分支和循环使Reflection等迭代工作流直观实现
- 适合需要精确控制执行路径的场景

### 4. 消息传递协作（AgentScope模式）

基于消息传递机制构建多Agent通信网络：
- Agent间通过结构化消息通信
- 支持分布式部署
- 工程化程度高，适合大规模系统

## 协作模式分类

| 模式 | 控制方式 | 灵活性 | 可预测性 | 典型框架 |
|------|---------|--------|---------|---------|
| 顺序轮询 | 预定义顺序 | 低 | 高 | AutoGen RoundRobin |
| 自由对话 | Agent自主决定 | 高 | 低 | CAMEL |
| 图结构控制 | 显式条件边 | 中 | 高 | LangGraph |
| 消息传递 | 事件驱动 | 中高 | 中 | AgentScope |

## 子代理架构与上下文隔离

多Agent协作的一个重要工程价值是**上下文隔离**：
- 主代理负责高层规划与综合
- 专长子代理在"干净的上下文窗口"中各自深挖
- 子代理仅回传凝练摘要（1,000-2,000 tokens）
- 庞杂的搜索上下文留在子代理内部，主代理专注整合与推理

这种模式在复杂研究任务上相较单Agent基线具有显著优势，是上下文工程中应对长时程任务的核心手段之一。

## 协议层支撑

多Agent协作需要通信协议支撑：
- **A2A协议**提供Agent间点对点对等通信标准
- **MCP协议**让Agent团队共享工具和资源访问能力
- **ANP协议**支持大规模Agent网络中的服务发现

详见通信协议概念文档。

## 综合案例中的多Agent

教程实战章节展示了多Agent协作的真实应用：
- **智能旅行助手**：4个专门Agent（景点搜索、天气查询、酒店推荐、行程规划）通过MCP协作
- **深度研究助手**：3个Agent（TODO Planner、Task Summarizer、Report Writer）+ 2工具（SearchTool、NoteTool）
- **赛博小镇**：每个NPC是独立SimpleAgent实例，拥有独立记忆和状态

## 相关阅读

- 第六章 框架开发实践
- 通信协议
- 智能体范式与ReAct
- 上下文工程
