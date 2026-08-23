---
title: 第三章 大语言模型基础
type: reference
bundle: /datawhale/hello-agents
chapter: 3
part: 第一部分：智能体与语言模型基础
sources:
  - https://github.com/datawhalechina/hello-agents/blob/main/docs/chapter3/第三章%20大语言模型基础.md
---

# 第三章 大语言模型基础

## 章节概要

本章聚焦LLM本身，从语言模型基本定义出发，理解Transformer架构、提示工程和LLM能力边界，为理解Agent工作原理打基础。

## 核心知识点

### 语言模型演进
- **N-gram模型**：基于马尔可夫假设，词出现概率只与前n-1个词有关
  - Bigram: $P(w_i|w_{i-1})$
  - Trigram: $P(w_i|w_{i-2}, w_{i-1})$
  - 最大似然估计：Count(w_{i-1},w_i) / Count(w_{i-1})
- **RNN/LSTM**：处理变长序列，但存在梯度消失/爆炸问题
- **Transformer**：自注意力机制，并行计算，长距离依赖

### Transformer架构核心
- **自注意力（Self-Attention）**：每个token与所有token建立关联
  - Q（Query）、K（Key）、V（Value）矩阵
  - Attention(Q,K,V) = softmax(QK^T/√d_k)V
- **多头注意力**：多组Q/K/V并行关注不同子空间
- **位置编码**：注入序列位置信息
- **前馈网络**：逐位置非线性变换

### 提示工程（Prompt Engineering）
- **Zero-shot**：无示例直接提问
- **Few-shot**：提供少量示例引导模型
- **Chain-of-Thought（CoT）**：引导模型逐步推理
  - "让我们一步步思考"
  - 显著提升复杂推理任务表现

### 主流LLM概览
- GPT系列（OpenAI）
- Claude（Anthropic）
- Qwen/通义千问（阿里巴巴）
-  DeepSeek、Llama等开源模型

### LLM能力与局限
**能力**：
- 强大的自然语言理解和生成
- 少样本学习和涌现能力
- 多轮对话和指令遵循

**局限**：
- **幻觉（Hallucination）**：生成看似合理但事实错误的内容
- **上下文窗口限制**：可处理的token长度有限
- 知识时效性（训练数据截止点）
- 推理能力在复杂任务上不稳定

## 关键内容
- 语言模型概率计算与链式法则
- Transformer自注意力机制数学原理
- Token化与采样策略（temperature、top-p、top-k）
- OpenAI兼容API调用方式

## 相关概念
- [智能体范式与ReAct](/datawhale/hello-agents/concepts/agent-paradigms-react)
- [上下文工程](/datawhale/hello-agents/concepts/context-engineering)
