---
type: reference
title: "第六章 大模型训练流程实践"
bundle: /datawhale/happy-llm
description: "Transformers 框架、DeepSpeed 分布式训练、预训练/SFT/LoRA/QLoRA 高效微调工业级实践"
source: https://github.com/datawhalechina/happy-llm/blob/main/docs/chapter6/第六章%20大模型训练流程实践.md
path: docs/chapter6/第六章 大模型训练流程实践.md
code: docs/chapter6/code/
tags: [transformers, deepspeed, lora, qlora, peft, sft, pretrain]
status: stable
---

# 第六章 大模型训练流程实践

## 信源信息

- **文件路径**：`docs/chapter6/第六章 大模型训练流程实践.md`
- **实践说明**：`docs/chapter6/readme.md`
- **补充专题**：`docs/chapter6/6.4[WIP] 偏好对齐.md`
- **代码目录**：`docs/chapter6/code/`
- **GitHub**：https://github.com/datawhalechina/happy-llm/blob/main/docs/chapter6/第六章%20大模型训练流程实践.md

## 内容概要

本章从手写实现切换到工业级训练框架，涵盖：

- **6.1 模型预训练**
  - Transformers 框架介绍（AutoModel、AutoConfig、Trainer）
  - HuggingFace Hub 生态（模型、数据集、评估）
  - 使用 Qwen-2.5-1.5B 架构初始化模型
  - `pretrain.py`/`pretrain.sh` 预训练脚本
  - DeepSpeed ZeRO-2 分布式配置（`ds_config_zero2.json`）

- **6.2 有监督微调（SFT）**
  - `finetune.py`/`finetune.sh` 微调脚本
  - 数据预处理（`process_dataset.ipynb`）
  - 全参数微调实践

- **6.3 高效微调**
  - LoRA（Low-Rank Adaptation）：低秩分解矩阵，仅训练 0.1%-1% 参数
  - QLoRA：4-bit 量化 + LoRA，单卡 24GB 可微调 65B 模型
  - PEFT 库集成

- **6.4 偏好对齐**（WIP 补充专题）
  - RLHF 整体学习路线

## 代码资产

| 文件 | 用途 |
|------|------|
| `download_model.py` | 下载基座模型 |
| `download_dataset.py` | 下载训练数据 |
| `pretrain.py` / `pretrain.sh` | 预训练主脚本 |
| `finetune.py` / `finetune.sh` | SFT/PEFT 微调主脚本 |
| `ds_config_zero2.json` | DeepSpeed ZeRO-2 配置 |
| `pretrain.ipynb` | 预训练 Notebook |
| `process_dataset.ipynb` | 数据处理 Notebook |
| `whole.ipynb` | 完整流程 Notebook |

## 对应概念

- [模型训练](../concepts/model-training.md)
- [LLaMA2 手写实现](../concepts/llama2-implementation.md)
- [LLaMA2 模型构建与预训练示例](../examples/llama2-pretrain-sft.md)
