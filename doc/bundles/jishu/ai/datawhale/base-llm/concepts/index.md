# 概念文档

本目录包含 base-llm 教程的 8 个核心概念文档，按六大部分组织：从 NLP 基础到多模态前沿逐步深入。

## 一、NLP 基础

* [NLP 基础与发展历程](nlp-basics.md) — NLP 定义与核心任务（NLU/NLG）、技术四层次（词法/句法/语义/语用）、发展四阶段（规则→统计→深度学习→LLM）、关键里程碑（Word2Vec→Transformer→BERT→GPT→ChatGPT）、环境准备。

## 二、词向量与序列模型

* [词向量与循环神经网络](word-vectors-rnn.md) — 分词技术（jieba/用户词典）、词向量表示（One-hot→分布式表示）、Word2Vec（CBOW/Skip-gram/Hierarchical Softmax/Negative Sampling）、Gensim 实战、RNN 原理与梯度问题、LSTM 三门控机制、GRU 简化门控。

## 三、Transformer 与预训练

* [Transformer 架构](transformer.md) — Seq2Seq 编码器-解码器框架与信息瓶颈、注意力机制（Q/K/V 范式/Bahdanau/Luong）、自注意力 vs 交叉注意力、缩放点积注意力、多头注意力、位置编码（正弦/可学习）、位置前馈网络、残差连接与层归一化、Encoder-Decoder 完整堆叠、手写 Transformer 实现。
* [预训练语言模型](pretrained-models.md) — BERT（Encoder-only/MLM/NSP/输入表示/微调范式）、GPT（Decoder-only/自回归语言模型/生成式预训练）、T5（Encoder-Decoder/文本到文本统一框架）、Hugging Face 生态（Transformers/Tokenizers/Datasets/Accelerate）、模型缓存与 Bucket ID。
* [大模型架构深入](llm-architecture.md) — 手搓 Llama2（RoPE 旋转位置编码/RMSNorm/SwiGLU 激活/GQA 分组查询注意力/KV Cache）、MoE 混合专家（稀疏激活/路由机制/负载均衡）、文本生成策略（Greedy/Beam Search/Top-k/Top-p/Temperature/Repetition Penalty）、上下文学习（Zero-shot/Few-shot/CoT）与提示词工程。

## 四、微调与对齐

* [参数高效微调与人类对齐](finetuning-alignment.md) — PEFT 技术谱系（Adapter Tuning/Prefix Tuning/Prompt Tuning/P-Tuning）、LoRA 低秩分解（ΔW=BA/秩选择/缩放因子α/零推理延迟合并）、QLoRA（4-bit NF4/双重量化/分页优化器）、RLHF 三阶段（SFT 监督微调→RM 奖励模型→PPO 强化学习）、DPO 直接偏好优化、LLaMA-Factory 框架实战、Qwen2.5 私有数据微调。

## 五、高效推理与部署

* [量化推理与服务部署](inference-deployment.md) — 模型量化原理（FP16→INT8/INT4/PTQ/QAT/AWQ/GPTQ）、LLM Compressor 实战、DeepSpeed 分布式训练（ZeRO 三阶段/混合精度/梯度累积）、FastAPI 模型服务化（同步/异步/路由）、uv Python 包管理器与 Linux 云部署、Docker Compose 容器化编排、Git 版本控制、Jenkins CI/CD 自动化流水线。

## 六、安全与多模态

* [大模型安全与多模态前沿](safety-multimodal.md) — LLM 安全全景（传统安全/对齐安全/系统安全）、威胁建模（STRIDE/攻击树）、提示注入/越狱/数据泄露/幻觉风险分析、多模态定义与分类、ViT 视觉 Transformer（Patch Embedding/分类标记）、CLIP 图文对比学习（双塔架构/零样本分类）、BLIP-2（Q-Former/桥接模块）、LLaVA（视觉指令微调）、原生统一架构、从零训练简化版 Omni 模型（seeker-omni 项目）。

```{toctree}
:hidden:
:maxdepth: 7

finetuning-alignment
inference-deployment
llm-architecture
nlp-basics
pretrained-models
safety-multimodal
transformer
word-vectors-rnn
```
