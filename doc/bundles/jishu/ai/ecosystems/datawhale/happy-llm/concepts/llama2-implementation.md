---
type: concept
title: "LLaMA2 手写实现"
bundle: /datawhale/happy-llm
description: "基于 PyTorch 从零实现 LLaMA2 模型架构：RMSNorm、RoPE、GQA、SwiGLU、KV Cache 等现代 LLM 核心组件"
sources: https://github.com/datawhalechina/happy-llm/blob/main/docs/chapter5/第五章%20动手搭建大模型.md
related:
  - /datawhale/happy-llm/concepts/transformer-architecture
  - /datawhale/happy-llm/concepts/pretrained-language-model
  - /datawhale/happy-llm/concepts/model-training
  - /datawhale/happy-llm/examples/llama2-pretrain-sft
tags: [llama2, pytorch, implementation, rmsnorm, rope, gqa, swiglu]
status: stable
---

# LLaMA2 手写实现

## 核心理解

第五章引导读者基于纯 PyTorch 从零搭建一个 LLaMA2 架构的小型大模型（Tiny-K，215M 参数），完整实现从模型定义、Tokenizer 训练、数据处理到预训练和有监督微调的全流程。这是理解现代 LLM 内部结构的最直接方式。

LLaMA2 是 Meta 于 2023 年发布的开源大语言模型，在 Transformer Decoder 基础上集成了多项现代架构改进。

## 核心组件

### ModelConfig 超参数配置

```python
class ModelConfig(PretrainedConfig):
    model_type = "Tiny-K"
    dim: int = 768           # 模型隐藏维度
    n_layers: int = 12       # Transformer 层数
    n_heads: int = 16        # Query 注意力头数
    n_kv_heads: int = 8      # Key/Value 头数（GQA）
    vocab_size: int = 6144   # 词汇表大小
    max_seq_len: int = 512   # 最大序列长度
```

继承 `transformers.PretrainedConfig`，便于后续导出 HuggingFace 格式模型。

### RMSNorm（均方根层归一化）

替代 LayerNorm 的归一化方法，仅使用均方根进行缩放，不减去均值，计算更简洁：

```
RMSNorm(x) = x / sqrt(mean(x²) + ε) · γ
```

其中 γ 是可学习缩放参数。RMSNorm 在深层网络中训练更稳定。

### RoPE（旋转位置编码）

旋转位置编码通过对 Q/K 向量施加旋转变换注入位置信息，具有相对位置编码特性和长度外推能力。相比 Transformer 原始的正弦绝对位置编码，RoPE：

- 编码相对位置关系而非绝对位置
- 支持一定程度的长度外推（推理时可处理比训练更长的序列）
- 是 LLaMA、Qwen、DeepSeek 等现代 LLM 的标准位置编码

### GQA（分组查询注意力）

GQA 是 MHA（多头注意力）和 MQA（多查询注意力）的折中：

- **MHA**：每个 Q 头对应独立的 K/V 头（质量最高，KV Cache 最大）
- **MQA**：所有 Q 头共享一组 K/V（KV Cache 最小，质量有损）
- **GQA**：Q 头分组，每组共享一组 K/V（平衡质量与效率）

配置中 `n_heads=16, n_kv_heads=8` 表示每 2 个 Q 头共享 1 组 K/V。

### SwiGLU 激活函数

LLaMA2 的 FFN 使用 SwiGLU 替代 ReLU：

```
FFN(x) = (Swish(xW_1) ⊗ xW_2) W_3
```

SwiGLU 在语言模型任务上表现优于 ReLU 和 GELU，但使用三个权重矩阵（而非传统的两个）。隐藏层维度通常设为 `(8/3) · dim` 并对齐到 256 的倍数。

### Transformer Block

LLaMA2 的每个 Decoder Layer 结构：

```
输入
  → RMSNorm → Self-Attention（GQA + RoPE + KV Cache）→ 残差连接
  → RMSNorm → SwiGLU FFN → 残差连接
输出
```

与原始 Transformer 的区别：Pre-Norm（归一化在注意力/FFN 之前）、RMSNorm 替代 LayerNorm、GQA 替代 MHA、SwiGLU 替代 ReLU。

### KV Cache

自回归生成时缓存已计算的 Key/Value 张量，避免每生成一个 token 就重新计算整个序列的注意力，将生成复杂度从 O(n²) 降至 O(n)。

## Tokenizer 训练

使用 BPE（Byte-Pair Encoding）算法在中文语料上训练 Tokenizer，词汇表大小 6144。代码位于 `train_tokenizer.py`。

## 训练流程

1. **数据预处理**（`dataset.py`/`deal_dataset.py`）：语料分块、构建预训练和 SFT 数据集
2. **预训练**（`ddp_pretrain.py`）：DDP 分布式训练，CLM 任务
3. **有监督微调**（`ddp_sft_full.py`）：在指令数据上全参数微调
4. **模型导出**（`export_model.py`）：转换为 HuggingFace 格式

最终产出 Happy-LLM-Chapter5-Base-215M 和 SFT-215M 模型，开源于 ModelScope。

## 在 Happy-LLM 中的位置

第五章是全书的"动手核心"，将前四章的理论知识（Transformer、PLM、LLM 训练）转化为可运行的代码。手写阶段不追求生产可用，而追求每个组件都能对应到论文和架构图，为第六章使用工业级框架建立心智模型。

## 延伸阅读

- [Transformer 架构](transformer-architecture.md)——LLaMA2 的基础架构
- [预训练语言模型](pretrained-language-model.md)——Decoder-only 路线
- [模型训练](model-training.md)——从手写到 Transformers 框架的训练实践
- [LLaMA2 模型构建与预训练示例](../examples/llama2-pretrain-sft.md)——第五章代码实践
