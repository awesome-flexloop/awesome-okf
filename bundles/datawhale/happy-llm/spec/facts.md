---
type: spec
title: Happy-LLM 事实清单
bundle: /datawhale/happy-llm
sources: https://github.com/datawhalechina/happy-llm
---

# Happy-LLM 事实清单

## 项目元信息

F-001: Happy-LLM 是 Datawhale 开源的系统性 LLM 学习教程，定位为"从零开始构建大模型"，旨在帮助读者深入理解大语言模型原理并动手实现第一个大模型。项目负责人为宋志学（KMnO4-zx）和邹雨衡（logan-zou），指导专家为朱信忠。

F-002: 项目源码位于 `external/libs/ai/datawhalechina/happy-llm`，文档位于 `docs/` 目录，采用 docsify 架构（`_sidebar.md` + `index.html`），在线阅读地址为 https://datawhalechina.github.io/happy-llm/。

F-003: 项目分为两大部分：基础知识（第1-4章）与实战应用（第5-8章），另含 Extra-Chapter（社区博客贡献）。全书覆盖从 NLP 基础到 Agentic RL 的完整 LLM 知识链路。

F-004: 按章节拆分依赖（`requirements.txt`），不同章节建议使用独立 Python 环境。第2-7章推荐 Python 3.10/3.11，第8章使用 Python 3.13 并依赖 PyTRIO 0.2.6。

## 章节结构（与 _sidebar.md 一致）

F-005: **学习与环境准备**（`docs/学习与环境准备.md`）——分章依赖说明、硬件建议、第6章和第8章快速开始指南、常见问题。

F-006: **前言**（`docs/前言.md`）——项目缘起（承接 self-llm 和 llm-universe）、LLM 发展背景、写给读者的建议、全书结构说明。

F-007: **第一章 NLP 基础概念**（`docs/chapter1/第一章 NLP基础概念.md`）——什么是 NLP、发展历程（符号主义→统计学习→深度学习→预训练模型→大模型）、任务分类、文本表示演进（VSM→Word2Vec→ELMo→BERT）。

F-008: **第二章 Transformer 架构**（`docs/chapter2/第二章 Transformer架构.md`）——注意力机制（Query/Key/Value）、Self-Attention、Multi-Head Attention、位置编码（Sinusoidal）、Encoder-Decoder 结构、手把手搭建 Transformer（含 `code/transformer.py`）。

F-009: **第三章 预训练语言模型**（`docs/chapter3/第三章 预训练语言模型.md`）——Encoder-only（BERT：MLM+NSP、WordPiece、GELU）、Encoder-Decoder（T5）、Decoder-Only（GPT 系列）三种架构对比，主流 LLM 架构思想。

F-010: **第四章 大语言模型**（`docs/chapter4/第四章 大语言模型.md`）——LLM 定义（数百亿参数、数T token语料）、涌现能力、上下文学习（ICL）、指令遵循、逐步推理（CoT）、多语言/长文本/多模态/幻觉等特点、三阶段训练流程（Pretrain→SFT→RLHF）。

F-011: **第五章 动手搭建大模型**（`docs/chapter5/第五章 动手搭建大模型.md`）——基于 PyTorch 手写 LLaMA2（ModelConfig、RMSNorm、RoPE、GQA、SwiGLU、Transformer Block）、训练 Tokenizer（BPE）、数据处理（`dataset.py`、`deal_dataset.py`）、预训练（`ddp_pretrain.py`）、SFT（`ddp_sft_full.py`）、模型导出（`export_model.py`）。产出 Happy-LLM-Chapter5-Base/SFT-215M 模型。

F-012: **第六章 大模型训练流程实践**（`docs/chapter6/第六章 大模型训练流程实践.md`）——Transformers 框架（AutoModel、Trainer）、DeepSpeed 分布式训练（ZeRO-2 配置）、预训练实践（`pretrain.py`/`pretrain.sh`）、有监督微调（`finetune.py`/`finetune.sh`）、LoRA/QLoRA 高效微调（PEFT），另含 6.4 偏好对齐（WIP）和实践说明（`readme.md`）。

F-013: **第七章 大模型应用**（`docs/chapter7/第七章 大模型应用.md`）——LLM 评测（MMLU/GSM8K/ARC/HellaSwag 等评测集、Open LLM Leaderboard/Lmsys Chatbot Arena/OpenCompass 榜单、垂直领域榜单）、RAG 检索增强生成（TinyRAG 实现：Embeddings、VectorBase、LLM 调用）、Agent 智能体（TinyAgent：核心调度、工具调用、Streamlit Web Demo）。

F-014: **第八章 大模型强化学习**（`docs/chapter8/第八章 大模型强化学习.md`）——GRPO（Group Relative Policy Optimization，组内相对优势估计，省去 Value Model）、OPD（On-Policy Distillation，Student 在自身分布上获得 Teacher 逐 token 指导）、Search-R1（搜索引擎环境的 Agentic RL）、ReTool（代码解释器环境的 Agentic RL，含 sandbox 沙箱）。全部示例使用 PyTRIO 远端采样+训练，本地仅负责数据处理与环境交互。

F-015: **Extra-Chapter**（`Extra-Chapter/`）——社区贡献博客，包含：微调小模型的意义、Transformer 模块设计解读、文本数据处理详解、Qwen3-VL 拼接微调、S1 Thinking Budget with vLLM、CDDRS 增强 RAG 检索方法、大模型 Token 生成方式等。

## 代码资产

F-016: 第二章代码（`docs/chapter2/code/transformer.py`）——纯 PyTorch 手写 Transformer 实现，含注意力机制、Encoder、Decoder。

F-017: 第五章代码（`docs/chapter5/code/`）——`k_model.py`（LLaMA2 模型定义）、`model_sample.py`（模型采样）、`train_tokenizer.py`（Tokenizer 训练）、`dataset.py`/`deal_dataset.py`（数据处理）、`ddp_pretrain.py`/`ddp_sft_full.py`（DDP 训练）、`export_model.py`（HuggingFace 格式导出）。

F-018: 第六章代码（`docs/chapter6/code/`）——`download_model.py`/`download_dataset.py`（资源下载）、`pretrain.py`/`pretrain.sh`（预训练）、`finetune.py`/`finetune.sh`（SFT/PEFT 微调）、`ds_config_zero2.json`（DeepSpeed 配置）、Jupyter Notebook（`pretrain.ipynb`、`process_dataset.ipynb`、`whole.ipynb`）。

F-019: 第七章 RAG 代码（`docs/chapter7/RAG/`）——`Embeddings.py`（嵌入模型）、`VectorBase.py`（向量数据库）、`LLM.py`（大模型调用）、`utils.py`（工具函数）、`demo.py`（命令行演示）。

F-020: 第七章 Agent 代码（`docs/chapter7/Agent/`）——`src/core.py`（Agent 核心逻辑）、`src/tools.py`（工具定义）、`src/utils.py`（工具函数）、`demo.py`（命令行演示）、`web_demo.py`（Streamlit Web 界面）。

F-021: 第八章代码（`docs/chapter8/`）——`grpo/`（同步/异步 GRPO 示例）、`opd/`（同步/异步 OPD 示例）、`search-r1/`（搜索引擎 RL：data/protocol/reward/rollout/search/train/eval）、`retool/`（代码执行 RL：data/protocol/reward/rollout/sandbox/train/eval/analysis）。

## 模型与资源

F-022: 开源模型 Happy-LLM-Chapter5-Base-215M 和 Happy-LLM-Chapter5-SFT-215M，托管于 ModelScope（kmno4zx/happy_llm-215M-base、kmno4zx/happy_llm-215M-sft），并提供创空间在线体验。

F-023: PDF 教程完全开源免费（CC BY-NC-SA 4.0），发布于 GitHub Releases v1.0.2，预添加 Datawhale 水印。配套教学 PPT 托管于 github.com/HZAI-ZJNU/happy-llm-ppt。

## 学习路径

F-024: 基础知识路径：第1章 NLP 基础 → 第2章 Transformer 架构 → 第3章 预训练语言模型（Encoder-only/Encoder-Decoder/Decoder-Only）→ 第4章 大语言模型（能力与三阶段训练）。

F-025: 实战应用路径：第5章 手写 LLaMA2（PyTorch 底层）→ 第6章 Transformers 框架训练（工业级）→ 第7章 应用层（评测/RAG/Agent）→ 第8章 Agentic RL（GRPO/OPD/Search-R1/ReTool）。
