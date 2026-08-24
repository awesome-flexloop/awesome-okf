---
okf_version: "0.2"
type: index
title: "Happy-LLM：从零开始构建大模型"
bundle: happy-llm
description: "Datawhale 开源的系统性 LLM 学习教程——从 NLP 基础到 Transformer 架构，从手写 LLaMA2 到 GRPO 强化学习，覆盖 RAG 与 Agent 应用全链路"
concepts:
  - /datawhale/happy-llm/concepts/transformer-architecture
  - /datawhale/happy-llm/concepts/pretrained-language-model
  - /datawhale/happy-llm/concepts/llama2-implementation
  - /datawhale/happy-llm/concepts/model-training
  - /datawhale/happy-llm/concepts/grpo-reinforcement-learning
  - /datawhale/happy-llm/concepts/rag-retrieval-augmented-generation
  - /datawhale/happy-llm/concepts/agent-intelligent-agent
references:
  - /datawhale/happy-llm/references/chapter1-nlp-basics
  - /datawhale/happy-llm/references/chapter2-transformer
  - /datawhale/happy-llm/references/chapter3-plm
  - /datawhale/happy-llm/references/chapter4-llm
  - /datawhale/happy-llm/references/chapter5-build-llm
  - /datawhale/happy-llm/references/chapter6-training-practice
  - /datawhale/happy-llm/references/chapter7-applications
  - /datawhale/happy-llm/references/chapter8-reinforcement-learning
examples:
  - /datawhale/happy-llm/examples/transformer-handwritten
  - /datawhale/happy-llm/examples/llama2-pretrain-sft
  - /datawhale/happy-llm/examples/rag-tinyrag
  - /datawhale/happy-llm/examples/agent-tinyagent
sources: https://github.com/datawhalechina/happy-llm
generated:
  by: okf-wiki-bot
  at: "2026-08-23T00:00:00Z"
verified:
  by: process:seven-concepts-v
  at: "2026-08-23T00:00:00Z"
status: stable
stale_after: "2027-08-23"
---

# Happy-LLM：从零开始构建大模型

[Happy-LLM](https://github.com/datawhalechina/happy-llm) 是 Datawhale 开源的系统性 LLM 学习教程，定位为"深入理解 LLM 核心原理，动手实现你的第一个大模型"。全书 8 章 + Extra-Chapter，从 NLP 基本概念出发，逐层深入 Transformer 架构、预训练语言模型、大语言模型原理，最终引导读者亲手搭建 LLaMA2、完成预训练与微调全流程，并进一步掌握 RAG、Agent 与 GRPO 强化学习等前沿技术。

## 知识地图

```
📖 基础知识（第1-4章）
  ├── NLP 基础概念 → 发展历程、任务分类、文本表示
  ├── Transformer 架构 → 注意力机制、Encoder-Decoder、手写实现
  ├── 预训练语言模型 → BERT(Encoder-only)、T5(Encoder-Decoder)、GPT(Decoder-only)
  └── 大语言模型 → 涌现能力、ICL、指令遵循、三阶段训练
        ↓
🛠️ 实战应用（第5-8章）
  ├── 动手搭建大模型 → 手写 LLaMA2、Tokenizer、Pretrain、SFT
  ├── 大模型训练实践 → Transformers + DeepSpeed + PEFT(LoRA/QLoRA)
  ├── 大模型应用 → 评测、RAG(TinyRAG)、Agent(TinyAgent)
  └── 大模型强化学习 → GRPO、OPD、Search-R1、ReTool
        ↓
🌐 Extra-Chapter → 社区博客贡献（微调实践、架构解读、RAG 增强等）
```

## 核心概念（concepts/）

* [Transformer 架构](concepts/transformer-architecture.md) — 注意力机制（Query/Key/Value）、Self-Attention、Multi-Head Attention、位置编码、Encoder-Decoder 结构，LLM 的架构基石。
* [预训练语言模型](concepts/pretrained-language-model.md) — Encoder-only（BERT/MLM）、Encoder-Decoder（T5）、Decoder-only（GPT/CLM）三种架构范式与预训练-微调范式。
* [LLaMA2 手写实现](concepts/llama2-implementation.md) — 基于 PyTorch 从零实现 LLaMA2：RMSNorm、RoPE、GQA、SwiGLU、Transformer Block、KV Cache。
* [模型训练](concepts/model-training.md) — LLM 三阶段训练（Pretrain→SFT→RLHF）、DeepSpeed 分布式训练、LoRA/QLoRA 高效微调。
* [GRPO 强化学习](concepts/grpo-reinforcement-learning.md) — Group Relative Policy Optimization、组内相对优势估计、RLVR 可验证奖励、从 PPO 到 GRPO 的演进。
* [RAG 检索增强生成](concepts/rag-retrieval-augmented-generation.md) — 检索增强生成原理、文档分块、Embedding、向量检索、Prompt 组装，缓解 LLM 幻觉与知识过时。
* [Agent 智能体](concepts/agent-intelligent-agent.md) — ReAct 推理-行动范式、工具调用、多轮交互、TinyAgent 架构，从问答到自主行动。

## 实战示例（examples/）

* [手写 Transformer 注意力机制](examples/transformer-handwritten.md) — 第2章代码实践：纯 PyTorch 实现 Multi-Head Attention 和完整 Transformer。
* [LLaMA2 模型构建与预训练](examples/llama2-pretrain-sft.md) — 第5章代码实践：ModelConfig、RMSNorm、RoPE、GQA、Tokenizer 训练、DDP 预训练与 SFT。
* [TinyRAG 检索增强生成](examples/rag-tinyrag.md) — 第7章 RAG 实践：Embeddings、VectorBase、LLM 调用的完整 RAG 链路。
* [TinyAgent 智能体工具调用](examples/agent-tinyagent.md) — 第7章 Agent 实践：核心调度、工具注册、Streamlit Web Demo。

## 信源登记（references/）

* [第一章 NLP 基础概念](references/chapter1-nlp-basics.md) — NLP 定义、发展历程、任务分类、文本表示方法演进。
* [第二章 Transformer 架构](references/chapter2-transformer.md) — 注意力机制原理、Encoder-Decoder 结构、手写 Transformer 代码。
* [第三章 预训练语言模型](references/chapter3-plm.md) — BERT/T5/GPT 三种架构、预训练任务设计、主流模型对比。
* [第四章 大语言模型](references/chapter4-llm.md) — LLM 定义与能力、涌现能力、三阶段训练流程。
* [第五章 动手搭建大模型](references/chapter5-build-llm.md) — LLaMA2 手写实现、Tokenizer、预训练与 SFT 全流程代码。
* [第六章 大模型训练实践](references/chapter6-training-practice.md) — Transformers 框架、DeepSpeed、LoRA/QLoRA 工业级训练。
* [第七章 大模型应用](references/chapter7-applications.md) — LLM 评测体系、RAG 检索增强、Agent 智能体。
* [第八章 大模型强化学习](references/chapter8-reinforcement-learning.md) — GRPO、OPD、Search-R1、ReTool Agentic RL 实践。

## 深度洞察

本知识束的设计决策与核心洞察详见 [spec/insights.md](spec/insights.md)，包括：

1. **手写实现驱动的双层学习路径**——先 PyTorch 手写建立心智模型，后 Transformers 框架建立工程能力
2. **从 Transformer 到 LLaMA2 的架构演进主线**——RNN→Transformer→BERT/GPT→LLaMA2 的持续优化链
3. **训练 vs 推理的分野**——三阶段训练赋予能力，RAG/Agent 在推理时释放能力
4. **从 RAG 到 Agentic RL 的应用递进**——知识增强→工具调用→环境交互强化学习的闭环

## 目录结构

```
happy-llm/
├── spec/
│   ├── facts.md              # 章节结构与代码资产事实清单
│   └── insights.md           # 4 个核心设计洞察
├── concepts/                 # 7 个核心概念
│   ├── index.md
│   ├── transformer-architecture.md
│   ├── pretrained-language-model.md
│   ├── llama2-implementation.md
│   ├── model-training.md
│   ├── grpo-reinforcement-learning.md
│   ├── rag-retrieval-augmented-generation.md
│   └── agent-intelligent-agent.md
├── examples/                 # 4 个实战示例
│   ├── index.md
│   ├── transformer-handwritten.md
│   ├── llama2-pretrain-sft.md
│   ├── rag-tinyrag.md
│   └── agent-tinyagent.md
├── references/               # 8 章信源登记
│   ├── index.md
│   └── chapter1-8 ... .md
├── index.md                  # 本文件
└── log.md                    # 更新日志
```

---

> **源码位置**：`external/libs/ai/datawhalechina/happy-llm/`
>
> **在线阅读**：https://datawhalechina.github.io/happy-llm/
>
> **开源协议**：CC BY-NC-SA 4.0
>
> **生成时间**：2026-08-23 | **维护者**：OKF Wiki Bot

```{toctree}
:hidden:

concepts/index
examples/index
references/index
spec/facts
spec/insights
log
```
