---
title: Agentic-RL
type: concept
bundle: /datawhale/hello-agents
related:
  - /datawhale/hello-agents/concepts/agent-paradigms-react
  - /datawhale/hello-agents/concepts/evaluation-methods
  - /datawhale/hello-agents/references/chapter11-agentic-rl
sources:
  - https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter11/第十一章%20Agentic-RL.md
---

# Agentic-RL

Agentic-RL（基于强化学习的智能体训练）将LLM视为可学习策略，嵌入智能体的感知-决策-执行循环，通过强化学习优化多步任务表现。它标志着从"优化单次回答质量"到"优化任务完成度"的范式转移。

## LLM训练全景

一个强大的LLM诞生经历两大阶段：

### 预训练阶段
- 海量文本数据（数TB级），自监督学习
- 因果语言建模（下一个词预测）
- 学习语法规则、语义知识、世界知识和基础推理能力

### 后训练阶段
1. **监督微调（SFT）**：用(prompt, completion)对训练，学习指令遵循和对话格式
2. **奖励建模（RM）**：用偏好对比数据（chosen vs rejected）训练奖励模型
3. **强化学习微调**：PPO等算法，最大化奖励同时通过KL散度防止偏离参考模型

RLHF（人类反馈强化学习）成本高昂，RLAIF（AI反馈强化学习）用强大AI模型替代人类标注员，效果接近甚至超过RLHF。

## Agentic RL vs 传统后训练

传统后训练称为PBRFT（Preference-Based Reinforcement Fine-Tuning），两者从MDP角度有本质区别：

| MDP要素 | PBRFT | Agentic RL |
|---------|-------|------------|
| 状态 | 仅用户prompt（$s_0$） | prompt + 历史观察（$s_t$ = prompt, $o_1$...$o_t$） |
| 时间跨度 | T=1（单步） | T≫1（多步） |
| 行动空间 | 仅文本生成 | 文本生成 + 工具调用 + 环境操作 |
| 状态转移 | 无 | 根据行动和环境动态变化 |
| 奖励 | 单步，任务结束时给 | 多步，可中间给予部分奖励 |
| 优化目标 | 最大化单步期望奖励 | 最大化累积折扣奖励 |
| 思维焦点 | "如何生成更好的单个回答" | "如何完成复杂任务" |

### 奖励设计
- **稀疏奖励**：只在任务完成时给予（如答案正确+1）
- **密集奖励**：每步都给予（如工具调用成功+0.1）
- **混合奖励**：结合两者

## 六大核心能力

Agentic RL旨在赋予LLM智能体：

1. **推理（Reasoning）**：通过试错学习有效推理策略，发现训练数据中没有的推理路径
2. **工具使用（Tool Use）**：学会何时用工具、选哪个工具、如何组合多个工具
3. **记忆（Memory）**：学会记忆管理策略——记住什么、何时更新、何时遗忘
4. **规划（Planning）**：动态规划行动序列，权衡短期和长期收益
5. **自我改进（Self-Improvement）**：识别错误、分析失败原因、调整策略
6. **感知（Perception）**：理解多模态信息，视觉推理与规划

## GRPO：群组相对策略优化

GRPO（Group Relative Policy Optimization）是Agentic RL的关键算法创新：

- **去除critic网络**：不需要价值函数估计，降低训练成本和显存占用
- **群组内相对优势**：对同一问题采样一组输出，用组内奖励的相对值作为优势估计
- **工程价值显著**：使中小团队也能进行Agent强化学习训练

## 完整训练Pipeline

```
数据加载 → 奖励函数定义 → LoRA配置 → SFT训练 → GRPO训练 → 模型评估
```

### 关键技术组件

- **LoRA（低秩适配）**：参数高效微调，只训练少量低秩矩阵，大幅降低显存需求
- **DeepSpeed ZeRO**：分布式训练优化
  - ZeRO2：分割优化器状态和梯度
  - ZeRO3：分割模型参数、梯度和优化器状态
- **多GPU DDP**：数据并行训练

### 代码结构（code/chapter11/）
- `01_dataset_loading.py`：数据集加载
- `02_reward_functions.py`：奖励函数定义
- `03_lora_configuration.py`：LoRA配置
- `04_sft_training.py`：SFT训练
- `05_grpo_training.py`：GRPO训练
- `06_complete_pipeline.py`：完整pipeline
- `07_model_evaluation.py`：模型评估
- `08_distributed_training.py`：分布式训练

## 范式转移的意义

Agentic RL不仅仅是技术细节差异，而是思维方式的根本转变：

- PBRFT思维：优化回答质量 → 关注语言表达 → 单步决策
- Agentic RL思维：优化任务完成度 → 关注行动策略 → 多步规划

这种转变使LLM从"对话助手"进化为"自主智能体"——能够主动寻找信息、知道何时如何使用外部工具、为最终目标执行"绕路"的中间步骤、从错误中学习。

## 相关阅读

- [第十一章 Agentic-RL](/datawhale/hello-agents/references/chapter11-agentic-rl)
- [智能体范式与ReAct](/datawhale/hello-agents/concepts/agent-paradigms-react)
- [评估方法](/datawhale/hello-agents/concepts/evaluation-methods)
