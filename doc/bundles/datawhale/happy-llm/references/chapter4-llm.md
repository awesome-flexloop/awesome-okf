---
type: reference
title: "第四章 大语言模型"
bundle: /datawhale/happy-llm
description: "LLM 定义、涌现能力、上下文学习、指令遵循、逐步推理与三阶段训练流程"
source: https://github.com/datawhalechina/happy-llm/blob/main/docs/chapter4/第四章%20大语言模型.md
path: docs/chapter4/第四章 大语言模型.md
tags: [llm, emergent-abilities, icl, sft, rlhf]
status: stable
---

# 第四章 大语言模型

## 信源信息

- **文件路径**：`docs/chapter4/第四章 大语言模型.md`
- **GitHub**：https://github.com/datawhalechina/happy-llm/blob/main/docs/chapter4/第四章%20大语言模型.md

## 内容概要

本章正式进入 LLM 部分，涵盖：

- **4.1 什么是 LLM**
  - 定义：数百亿+参数、数 T token 语料预训练、具备涌现能力的语言模型
  - 广义范围：从十亿参数（Qwen-1.5B）到千亿参数（Grok-314B）
  - 开端：GPT-3（1750 亿参数），ChatGPT 主导 LLM 时代

- **LLM 四大核心能力**：
  - **涌现能力（Emergent Abilities）**：小型模型不具备、大型模型突然显现的能力，量变引起质变
  - **上下文学习（In-context Learning, ICL）**：通过 Prompt 中的示例或指令执行任务，无需参数更新
  - **指令遵循（Instruction Following）**：理解并遵循未见过的指令，泛化到新任务
  - **逐步推理（Step by Step Reasoning）**：通过思维链（CoT）解决多步推理任务

- **LLM 特点**：多语言支持、长文本处理（RoPE 外推）、多模态拓展、幻觉问题

- **4.2 如何训练一个 LLM**——三阶段训练流程：
  1. **预训练（Pretraining）**：海量无监督语料 CLM 训练
  2. **有监督微调（SFT）**：指令数据微调
  3. **强化学习对齐（RLHF）**：奖励模型 + PPO

## 对应概念

- [模型训练](../concepts/model-training.md)
- [预训练语言模型](../concepts/pretrained-language-model.md)
