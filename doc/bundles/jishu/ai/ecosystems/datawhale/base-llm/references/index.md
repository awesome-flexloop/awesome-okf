---
okf_version: "0.2"
type: index
title: base-llm 信源登记
sources:
  - https://github.com/datawhalechina/base-llm/tree/main/docs
---

# 信源登记簿

本目录登记 base-llm 教程 `docs/` 下全部章节。所有概念文档的 `sources` 字段均指向此处登记的原始章节。章节标题与 `docs/_sidebar.md` 严格一致。

---

## 第一部分：理论篇

### 第 1 章：NLP 简介（chapter1/）

| 章节 | 文件 | 对应概念 |
|------|------|---------|
| NLP 概述 | [01_nlp_intro.md](https://github.com/datawhalechina/base-llm/blob/main/docs/chapter1/01_nlp_intro.md) | [NLP 基础与发展历程](../concepts/nlp-basics.md) |
| 环境准备 | [02_preparation.md](https://github.com/datawhalechina/base-llm/blob/main/docs/chapter1/02_preparation.md) | [NLP 基础与发展历程](../concepts/nlp-basics.md) |

### 第 2 章：文本表示与词向量（chapter2/）

| 章节 | 文件 | 对应概念 |
|------|------|---------|
| 初级分词技术 | [03_tokenization.md](https://github.com/datawhalechina/base-llm/blob/main/docs/chapter2/03_tokenization.md) | [词向量与循环神经网络](../concepts/word-vectors-rnn.md) |
| 词向量表示 | [04_word_vector.md](https://github.com/datawhalechina/base-llm/blob/main/docs/chapter2/04_word_vector.md) | [词向量与循环神经网络](../concepts/word-vectors-rnn.md) |
| 从主题模型到 Word2Vec | [05_Word2Vec.md](https://github.com/datawhalechina/base-llm/blob/main/docs/chapter2/05_Word2Vec.md) | [词向量与循环神经网络](../concepts/word-vectors-rnn.md) |
| 基于 Gensim 的词向量实战 | [06_gensim.md](https://github.com/datawhalechina/base-llm/blob/main/docs/chapter2/06_gensim.md) | [词向量与循环神经网络](../concepts/word-vectors-rnn.md) |

### 第 3 章：循环神经网络（chapter3/）

| 章节 | 文件 | 对应概念 |
|------|------|---------|
| 循环神经网络 | [08_RNN.md](https://github.com/datawhalechina/base-llm/blob/main/docs/chapter3/08_RNN.md) | [词向量与循环神经网络](../concepts/word-vectors-rnn.md) |
| LSTM 与 GRU | [09_LSTM&GRU.md](https://github.com/datawhalechina/base-llm/blob/main/docs/chapter3/09_LSTM&GRU.md) | [词向量与循环神经网络](../concepts/word-vectors-rnn.md) |

### 第 4 章：注意力机制与 Transformer（chapter4/）

| 章节 | 文件 | 对应概念 |
|------|------|---------|
| Seq2Seq 架构 | [10_seq2seq.md](https://github.com/datawhalechina/base-llm/blob/main/docs/chapter4/10_seq2seq.md) | [Transformer 架构](../concepts/transformer.md) |
| 注意力机制 | [11_attention.md](https://github.com/datawhalechina/base-llm/blob/main/docs/chapter4/11_attention.md) | [Transformer 架构](../concepts/transformer.md) |
| 深入解析 Transformer | [12_transformer.md](https://github.com/datawhalechina/base-llm/blob/main/docs/chapter4/12_transformer.md) | [Transformer 架构](../concepts/transformer.md) |

### 第 5 章：预训练模型（chapter5/）

| 章节 | 文件 | 对应概念 |
|------|------|---------|
| BERT 结构及应用 | [13_Bert.md](https://github.com/datawhalechina/base-llm/blob/main/docs/chapter5/13_Bert.md) | [预训练语言模型](../concepts/pretrained-models.md) |
| GPT 结构及应用 | [14_GPT.md](https://github.com/datawhalechina/base-llm/blob/main/docs/chapter5/14_GPT.md) | [预训练语言模型](../concepts/pretrained-models.md) |
| T5 结构及应用 | [15_T5.md](https://github.com/datawhalechina/base-llm/blob/main/docs/chapter5/15_T5.md) | [预训练语言模型](../concepts/pretrained-models.md) |
| Hugging Face 生态与核心库 | [16_HuggingFace.md](https://github.com/datawhalechina/base-llm/blob/main/docs/chapter5/16_HuggingFace.md) | [预训练语言模型](../concepts/pretrained-models.md) |

### 第 6 章：深入大模型架构（chapter6/）

| 章节 | 文件 | 对应概念 |
|------|------|---------|
| 手搓一个大模型 | [17_handcraft_llama2.md](https://github.com/datawhalechina/base-llm/blob/main/docs/chapter6/17_handcraft_llama2.md) | [大模型架构深入](../concepts/llm-architecture.md) |
| MoE 架构解析 | [18_MoE.md](https://github.com/datawhalechina/base-llm/blob/main/docs/chapter6/18_MoE.md) | [大模型架构深入](../concepts/llm-architecture.md) |
| 手撕大模型生成策略 | [19_text_generation.md](https://github.com/datawhalechina/base-llm/blob/main/docs/chapter6/19_text_generation.md) | [大模型架构深入](../concepts/llm-architecture.md) |
| 上下文学习与提示词技术 | [20_in_context_learning.md](https://github.com/datawhalechina/base-llm/blob/main/docs/chapter6/20_in_context_learning.md) | [大模型架构深入](../concepts/llm-architecture.md) |

---

## 第二部分：实战篇

### 第 1 章：文本分类（chapter7/）

| 章节 | 文件 | 对应概念 |
|------|------|---------|
| 文本分类简单实现 | [01_text_classification.md](https://github.com/datawhalechina/base-llm/blob/main/docs/chapter7/01_text_classification.md) | [预训练语言模型](../concepts/pretrained-models.md) |
| 基于 LSTM 的文本分类 | [02_lstm_text_classification.md](https://github.com/datawhalechina/base-llm/blob/main/docs/chapter7/02_lstm_text_classification.md) | [词向量与循环神经网络](../concepts/word-vectors-rnn.md) |
| 微调 BERT 模型进行文本分类 | [03_bert_text_classification.md](https://github.com/datawhalechina/base-llm/blob/main/docs/chapter7/03_bert_text_classification.md) | [预训练语言模型](../concepts/pretrained-models.md) |

### 第 2 章：命名实体识别（chapter8/）

| 章节 | 文件 | 对应概念 |
|------|------|---------|
| 命名实体识别概要 | [01_named_entity_recognition.md](https://github.com/datawhalechina/base-llm/blob/main/docs/chapter8/01_named_entity_recognition.md) | [预训练语言模型](../concepts/pretrained-models.md) |
| NER 项目的数据处理 | [02_data_processing.md](https://github.com/datawhalechina/base-llm/blob/main/docs/chapter8/02_data_processing.md) | [预训练语言模型](../concepts/pretrained-models.md) |
| 模型构建、训练与推理 | [03_model_building_and_training.md](https://github.com/datawhalechina/base-llm/blob/main/docs/chapter8/03_model_building_and_training.md) | [预训练语言模型](../concepts/pretrained-models.md) |
| 模型的推理与优化 | [04_evaluation_and_prediction.md](https://github.com/datawhalechina/base-llm/blob/main/docs/chapter8/04_evaluation_and_prediction.md) | [预训练语言模型](../concepts/pretrained-models.md) |

---

## 第三部分：微调量化篇

### 第 1 章：参数高效微调（chapter11/）

| 章节 | 文件 | 对应概念 |
|------|------|---------|
| PEFT 技术综述 | [01_PEFT.md](https://github.com/datawhalechina/base-llm/blob/main/docs/chapter11/01_PEFT.md) | [参数高效微调与人类对齐](../concepts/finetuning-alignment.md) |
| LoRA 方法详解 | [02_lora.md](https://github.com/datawhalechina/base-llm/blob/main/docs/chapter11/02_lora.md) | [参数高效微调与人类对齐](../concepts/finetuning-alignment.md) |
| 基于 peft 库的 LoRA 实战 | [03_peft_lora.md](https://github.com/datawhalechina/base-llm/blob/main/docs/chapter11/03_peft_lora.md) | [参数高效微调与人类对齐](../concepts/finetuning-alignment.md) |
| Qwen2.5 微调私有数据 | [04_qwen2.5_qlora.md](https://github.com/datawhalechina/base-llm/blob/main/docs/chapter11/04_qwen2.5_qlora.md) | [参数高效微调与人类对齐](../concepts/finetuning-alignment.md) |

### 第 2 章：高级微调技术（chapter12/）

| 章节 | 文件 | 对应概念 |
|------|------|---------|
| RLHF 技术详解 | [01_RLHF.md](https://github.com/datawhalechina/base-llm/blob/main/docs/chapter12/01_RLHF.md) | [参数高效微调与人类对齐](../concepts/finetuning-alignment.md) |
| LLaMA-Factory RLHF（DPO）实战 | [02_llama_factory.md](https://github.com/datawhalechina/base-llm/blob/main/docs/chapter12/02_llama_factory.md) | [参数高效微调与人类对齐](../concepts/finetuning-alignment.md) |

### 第 3 章：大模型训练与量化（chapter13/）

| 章节 | 文件 | 对应概念 |
|------|------|---------|
| 模型量化实战 | [01_quantization.md](https://github.com/datawhalechina/base-llm/blob/main/docs/chapter13/01_quantization.md) | [量化推理与服务部署](../concepts/inference-deployment.md) |
| Deepspeed 框架介绍 | [02_deepspeed.md](https://github.com/datawhalechina/base-llm/blob/main/docs/chapter13/02_deepspeed.md) | [量化推理与服务部署](../concepts/inference-deployment.md) |

---

## 第四部分：应用部署篇

### 第 1 章：模型服务部署（chapter14/）

| 章节 | 文件 | 对应概念 |
|------|------|---------|
| FastAPI 模型部署实战 | [01_fastapi.md](https://github.com/datawhalechina/base-llm/blob/main/docs/chapter14/01_fastapi.md) | [量化推理与服务部署](../concepts/inference-deployment.md) |
| 云服务器模型部署实战 | [02_uv_linux.md](https://github.com/datawhalechina/base-llm/blob/main/docs/chapter14/02_uv_linux.md) | [量化推理与服务部署](../concepts/inference-deployment.md) |
| 使用 Docker Compose 部署模型服务 | [03_docker_deploy.md](https://github.com/datawhalechina/base-llm/blob/main/docs/chapter14/03_docker_deploy.md) | [量化推理与服务部署](../concepts/inference-deployment.md) |

### 第 2 章：自动化与性能优化（chapter15/）

| 章节 | 文件 | 对应概念 |
|------|------|---------|
| Git 与 GitHub 版本控制基础 | [01_Git.md](https://github.com/datawhalechina/base-llm/blob/main/docs/chapter15/01_Git.md) | [量化推理与服务部署](../concepts/inference-deployment.md) |
| 搭建 Jenkins CI/CD 自动化部署流水线 | [02_Jenkins.md](https://github.com/datawhalechina/base-llm/blob/main/docs/chapter15/02_Jenkins.md) | [量化推理与服务部署](../concepts/inference-deployment.md) |

---

## 第五部分：大模型安全

### 第 1 章：安全全景与威胁建模（chapter16/）

| 章节 | 文件 | 对应概念 |
|------|------|---------|
| 大模型安全总览 | [01_LLM_safety_overview.md](https://github.com/datawhalechina/base-llm/blob/main/docs/chapter16/01_LLM_safety_overview.md) | [大模型安全与多模态前沿](../concepts/safety-multimodal.md) |
| 威胁建模及风险分析 | [02_threat_modeling_analysis.md](https://github.com/datawhalechina/base-llm/blob/main/docs/chapter16/02_threat_modeling_analysis.md) | [大模型安全与多模态前沿](../concepts/safety-multimodal.md) |

### 第 2 章：安全工程：对齐与架构设计（建设中）

- 行为对齐工程（未发布）
- 安全架构设计（未发布）

---

## 第六部分：多模态前沿

### 第 1 章：认识多模态边界（chapter19/）

| 章节 | 文件 | 对应概念 |
|------|------|---------|
| 多模态全景概述 | [01_multimodal_definition.md](https://github.com/datawhalechina/base-llm/blob/main/docs/chapter19/01_multimodal_definition.md) | [大模型安全与多模态前沿](../concepts/safety-multimodal.md) |
| 图文多模态 | [02_ViT_CLIP.md](https://github.com/datawhalechina/base-llm/blob/main/docs/chapter19/02_ViT_CLIP.md) | [大模型安全与多模态前沿](../concepts/safety-multimodal.md) |

### 第 2 章：视觉问答（chapter20/）

| 章节 | 文件 | 对应概念 |
|------|------|---------|
| BLIP-2 与 LLaVA | [01_blip2_llava.md](https://github.com/datawhalechina/base-llm/blob/main/docs/chapter20/01_blip2_llava.md) | [大模型安全与多模态前沿](../concepts/safety-multimodal.md) |
| 原生统一架构 | [02_native_unified.md](https://github.com/datawhalechina/base-llm/blob/main/docs/chapter20/02_native_unified.md) | [大模型安全与多模态前沿](../concepts/safety-multimodal.md) |
| 从 0 训练简化版 Omni 模型 | [03_simplified_omni.md](https://github.com/datawhalechina/base-llm/blob/main/docs/chapter20/03_simplified_omni.md) | [大模型安全与多模态前沿](../concepts/safety-multimodal.md) |

---

## 章节统计

| 部分 | 章数 | 已发布节数 |
|------|------|-----------|
| 第一部分：理论篇 | 6 | 19 |
| 第二部分：实战篇 | 2 | 7 |
| 第三部分：微调量化篇 | 3 | 8 |
| 第四部分：应用部署篇 | 2 | 5 |
| 第五部分：大模型安全 | 1（第2章建设中） | 2 |
| 第六部分：多模态前沿 | 2 | 5 |
| **合计** | **16** | **46** |
