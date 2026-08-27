---
title: TinyAgent 智能体
type: concept
bundle: /datawhale/tiny-universe
related:
  - /datawhale/tiny-universe/concepts/white-box-philosophy
  - /datawhale/tiny-universe/concepts/tiny-rag
  - /datawhale/tiny-universe/concepts/tiny-llm
sources:
  - https://github.com/datawhalechina/tiny-universe
---

# TinyAgent 智能体

## 定位

TinyAgent 是 tiny-universe 主体部分的第六个模块，**基于 ReAct 方式手动制作一个最小的 Agent 结构**。项目坦承"其实更多的是调用工具"，核心目标是让读者通过手写 Agent 理解其构成与运作，为后续搭建个性化 Agent 系统奠定基础。

## 解决的问题

大模型能力强大，但在逻辑推理、现实事件、垂直领域仍存在薄弱环节。通过工具为大模型赋能，使其与现实世界对齐颗粒度，是大模型应用的重要方向。Agent 将 LLM 打造为能自主理解、规划决策、执行复杂任务的智能体，给予其专业工具，使大模型走入现实应用。

## 核心技术点

### ReAct 结构

TinyAgent 采用 ReAct（Reasoning + Acting）范式，核心循环为：

1. **思考（Thought）**：LLM 分析当前问题与已有信息
2. **行动（Action）**：选择并调用合适的工具
3. **观察（Observation）**：接收工具返回结果
4. 重复上述循环，直至生成最终答案

项目手工实现这一循环，而非使用 Agent 框架封装好的执行器。

### 工具调用

模块重点在于工具调用机制：如何定义工具、如何将工具描述注入 prompt、如何解析 LLM 输出中的工具调用请求、如何将工具返回结果送回 LLM。

### 后续演进

README 提到计划在暑假将 ReAct 结构修改为 SOP（Standard Operating Procedure）结构，体现了 Agent 架构从动态推理到流程化执行的探索方向。

## 白盒特征

- **最小结构**：不追求完整 Agent 框架，只保留 ReAct 闭环
- **手写解析**：手工实现 LLM 输出解析与工具调度，不依赖框架的 agent executor
- **可扩展**：理解最小结构后，可自由替换为 SOP、Plan-and-Execute 等其他架构

## 在项目中的位置

TinyAgent 位于"增强系统层"的顶端，建立在 TinyRAG 的检索能力与 TinyLLM 的生成能力之上，是大模型从"被动回答"走向"主动行动"的关键环节。TinyEval 则为 Agent 等系统的能力评估提供方法。

项目 README 中配有 ReAct 架构图（`./content/TinyAgent/images/React.png`）。

## 学习资源

- Datawhale 视频号搜索"动手搭建一个最小 Agent 系统"
- README 暂无录播链接

## 延伸

- 检索基础：TinyRAG
- 模型底座：TinyLLM
- 方法论根源：白盒构建理念
