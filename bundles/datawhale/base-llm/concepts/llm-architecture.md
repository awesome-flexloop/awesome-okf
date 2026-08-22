---
type: concept
title: "大模型架构深入"
bundle: "/datawhale/base-llm"
description: "手搓 Llama2（RoPE/RMSNorm/SwiGLU/GQA/KV Cache）、MoE 混合专家架构、文本生成策略（Greedy/Beam/Top-k/Top-p）、上下文学习与提示词技术。"
sources:
  - https://github.com/datawhalechina/base-llm/blob/main/docs/chapter6/17_handcraft_llama2.md
  - https://github.com/datawhalechina/base-llm/blob/main/docs/chapter6/18_MoE.md
  - https://github.com/datawhalechina/base-llm/blob/main/docs/chapter6/19_text_generation.md
  - https://github.com/datawhalechina/base-llm/blob/main/docs/chapter6/20_in_context_learning.md
related:
  - /datawhale/base-llm/concepts/transformer
  - /datawhale/base-llm/concepts/pretrained-models
  - /datawhale/base-llm/concepts/finetuning-alignment
---

# 大模型架构深入

## 核心理解

本章在标准 Transformer 的基础上，深入现代大语言模型的架构演进。以 Llama2 为代表，展示了从原始 Transformer 到现代 LLM 的关键改进；以 MoE 展示稀疏激活的参数扩展路径；以生成策略解码模型输出；以上下文学习揭示大模型的涌现能力。`code/C6/llama2/` 和 `code/C6/MoE/` 提供了完整的手写实现。

## 手搓 Llama2

Llama2（Meta, 2023）是开源大模型的里程碑，其架构在标准 Transformer Decoder 基础上引入多项现代改进：

### RoPE（Rotary Position Embedding，旋转位置编码）

与原始 Transformer 的正弦位置编码不同，RoPE 通过**旋转矩阵**将位置信息融入 Q 和 K：

- 对 Q/K 向量的每对维度施加二维旋转，旋转角度与位置成正比。
- 天然支持相对位置编码：$q_i^T k_j$ 的值仅依赖相对位置 $i-j$。
- 具备良好的外推性（可扩展到训练时未见的序列长度，配合 NTK 等插值方法效果更佳）。

### RMSNorm（Root Mean Square Layer Normalization）

替代标准 LayerNorm：
- 移除均值偏移，仅用均方根进行缩放：$RMSNorm(x) = \frac{x}{RMS(x)} \cdot \gamma$。
- 计算更简洁，训练更稳定，效果与 LayerNorm 相当。

### SwiGLU 激活函数

替代 ReLU FFN：
- $FFN_{SwiGLU}(x) = (Swish(xW_1) \otimes xV) W_2$
- 引入门控机制，使用三个权重矩阵而非两个，中间维度通常设为 $\frac{8}{3}d$ 以保持参数量平衡。
- 在多项基准上优于 ReLU/GELU。

### GQA（Grouped-Query Attention，分组查询注意力）

在 MHA（多头注意力）和 MQA（多查询注意力）之间取折中：
- **MHA**：每个头有独立的 Q/K/V。
- **MQA**：所有头共享一组 K/V，加速推理但可能损失质量。
- **GQA**：将头分组，每组共享 K/V，在推理速度和模型质量间取得平衡。

### KV Cache

自回归生成时，已生成 token 的 K/V 向量可缓存复用，避免重复计算。每生成一个新 token，只需计算新 token 的 Q 并与缓存的 K/V 做注意力，是大模型推理加速的核心技术。

### 手写代码结构

`code/C6/llama2/src/` 模块分解：

| 文件 | 内容 |
|------|------|
| `attention.py` | 带 GQA/KV Cache 的注意力实现 |
| `rope.py` | RoPE 旋转位置编码 |
| `norm.py` | RMSNorm |
| `ffn.py` | SwiGLU 前馈网络 |
| `transformer.py` | 完整 Llama2 Block 和模型组装 |
| `main.py` | 运行入口 |

## MoE（Mixture of Experts，混合专家）

### 核心思想

MoE 通过**稀疏激活**在不增加计算量的前提下大幅扩展模型参数量：
- 将 FFN 层替换为多个"专家"网络（Expert）。
- 路由器（Router/Gating Network）根据输入动态选择 Top-k 个专家处理。
- 每个 token 只激活部分专家，总参数量大但单 token 计算量保持不变。

### 关键机制

- **路由**：$G(x) = Softmax(TopK(x \cdot W_g))$，通常选择 Top-2 专家。
- **负载均衡**：引入辅助损失（Load Balancing Loss）防止所有 token 集中到少数专家。
- **容量因子**：每个专家设置 token 容量上限，超出的 token 被丢弃（token dropping）。

### 代表模型

- Switch Transformer（Google）：Top-1 路由，简化训练。
- Mixtral 8x7B（Mistral）：8 个专家，每 token 选 2 个，总参数量 47B 但仅激活 13B。
- DeepSeekMoE：细粒度专家分割和共享专家。

`code/C6/MoE/` 提供了与 Llama2 同构的手写实现，将 FFN 替换为 MoE 层。

## 文本生成策略

大模型输出的是下一个 token 的概率分布，生成策略决定如何从中采样：

### 确定性解码

| 策略 | 方法 | 特点 |
|------|------|------|
| **Greedy Search** | 每步选概率最高的 token | 简单但易重复，缺乏多样性 |
| **Beam Search** | 维护 top-k 个候选序列，选总概率最高 | 质量较高但可能过于保守，适合翻译/摘要 |

### 随机采样

| 策略 | 方法 | 特点 |
|------|------|------|
| **Temperature** | $p_i = \frac{\exp(z_i/T)}{\sum \exp(z_j/T)}$，T 越低越确定 | 控制随机性/创造性 |
| **Top-k** | 仅从概率最高的 k 个 token 中采样 | 过滤低概率 token，但 k 值固定不适应上下文 |
| **Top-p（Nucleus）** | 从累积概率达到 p 的最小 token 集合中采样 | 动态调整候选集大小，自适应上下文 |
| **Repetition Penalty** | 对已出现 token 的概率施加惩罚 | 减少重复生成 |

实际应用中通常组合使用：Temperature + Top-p + Repetition Penalty。

## 上下文学习（In-Context Learning, ICL）

### 涌现能力

GPT-3 展示的标志性能力：模型无需参数更新，仅通过在上下文中提供示例即可完成新任务：

- **Zero-shot**：仅给指令，无示例。
- **One-shot**：给一个示例。
- **Few-shot**：给少量示例（通常 3-5 个）。

### 思维链（Chain-of-Thought, CoT）

通过在示例中展示**推理步骤**而非仅给出答案，引导模型逐步推理：
- 标准提示："Q: 小明有 3 个苹果，吃了 2 个，还剩几个？A: 1 个"
- CoT 提示："Q: ... A: 小明原有 3 个，吃了 2 个，3-2=1，答案是 1 个"

CoT 在数学推理、逻辑推理等复杂任务上显著提升表现。

### 提示词工程（Prompt Engineering）

系统化的提示设计技术：
- **角色设定**：给模型分配专业角色。
- **指令清晰**：明确任务、格式、约束。
- **少样本示例**：提供输入输出范例。
- **思维链**：要求模型"一步步思考"。
- **自一致性**：多次采样取多数结果。
- **ReAct**：推理（Reasoning）+行动（Acting）交替进行。

## 延伸阅读

- 前置：[预训练语言模型](pretrained-models.md)——BERT/GPT/T5 基础
- 微调：[参数高效微调与人类对齐](finetuning-alignment.md)
- 部署：[量化推理与服务部署](inference-deployment.md)
- 示例代码：[C6 大模型架构代码](../examples/index.md#c6-大模型架构)
