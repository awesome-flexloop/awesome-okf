---
type: example
title: "LLaMA2 模型构建与预训练"
bundle: /datawhale/happy-llm
description: "第五章代码实践：纯 PyTorch 手写 LLaMA2 架构，训练 Tokenizer，完成预训练与有监督微调全流程"
sources: https://github.com/datawhalechina/happy-llm/tree/main/docs/chapter5/code
related:
  - /datawhale/happy-llm/concepts/llama2-implementation
  - /datawhale/happy-llm/concepts/model-training
tags: [llama2, pretrain, sft, tokenizer, ddp, pytorch]
status: stable
---

# LLaMA2 模型构建与预训练

## 概述

本示例对应 Happy-LLM 第五章，代码位于 `docs/chapter5/code/`。基于纯 PyTorch 从零搭建一个 LLaMA2 架构的小型大模型（Tiny-K，215M 参数），完整实现从模型定义、Tokenizer 训练、数据处理到预训练和 SFT 的全流程。

## 环境准备

```bash
pip install -r docs/chapter5/code/requirements.txt
```

建议单卡 GPU，部分步骤可先在 CPU 调试。

## 代码结构

| 文件 | 职责 |
|------|------|
| `k_model.py` | LLaMA2 模型定义（RMSNorm、RoPE、GQA、SwiGLU、Transformer Block） |
| `model_sample.py` | 模型采样/推理 |
| `train_tokenizer.py` | BPE Tokenizer 训练 |
| `dataset.py` | 数据集类定义 |
| `deal_dataset.py` | 数据预处理与分块 |
| `ddp_pretrain.py` | DDP 分布式预训练 |
| `ddp_sft_full.py` | DDP 全参数有监督微调 |
| `export_model.py` | 导出为 HuggingFace 格式 |

## 实践流程

### 第一步：训练 Tokenizer

```bash
python train_tokenizer.py
```

使用 BPE 算法在中文语料上训练，词汇表大小 6144，产出 tokenizer 配置文件。

### 第二步：数据预处理

```bash
python deal_dataset.py
```

将原始语料分块为固定长度序列，分别构建预训练数据集和 SFT 数据集。预训练数据为纯文本（CLM 任务），SFT 数据为指令-回答对。

### 第三步：预训练

```bash
torchrun --nproc_per_node=<GPU数> ddp_pretrain.py
```

使用 DDP 分布式训练，CLM 任务（预测下一个 token），产出 Base 模型。

### 第四步：有监督微调

```bash
torchrun --nproc_per_node=<GPU数> ddp_sft_full.py
```

在指令数据上全参数微调，产出 SFT（Chat）模型。

### 第五步：模型导出

```bash
python export_model.py
```

将训练好的模型转换为 HuggingFace 格式，便于使用 Transformers 加载和分享。

## 模型核心组件

### ModelConfig

配置模型维度（768）、层数（12）、注意力头数（16 Q heads / 8 KV heads）、词汇表大小（6144）、最大序列长度（512）等超参数。继承 `PretrainedConfig` 支持 HuggingFace 生态。

### RMSNorm

相比 LayerNorm 省去均值计算，仅用均方根归一化，训练更稳定。

### RoPE 旋转位置编码

通过对 Q/K 施加旋转变换注入位置信息，支持长度外推。

### GQA 分组查询注意力

16 个 Q 头共享 8 组 K/V 头，平衡 MHA 的质量和 MQA 的推理效率。

### SwiGLU FFN

使用 Swish 激活和门控机制，隐藏层维度约为 (8/3) × dim，表达能力优于 ReLU。

## 产出模型

- **Happy-LLM-Chapter5-Base-215M**：预训练基座模型
- **Happy-LLM-Chapter5-SFT-215M**：有监督微调对话模型

均开源于 ModelScope，提供创空间在线体验。

## 学习要点

1. **模型架构与公式的对应**：每个组件的代码实现都能对应到论文中的数学公式
2. **预训练 vs SFT 数据格式**：纯文本续写 vs 指令回答对
3. **DDP 分布式训练**：分布式采样器、梯度同步、检查点保存
4. **HuggingFace 格式兼容**：继承 PretrainedConfig，便于生态集成

## 延伸阅读

- [LLaMA2 手写实现](../concepts/llama2-implementation.md)——完整概念解析
- [模型训练](../concepts/model-training.md)——三阶段训练与工业级框架
- [手写 Transformer 注意力机制](transformer-handwritten.md)——第二章基础实现
