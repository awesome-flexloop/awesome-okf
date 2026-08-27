---
title: 第十一章 Agentic-RL
type: reference
bundle: /datawhale/hello-agents
chapter: 11
part: 第三部分：高级知识扩展
sources:
  - https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter11/第十一章%20Agentic-RL.md
---

# 第十一章 Agentic-RL

## 章节概要

本章从LLM训练基础出发，深入Agentic RL范式——将LLM作为可学习策略嵌入序贯决策循环，通过SFT和GRPO训练具备推理、工具使用等能力的智能体。

## 核心知识点

### LLM训练全景
**预训练阶段**：
- 海量文本，自监督学习
- 因果语言建模（下一个词预测）
- 学习语法、语义、世界知识、基础推理

**后训练三步骤**：
1. **SFT（监督微调）**：(prompt, completion)对，学习指令遵循
2. **RM（奖励建模）**：偏好对比数据（chosen vs rejected），学习人类偏好
3. **RL微调**：PPO算法，最大化奖励+KL散度约束
   - RLHF：人类反馈
   - RLAIF：AI反馈（成本低，效果接近RLHF）

### Agentic RL vs PBRFT

PBRFT（Preference-Based RL Fine-Tuning）优化单轮对话质量，Agentic RL优化多步任务完成度：

| 维度 | PBRFT | Agentic RL |
|------|-------|------------|
| 状态 | 仅prompt | prompt+历史观察 |
| 时间跨度 | T=1 | T≫1 |
| 行动 | 仅文本生成 | 文本+工具调用+环境操作 |
| 奖励 | 单步/任务结束 | 多步/可中间反馈 |
| 目标 | 单步期望奖励 | 累积折扣奖励 |

### 六大核心能力
1. **推理**：通过试错学习有效推理策略，发现新推理路径
2. **工具使用**：何时用、选哪个、如何组合工具
3. **记忆**：学习记忆管理策略（记住/更新/遗忘）
4. **规划**：动态规划行动序列，权衡长短收益
5. **自我改进**：识别错误、分析原因、调整策略
6. **感知**：多模态理解、视觉推理与规划

### GRPO（群组相对策略优化）
- **创新**：去除critic网络，用群组内相对奖励作为优势估计
- **流程**：对每个问题采样一组（8个）回答，计算组内相对优势
- **价值**：降低约50%显存占用，使中小团队可训练

### SFT训练
- 让模型学会Agent输出格式（Thought/Action/Observation）
- 数据量较小但质量要求高
- 通常配合LoRA参数高效微调

### LoRA（低秩适配）
- 只训练低秩矩阵（r=16），参数量<1%
- 目标模块：q/k/v/o_proj + gate/up/down_proj
- 大幅降低显存需求

### 分布式训练
- **DDP**：数据并行
- **DeepSpeed ZeRO2**：分割优化器状态+梯度
- **DeepSpeed ZeRO3**：分割模型参数+梯度+优化器状态

### 奖励函数设计
- **稀疏奖励**：答案正确+1（最终目标）
- **密集奖励**：工具调用成功+0.1、格式正确+0.1（过程引导）
- **混合奖励**：稀疏+密集组合，训练更稳定

## 配套代码（code/chapter11/）
8个脚本+加速配置：数据加载→奖励函数→LoRA配置→SFT训练→GRPO训练→完整pipeline→评估→分布式训练

## 相关概念
- Agentic-RL
- 评估方法
