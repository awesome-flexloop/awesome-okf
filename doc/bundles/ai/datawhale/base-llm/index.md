---
okf_version: "0.2"
type: index
title: "Base LLM — 从 NLP 到 LLM 的算法全栈教程"
bundle: base-llm
description: "Datawhale base-llm 教程的 OKF 知识包，系统覆盖 NLP 基础→词向量→RNN→Transformer→BERT/GPT→LoRA/RLHF→量化部署→安全多模态的完整技术脉络"
sources:
  - https://github.com/datawhalechina/base-llm
concepts:
  - nlp-basics
  - word-vectors-rnn
  - transformer
  - pretrained-models
  - llm-architecture
  - finetuning-alignment
  - inference-deployment
  - safety-multimodal
references:
  - part1-theory
  - part2-practice
  - part3-finetuning
  - part4-deployment
  - part5-safety
  - part6-multimodal
examples:
  - c2-word-vectors
  - c3-rnn
  - c4-transformer
  - c5-pretrained
  - c6-llm-arch
  - c7-text-classification
  - c8-ner
  - c11-lora
  - c13-quantization
  - c14-deployment
  - c19-multimodal
  - c20-omni
---

# Base LLM — 从 NLP 到 LLM 的算法全栈教程

本知识包系统化转译 [Datawhale/base-llm](https://github.com/datawhalechina/base-llm) 开源教程，遵循"Base LLM is all you need"理念，从传统自然语言处理（NLP）基础出发，沿词向量→循环神经网络→Transformer→预训练模型→大模型架构→微调对齐→量化部署→安全多模态的脉络，构建从理论到工程实战的完整知识体系。

## 核心主张

在 LLM 爆发的今天，许多开发者直接上手调用 API 或微调大模型，却忽视了底层 NLP 基础。base-llm 主张：**只有打通从 NLP 到 LLM 的技术演进脉络，才能真正理解大模型"为什么这样设计"，具备排查复杂问题和优化模型结构的能力。**

## 概念文档（concepts/）

按六大部分组织，共 8 篇核心概念：

### 第一部分：NLP 基础与文本表示

* [NLP 基础与发展历程](concepts/nlp-basics.md) — NLP 定义与核心任务（NLU/NLG）、技术四层次（词法/句法/语义/语用）、发展四阶段（规则→统计→深度学习→LLM）、环境准备。

### 第二部分：词向量与序列模型

* [词向量与循环神经网络](concepts/word-vectors-rnn.md) — 分词技术（jieba）、词向量表示、Word2Vec（CBOW/Skip-gram）、Gensim 实战、RNN 原理、LSTM 与 GRU 门控机制。

### 第三部分：Transformer 与预训练

* [Transformer 架构](concepts/transformer.md) — Seq2Seq 架构与信息瓶颈、注意力机制（Q/K/V）、自注意力与交叉注意力、多头注意力、位置编码、Encoder-Decoder 完整结构、手写实现。
* [预训练语言模型](concepts/pretrained-models.md) — BERT（Encoder-only/MLM/NSP）、GPT（Decoder-only/自回归）、T5（Encoder-Decoder/文本到文本）、Hugging Face 生态（Transformers/Tokenizers/Datasets）。
* [大模型架构深入](concepts/llm-architecture.md) — 手搓 Llama2（RoPE/RMSNorm/SwiGLU/GQA）、MoE 稀疏混合专家、文本生成策略（Greedy/Beam/Top-k/Top-p/Temperature）、上下文学习（ICL）与提示词技术。

### 第四部分：微调与对齐

* [参数高效微调与人类对齐](concepts/finetuning-alignment.md) — PEFT 技术谱系（Adapter/Prefix/Prompt Tuning）、LoRA 低秩分解（ΔW=BA）、QLoRA 4-bit 量化微调、RLHF 三阶段（SFT/RM/PPO）、DPO 简化对齐、LLaMA-Factory 实战。

### 第五部分：高效推理与部署

* [量化推理与服务部署](concepts/inference-deployment.md) — 模型量化（INT8/INT4/LLM Compressor）、DeepSpeed 分布式训练（ZeRO）、FastAPI 模型服务、uv/Linux 云部署、Docker Compose 容器化、Git+Jenkins CI/CD。

### 第六部分：安全与多模态

* [大模型安全与多模态前沿](concepts/safety-multimodal.md) — LLM 安全全景、威胁建模（STRIDE）、风险分析、多模态定义、ViT 视觉 Transformer、CLIP 图文对齐、BLIP-2/LLaVA 视觉问答、原生统一架构、从零训练 Omni 模型。

## 实战示例（examples/）

登记 `code/` 目录下的全部示例代码，共 12 组：

* [C2 词向量代码](examples/index.md#c2-词向量) — jieba 分词、Gensim Word2Vec
* [C3 RNN/LSTM 代码](examples/index.md#c3-循环神经网络) — RNN/LSTM 手写实现
* [C4 Transformer 代码](examples/index.md#c4-transformer) — Seq2Seq/Attention/手写 Transformer 模块
* [C5 预训练模型代码](examples/index.md#c5-预训练模型) — BERT/GPT/T5/HuggingFace 使用
* [C6 大模型架构代码](examples/index.md#c6-大模型架构) — 手写 Llama2/MoE
* [C7 文本分类代码](examples/index.md#c7-文本分类) — 朴素/LSTM/BERT 三种实现
* [C8 NER 项目代码](examples/index.md#c8-命名实体识别) — 完整 NER 项目（CMeEE-V2 数据集）
* [C11 LoRA 微调代码](examples/index.md#c11-参数高效微调) — PEFT/QLoRA/Qwen2.5 私有数据微调
* [C13 量化代码](examples/index.md#c13-量化) — LLM Compressor 量化实战
* [C14 部署代码](examples/index.md#c14-服务部署) — FastAPI+Docker NER 服务部署
* [C19 多模态代码](examples/index.md#c19-图文多模态) — CLIP 实现
* [C20 Omni 模型代码](examples/index.md#c20-视觉问答) — seeker-omni 从零训练多模态模型

## 信源登记（references/）

按六大部分登记 `docs/` 下全部章节，共 6 组：

* [第一部分：理论篇](references/index.md#第一部分理论篇) — C1-C6 共 19 节
* [第二部分：实战篇](references/index.md#第二部分实战篇) — C7-C8 共 7 节
* [第三部分：微调量化篇](references/index.md#第三部分微调量化篇) — C11-C13 共 8 节
* [第四部分：应用部署篇](references/index.md#第四部分应用部署篇) — C14-C15 共 5 节
* [第五部分：大模型安全](references/index.md#第五部分大模型安全) — C16 共 2 节
* [第六部分：多模态前沿](references/index.md#第六部分多模态前沿) — C19-C20 共 5 节

## 推荐学习路径

```
📚 NLP 基础（C1）
  → 词向量与 RNN（C2-C3）
    → Transformer（C4）★ 核心枢纽
      → BERT/GPT/T5（C5）
        → Llama2/MoE（C6）
          ├─────────────┐
          ↓             ↓
    实战项目（C7-C8）  微调对齐（C11-C12）
          │             │
          └──────┬──────┘
                 ↓
          量化与部署（C13-C15）
                 ↓
          安全与多模态（C16/C19-C20）
```

## 信任与生命周期说明

* **sources**：全部内容派生自 https://github.com/datawhalechina/base-llm 仓库的 `docs/` 和 `code/` 目录，章节标题与 `docs/_sidebar.md` 一一对应。
* **status**：`stable`——章节结构经 V 阶段校验与 `_sidebar.md` 一致。
* **stale_after**：2027-08-23——base-llm 为活跃教程项目，部分章节（C16 安全工程）标注"建设中"，需定期重新评估。

本知识包共收录 8 个概念文档 + 1 个示例登记 + 1 个信源登记，另含 concepts/examples/references 三个子目录索引和根 index.md、log.md。

```{toctree}
:hidden:

concepts/index
examples/index
references/index
spec/facts
spec/insights
log
```
