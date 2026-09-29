---
type: concept
title: "Agent 智能体"
bundle: /datawhale/happy-llm
description: "以 LLM 为推理核心，通过 ReAct 范式调用工具、多轮交互完成复杂任务的自主智能体，是 LLM 从问答走向行动的关键"
sources: https://github.com/datawhalechina/happy-llm/blob/main/docs/chapter7/第七章%20大模型应用.md
related:
  - /datawhale/happy-llm/concepts/rag-retrieval-augmented-generation
  - /datawhale/happy-llm/concepts/grpo-reinforcement-learning
  - /datawhale/happy-llm/concepts/model-training
tags: [agent, react, tool-calling, planning, autonomous]
status: stable
---

# Agent 智能体

## 核心理解

Agent（智能体）是以 LLM 为"大脑"，能够感知环境、自主规划、调用工具并执行行动以完成复杂任务的系统。如果说 RAG 让 LLM"查资料后回答"，Agent 则让 LLM"自己决定做什么并动手做"。第七章通过 TinyAgent 的实现，展示了 Agent 的核心架构和工具调用机制。

LLM 的指令遵循和逐步推理能力（第四章）是 Agent 的基础——Agent 将复杂任务拆解为多步推理，在每一步决定是否调用工具、调用哪个工具、传入什么参数，再根据工具返回结果继续推理，直到得出最终答案。

## Agent 的工作原理

一个典型 Agent 的运行循环：

```
用户目标
  ↓
┌─────────────────────────────┐
│  LLM 推理（Thought）         │
│  "我需要搜索 X 信息"          │
└──────────┬──────────────────┘
           ↓
┌─────────────────────────────┐
│  工具调用（Action）          │
│  search("X") → Observation  │
└──────────┬──────────────────┘
           ↓
┌─────────────────────────────┐
│  观察结果（Observation）     │
│  "搜索结果显示..."           │
└──────────┬──────────────────┘
           ↓
   需要更多工具？──是──→ 回到 LLM 推理
           ↓ 否
┌─────────────────────────────┐
│  最终回答（Final Answer）    │
└─────────────────────────────┘
```

## ReAct 范式

ReAct（Reasoning + Acting）是 Agent 最经典的推理框架，将**推理（Thought）**和**行动（Action）**交替进行：

- **Thought（思考）**：LLM 分析当前状态，决定下一步需要做什么
- **Action（行动）**：选择并调用一个工具（搜索、计算、代码执行等）
- **Observation（观察）**：获取工具返回结果
- 循环直到 LLM 判断信息足够，给出 **Final Answer**

ReAct 的关键洞察是：LLM 的链式推理（CoT）提供规划能力，工具调用提供行动能力，两者结合让模型能处理需要外部信息或实时交互的任务。

## Agent 核心组件

TinyAgent 的代码结构展示了最小 Agent 架构：

| 文件 | 职责 |
|------|------|
| `src/core.py` | Agent 核心：推理循环、Prompt 组装、响应解析、工具调度 |
| `src/tools.py` | 工具定义：工具名称、描述、参数 schema、执行函数 |
| `src/utils.py` | 工具函数：LLM 调用、输出解析等 |
| `demo.py` | 命令行演示 |
| `web_demo.py` | Streamlit Web 界面 |

### 工具（Tools）

工具是 Agent 与外部世界交互的接口。每个工具需要定义：

- **名称**：模型通过名称选择工具
- **描述**：告诉模型这个工具做什么、何时使用
- **参数**：工具需要的输入及其类型
- **执行函数**：实际执行操作并返回结果

常见工具类型：搜索引擎、代码解释器、API 调用、数据库查询、文件操作、计算器等。

### Agent 核心循环

```python
while not done:
    response = llm.chat(messages)  # LLM 推理
    action = parse_action(response)  # 解析工具调用
    if action.is_final:
        return action.answer
    result = tools.execute(action.name, action.args)  # 执行工具
    messages.add(result)  # 将观察结果加入上下文
```

## Agent 与 RAG 的关系

RAG 可以视为 Agent 的一种特例（工具 = 向量检索），但两者的抽象层次不同：

| 维度 | RAG | Agent |
|------|-----|-------|
| 决策方式 | 固定流程：检索→生成 | LLM 自主决定：是否用工具、用哪个、何时停止 |
| 工具数量 | 单一（检索） | 多个（搜索、代码、API 等） |
| 交互轮次 | 通常一轮 | 多轮推理-行动循环 |
| 复杂度 | 较低 | 较高 |
| 适用场景 | 知识问答、文档查询 | 复杂任务规划、多步骤执行 |

## 从 Agent 到 Agentic RL

第七章的 Agent 基于 SFT 模型 + Prompt Engineering 实现，工具调用能力来自指令微调。但当 Agent 进入搜索、代码执行等真实环境后，仅靠监督数据难以覆盖所有交互轨迹。

第八章的 **Search-R1** 和 **ReTool** 将 Agent 与强化学习结合（Agentic RL）：

- **Search-R1**：搜索引擎作为环境，模型通过 RL 学习多轮搜索策略
- **ReTool**：代码解释器作为环境，模型通过 RL 学习生成和执行代码

模型在环境中尝试动作，根据最终结果（答案是否正确、代码是否运行成功）获得奖励，通过 GRPO 等算法更新策略——这是从"教模型怎么做"到"让模型自己学会做"的跃迁。

## 在 Happy-LLM 中的位置

第七章 7.3 节讲解 Agent，是应用层章节的最后一个主题。Agent 建立在 LLM 的指令遵循和逐步推理能力（第四章）之上，与 RAG（7.2）形成"知识增强→行动增强"的递进。第八章的 Agentic RL 则进一步将 Agent 训练为可通过强化学习自主改进的系统，形成全书的完整闭环。

## 延伸阅读

- [RAG 检索增强生成](rag-retrieval-augmented-generation.md)——Agent 的知识检索基础
- [GRPO 强化学习](grpo-reinforcement-learning.md)——Agentic RL 的训练算法
- [TinyAgent 智能体工具调用示例](../examples/agent-tinyagent.md)——第七章 Agent 代码实践
