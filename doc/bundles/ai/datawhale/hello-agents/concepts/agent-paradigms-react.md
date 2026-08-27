---
title: 智能体范式与ReAct
type: concept
bundle: /datawhale/hello-agents
related:
  - /datawhale/hello-agents/concepts/multi-agent-collaboration
  - /datawhale/hello-agents/concepts/agent-framework-development
  - /datawhale/hello-agents/references/chapter04-classic-paradigms
sources:
  - https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter4/第四章%20智能体经典范式构建.md
---

# 智能体范式与ReAct

智能体范式（Agent Paradigm）是组织LLM"思考"与"行动"过程的架构模式。Hello-Agents教程重点实现了三种最具代表性的经典范式：**ReAct**、**Plan-and-Solve** 和 **Reflection**。

## ReAct：推理与行动协同

ReAct（Reasoning and Acting）由Shunyu Yao于2022年提出，其核心思想是模仿人类解决问题的方式，将**推理（Reasoning）**与**行动（Acting）**显式结合，形成"思考-行动-观察"的循环。

### 工作流程

```
Thought（思考）→ Action（行动）→ Observation（观察）→ Thought → ... → Final Answer
```

- **Thought**：智能体的"内心独白"，分析当前情况、分解任务、制定下一步计划或反思上一步结果
- **Action**：决定采取的具体动作，通常是调用外部工具，如 `Search['华为最新款手机']`
- **Observation**：执行Action后从外部工具返回的结果

智能体不断重复这个循环，将新观察追加到历史记录中形成增长的上下文，直到在Thought中认为已找到最终答案。

### ReAct的协同效应

在ReAct诞生之前，主流方法分为两类：
- **纯思考型**（如Chain-of-Thought）：能进行复杂逻辑推理，但无法与外部世界交互，容易产生事实幻觉
- **纯行动型**：直接输出动作，但缺乏规划和纠错能力

ReAct的巧妙之处在于认识到**思考与行动相辅相成**：推理使行动更具目的性，行动为推理提供事实依据。

## Plan-and-Solve：三思而后行

Plan-and-Solve范式采用"先规划后执行"的策略：
1. **规划阶段**：智能体首先生成一个完整的行动计划，将复杂任务分解为子任务列表
2. **执行阶段**：严格按照计划逐步执行每个子任务

与ReAct的交错式不同，Plan-and-Solve在行动前完成全部规划，适合流程相对固定、可预先分解的任务。其优势在于全局视野，但在动态环境中可能缺乏灵活性。

## Reflection：自我批判与修正

Reflection范式赋予智能体"反思"能力：
1. 生成初始答案或方案
2. 进行自我批判，识别问题和不足
3. 基于批判意见修正和优化
4. 重复反思-改进循环直到满足质量要求

这种范式特别适合需要高质量输出的场景，如代码生成、文案写作等。

## 三种范式对比

| 维度 | ReAct | Plan-and-Solve | Reflection |
|------|-------|----------------|------------|
| 思考-行动关系 | 交错进行 | 先规划后执行 | 先生成后反思 |
| 灵活性 | 高，可动态调整 | 中，按计划执行 | 中高，迭代修正 |
| 适用场景 | 信息检索、动态决策 | 流程固定的复杂任务 | 高质量内容生成 |
| 成本 | 中等（多轮工具调用） | 较低（一次规划） | 较高（多轮自我评估） |

## 从零实现的价值

教程强调亲手实现范式的重要性：
1. **理解设计机制**：直接使用高度抽象的框架不利于理解背后的运行原理
2. **暴露工程挑战**：框架处理了模型输出解析、工具调用失败重试、死循环防护等问题，亲手处理这些问题是培养系统设计能力的直接方式
3. **从使用者到创造者**：掌握设计原理后，当标准组件无法满足复杂需求时，具备深度定制能力

## 相关阅读

- 第四章 智能体经典范式构建
- Agent框架开发
- 多Agent协作
