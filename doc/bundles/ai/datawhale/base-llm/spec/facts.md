# facts.md — base-llm 知识包事实清单

> 来源：https://github.com/datawhalechina/base-llm
> 采集时间：2026-08-23
> 采集方式：阅读 README.md、docs/README.md、docs/_sidebar.md，LS docs/ 与 code/ 目录

## 一、项目基本信息

- **F-001**：项目名称 base-llm，全称"从 NLP 到 LLM 的算法全栈教程"，口号"Base LLM is all you need"。
- **F-002**：由 Datawhale 社区维护，项目负责人 dalvqw（FutureUnreal）。
- **F-003**：许可证 CC BY-NC-SA 4.0（知识共享署名-非商业性使用-相同方式共享 4.0）。
- **F-004**：要求 Python 3.10+，基于 PyTorch 框架。
- **F-005**：在线阅读地址 https://datawhalechina.github.io/base-llm/ 。

## 二、章节结构（C1-C20+）

教程按六大部分组织，章节编号存在跳号（缺 C9/C10/C17/C18），共 20 个章节目录。

### 第一部分：理论篇

- **F-010**：第 1 章 NLP 简介（chapter1/）
  - 01_nlp_intro.md — NLP 概述
  - 02_preparation.md — 环境准备
- **F-011**：第 2 章 文本表示与词向量（chapter2/）
  - 03_tokenization.md — 初级分词技术
  - 04_word_vector.md — 词向量表示
  - 05_Word2Vec.md — 从主题模型到 Word2Vec
  - 06_gensim.md — 基于 Gensim 的词向量实战
- **F-012**：第 3 章 循环神经网络（chapter3/）
  - 08_RNN.md — 循环神经网络
  - 09_LSTM&GRU.md — LSTM 与 GRU
- **F-013**：第 4 章 注意力机制与 Transformer（chapter4/）
  - 10_seq2seq.md — Seq2Seq 架构
  - 11_attention.md — 注意力机制
  - 12_transformer.md — 深入解析 Transformer
- **F-014**：第 5 章 预训练模型（chapter5/）
  - 13_Bert.md — BERT 结构及应用
  - 14_GPT.md — GPT 结构及应用
  - 15_T5.md — T5 结构及应用
  - 16_HuggingFace.md — Hugging Face 生态与核心库
- **F-015**：第 6 章 深入大模型架构（chapter6/）
  - 17_handcraft_llama2.md — 手搓一个大模型（Llama2）
  - 18_MoE.md — MoE 架构解析
  - 19_text_generation.md — 手撕大模型生成策略
  - 20_in_context_learning.md — 上下文学习与提示词技术

### 第二部分：实战篇

- **F-020**：第 1 章 文本分类（chapter7/）
  - 01_text_classification.md — 文本分类简单实现
  - 02_lstm_text_classification.md — 基于 LSTM 的文本分类
  - 03_bert_text_classification.md — 微调 BERT 模型进行文本分类
- **F-021**：第 2 章 命名实体识别（chapter8/）
  - 01_named_entity_recognition.md — 命名实体识别概要
  - 02_data_processing.md — NER 项目的数据处理
  - 03_model_building_and_training.md — 模型构建、训练与推理
  - 04_evaluation_and_prediction.md — 模型的推理与优化

### 第三部分：微调量化篇

- **F-030**：第 1 章 参数高效微调（chapter11/）
  - 01_PEFT.md — PEFT 技术综述
  - 02_lora.md — LoRA 方法详解
  - 03_peft_lora.md — 基于 peft 库的 LoRA 实战
  - 04_qwen2.5_qlora.md — Qwen2.5 微调私有数据
- **F-031**：第 2 章 高级微调技术（chapter12/）
  - 01_RLHF.md — RLHF 技术详解
  - 02_llama_factory.md — LLaMA-Factory RLHF（DPO）实战
- **F-032**：第 3 章 大模型训练与量化（chapter13/）
  - 01_quantization.md — 模型量化实战
  - 02_deepspeed.md — Deepspeed 框架介绍

### 第四部分：应用部署篇

- **F-040**：第 1 章 模型服务部署（chapter14/）
  - 01_fastapi.md — FastAPI 模型部署实战
  - 02_uv_linux.md — 云服务器模型部署实战
  - 03_docker_deploy.md — 使用 Docker Compose 部署模型服务
- **F-041**：第 2 章 自动化与性能优化（chapter15/）
  - 01_Git.md — Git 与 GitHub 版本控制基础
  - 02_Jenkins.md — 搭建 Jenkins CI/CD 自动化部署流水线

### 第五部分：大模型安全

- **F-050**：第 1 章 安全全景与威胁建模（chapter16/）
  - 01_LLM_safety_overview.md — 大模型安全总览
  - 02_threat_modeling_analysis.md — 威胁建模及风险分析
- **F-051**：第 2 章 安全工程：对齐与架构设计（建设中，未发布）

### 第六部分：多模态前沿

- **F-060**：第 1 章 认识多模态边界（chapter19/）
  - 01_multimodal_definition.md — 多模态全景概述
  - 02_ViT_CLIP.md — 图文多模态（ViT/CLIP）
- **F-061**：第 2 章 视觉问答（chapter20/）
  - 01_blip2_llava.md — BLIP-2 与 LLaVA
  - 02_native_unified.md — 原生统一架构
  - 03_simplified_omni.md — 从 0 训练简化版 Omni 模型

### Extra-chapter

- **F-070**：Extra-chapter/minimax-api-tutorial/ — MiniMax API 教程（基础对话/流式/多轮/长上下文）

## 三、代码示例位置（code/ 目录）

- **F-080**：code/C2/ — jieba 分词（01_jieba.py）、Gensim 词向量（04_gensim.ipynb）、用户词典
- **F-081**：code/C3/ — RNN 实现（01_RNN.py）、LSTM 实现（02_LSTM.py）
- **F-082**：code/C4/ — Seq2Seq（01_Seq2Seq.py）、注意力（02_attention.py）、自注意力（03_Self-Attention.py）、transformer/ 手写 Transformer 模块（src/attention.py, ffn.py, norm.py, pos.py, transformer.py, main.py）
- **F-083**：code/C5/ — BERT 使用（01_bert_usage.py）、GPT 使用（02_gpt_usage.py）、T5 使用（03_t5_usage.py）、bucket_id（03_bucket_id.py）、HuggingFace 实战（04_hf_usage.ipynb）
- **F-084**：code/C6/ — llama2/ 手写 Llama2（src/attention.py, ffn.py, norm.py, rope.py, transformer.py, main.py）、MoE/ 手写 MoE（src/ 同结构）
- **F-085**：code/C7/ — 文本分类三个 notebook（朴素实现/LSTM/BERT）
- **F-086**：code/C8/ — NER 完整项目：src/ 下 configs/data/loss/metrics/tokenizer/trainer/utils 模块，01-06 脚本（构建类别/构建词表/数据加载/模型/训练/预测），CMeEE-V2 数据集
- **F-087**：code/C11/ — PEFT Pythia-2.8b（03_peft_pythia-2.8b.ipynb）、数据集生成（04_dataset_gen.ipynb）、Qwen2.5 QLoRA（04_qwen2.5_qlora.ipynb）、Qwen2.5 测试（04_qwen2.5_test.ipynb）、blackwukong 数据集
- **F-088**：code/C13/ — Qwen2.5 LLM Compressor 量化（01_qwen2.5_llmcompressor.ipynb）
- **F-089**：code/C14/ — NER 部署项目（ner_deployment/：FastAPI main.py、predict.py、Dockerfile、docker-compose.yml、tokenizer/）、01_main.py、01_test.py
- **F-090**：code/C19/ — CLIP 实现（02_clip.py）
- **F-091**：code/C20/ — seeker-omni/ 从零训练简化版 Omni 模型：configs/（model/stages）、dataprep/（download/prepare）、seeker_omni/（dataset/model/steps/train）、pyproject.toml

## 四、核心主题脉络

- **F-100**：NLP 技术四层次：词法分析→句法分析→语义分析→语用分析。
- **F-101**：NLP 发展四阶段：规则时代（1960s-1980s）→统计时代（1990s-2000s）→深度学习时代（2010s-）→大语言模型时代（2020-）。
- **F-102**：关键里程碑：Word2Vec（2013）→Attention（2014）→Transformer（2017）→BERT（2018）→GPT-3（2020）→ChatGPT（2022）。
- **F-103**：Transformer 核心：自注意力机制（Q/K/V 同源）、多头注意力、位置编码、Encoder-Decoder 架构、残差连接+层归一化。
- **F-104**：预训练模型三大路线：BERT（Encoder-only/双向掩码）、GPT（Decoder-only/自回归）、T5（Encoder-Decoder/文本到文本）。
- **F-105**：LoRA 核心：低秩分解 ΔW=BA，秩 r≪min(d,k)，A 高斯初始化 B 零初始化，训练后可合并回原权重实现零推理延迟。
- **F-106**：RLHF 三阶段：监督微调（SFT）→奖励模型（RM）训练→PPO 强化学习对齐。
- **F-107**：量化技术：降低权重精度（FP16→INT8/INT4）减少显存和计算，LLM Compressor 等工具支持。
- **F-108**：部署技术栈：FastAPI 服务化→uv/Linux 云服务器→Docker Compose 容器化→Jenkins CI/CD。
- **F-109**：多模态路线：ViT/CLIP（图文对齐）→BLIP-2/LLaVA（视觉问答）→原生统一架构→从零训练 Omni。
