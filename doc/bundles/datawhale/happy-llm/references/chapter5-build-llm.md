---
type: reference
title: "第五章 动手搭建大模型"
bundle: /datawhale/happy-llm
description: "纯 PyTorch 手写 LLaMA2 架构，训练 Tokenizer，完成预训练与有监督微调全流程"
source: https://github.com/datawhalechina/happy-llm/blob/main/docs/chapter5/第五章%20动手搭建大模型.md
path: docs/chapter5/第五章 动手搭建大模型.md
code: docs/chapter5/code/
tags: [llama2, implementation, tokenizer, pretrain, sft, ddp]
status: stable
---

# 第五章 动手搭建大模型

## 信源信息

- **文件路径**：`docs/chapter5/第五章 动手搭建大模型.md`
- **代码目录**：`docs/chapter5/code/`
- **GitHub**：https://github.com/datawhalechina/happy-llm/blob/main/docs/chapter5/第五章%20动手搭建大模型.md

## 内容概要

本章是全书动手实践的核心，涵盖：

- **5.1 动手实现 LLaMA2 大模型**
  - ModelConfig 超参数配置（dim=768, n_layers=12, n_heads=16, n_kv_heads=8, vocab_size=6144）
  - RMSNorm 归一化层
  - RoPE 旋转位置编码
  - GQA 分组查询注意力
  - SwiGLU 前馈网络
  - Transformer Block 组装
  - KV Cache 推理加速

- **Tokenizer 训练**：BPE 算法，词汇表 6144

- **数据处理**：
  - `dataset.py`：数据集类
  - `deal_dataset.py`：语料分块与预处理
  - 预训练数据（纯文本）vs SFT 数据（指令-回答对）

- **训练脚本**：
  - `ddp_pretrain.py`：DDP 分布式预训练
  - `ddp_sft_full.py`：DDP 全参数 SFT
  - `export_model.py`：HuggingFace 格式导出

- **产出模型**：
  - Happy-LLM-Chapter5-Base-215M（预训练基座）
  - Happy-LLM-Chapter5-SFT-215M（微调对话模型）
  - 托管于 ModelScope，提供创空间体验

## 对应概念

- [LLaMA2 手写实现](../concepts/llama2-implementation.md)
- [模型训练](../concepts/model-training.md)
- [LLaMA2 模型构建与预训练示例](../examples/llama2-pretrain-sft.md)
