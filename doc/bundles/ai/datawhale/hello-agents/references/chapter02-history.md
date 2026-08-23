---
title: 第二章 智能体发展史
type: reference
bundle: /datawhale/hello-agents
chapter: 2
part: 第一部分：智能体与语言模型基础
sources:
  - https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter2/第二章%20智能体发展史.md
---

# 第二章 智能体发展史

## 章节概要

本章回溯智能体从符号主义到LLM驱动的演进历程，理解"问题驱动"的迭代脉络——每个新范式都解决上代的核心痛点。

## 核心知识点

### 符号主义时代（1950s-1980s）
- **物理符号系统假说（PSSH）**：Newell & Simon提出，智能的本质是符号的计算与处理
  - 充分性论断：物理符号系统具备产生通用智能的手段
  - 必要性论断：通用智能系统必然是物理符号系统
- **专家系统**：知识库+推理机分离
  - 知识表示：产生式规则（IF-THEN）
  - 推理方式：正向链（数据驱动）、反向链（目标驱动）
  - 代表：MYCIN（血液感染诊断，600条规则，置信因子CF）
- **SHRDLU**：积木世界自然语言交互，早期综合性Agent

### 反应式范式（1980s-1990s）
- **包容架构（Subsumption Architecture）**：Brooks提出
- 放弃符号表示和推理，直接感知-行动映射
- 分层行为模块，高层包容低层
- 解决了符号主义的脆性问题，但丧失长远规划能力

### 多智能体与分布式AI
- **合同网协议（Contract Net Protocol）**：任务招标-投标-授予机制
- 分布式问题求解（DPS）
- 从集中式智能到分布式协作

### 强化学习智能体
- **马尔可夫决策过程（MDP）**：(S, A, P, R, γ)五元组
- **Q-Learning**：无模型强化学习算法
- **AlphaGo/AlphaGo Zero**：深度强化学习里程碑，自我对弈发现超越人类的策略

### LLM驱动的现代智能体
- 从工具调用到自主规划
- 多模态感知与行动
- 多Agent协作系统

## 演进规律
**每个新范式解决上代的核心局限，同时引入新的挑战**：
符号主义（知识获取瓶颈）→ 反应式（缺乏规划）→ 分布式（协调复杂）→ RL（样本效率低）→ LLM Agent（幻觉+可靠性）

## 相关概念
- [智能体范式与ReAct](/ai/datawhale/hello-agents/concepts/agent-paradigms-react)
- [Agentic-RL](/ai/datawhale/hello-agents/concepts/agentic-rl)
