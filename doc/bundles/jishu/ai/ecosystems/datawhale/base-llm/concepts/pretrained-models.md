---
type: concept
title: "预训练语言模型"
bundle: "/datawhale/base-llm"
description: "BERT（Encoder-only）、GPT（Decoder-only）、T5（Encoder-Decoder）三条预训练路线，以及 Hugging Face 生态系统的核心库与使用范式。"
sources:
  - https://github.com/datawhalechina/base-llm/blob/main/docs/chapter5/13_Bert.md
  - https://github.com/datawhalechina/base-llm/blob/main/docs/chapter5/14_GPT.md
  - https://github.com/datawhalechina/base-llm/blob/main/docs/chapter5/15_T5.md
  - https://github.com/datawhalechina/base-llm/blob/main/docs/chapter5/16_HuggingFace.md
related:
  - /datawhale/base-llm/concepts/transformer
  - /datawhale/base-llm/concepts/llm-architecture
  - /datawhale/base-llm/concepts/finetuning-alignment
---

# 预训练语言模型

## 核心理解

Transformer 架构确立后，预训练语言模型（Pre-trained Language Model, PLM）沿三条路线发展：**BERT** 采用 Encoder-only 架构，擅长自然语言理解；**GPT** 采用 Decoder-only 架构，擅长自然语言生成；**T5** 采用 Encoder-Decoder 架构，将所有 NLP 任务统一为文本到文本格式。三者共同奠定了"预训练+微调"的新范式，而 Hugging Face 生态则将这些模型的使用门槛降到了极低。

## 预训练-微调范式

传统 NLP 针对每个任务从零训练模型。预训练范式分两阶段：

1. **预训练**：在大规模无标注语料上，通过自监督任务（如掩码语言模型、下一个词预测）训练通用语言表示。
2. **微调**：在下游任务的小规模标注数据上，以预训练权重为初始化，微调全部或部分参数。

优势：预训练学到的通用语言知识可迁移到各类下游任务，大幅减少标注数据需求和训练成本。

## BERT（Encoder-only）

### 架构特点

- 仅使用 Transformer **Encoder**，双向自注意力可看到每个位置的左右上下文。
- 输入表示 = Token Embedding + Segment Embedding + Position Embedding。
- 特殊标记：`<[BOS_never_used_51bce0c785ca2f68081bfa7d91973934]>`（分类标记，其输出向量用于句子级任务）、`[SEP]`（分隔符）、`[MASK]`（掩码标记）。

### 预训练任务

**1. 掩码语言模型（Masked Language Model, MLM）**

随机掩码 15% 的词元，让模型预测被掩码的词。在这 15% 中：
- 80% 替换为 `[MASK]`
- 10% 替换为随机词
- 10% 保持不变

MLM 使模型必须利用双向上下文进行预测，学到深层语义表示。

**2. 下一句预测（Next Sentence Prediction, NSP）**

给定句子对 (A, B)，判断 B 是否是 A 的下一句。50% 为真实下一句，50% 为随机句子。NSP 旨在学习句子间关系（后续研究表明其作用有限，RoBERTa 等模型移除了该任务）。

### 应用与微调

BERT 在问答（SQuAD）、自然语言推理（MNLI）、命名实体识别等理解类任务上取得突破。微调时在 `<[BOS_never_used_51bce0c785ca2f68081bfa7d91973934]>` 输出上接分类层，或在每个 token 输出上接序列标注层。

## GPT（Decoder-only）

### 架构特点

- 仅使用 Transformer **Decoder**，但移除了交叉注意力层（无需 Encoder）。
- **因果掩码（Causal Mask）**：自注意力中每个位置只能关注当前位置及之前的位置，确保自回归生成的因果性。

### 预训练任务

**自回归语言模型（Autoregressive Language Model）**：给定前文，预测下一个词：

$$P(x_1, x_2, ..., x_n) = \prod_{i=1}^{n} P(x_i | x_{<i})$$

GPT 系列的演进：
- **GPT-1（2018）**：1.17 亿参数，验证生成式预训练+判别式微调。
- **GPT-2（2019）**：15 亿参数，展示零样本（Zero-shot）能力。
- **GPT-3（2020）**：1750 亿参数，展示少样本（Few-shot）上下文学习能力，标志 LLM 时代到来。

## T5（Encoder-Decoder）

### 核心理念：Text-to-Text

T5 将所有 NLP 任务统一为**文本到文本**格式：
- 翻译：`translate English to German: Hello` → `Hallo`
- 分类：`sst2 sentence: This movie is great` → `positive`
- 摘要：`summarize: [long text]` → `[summary]`

### 架构与预训练

- 完整 Encoder-Decoder Transformer 架构。
- 预训练任务为 **Span Corruption**：随机遮蔽连续文本片段，用哨兵标记替换，让 Decoder 重建被遮蔽的片段。
- T5 系统性研究了预训练的各设计选择（模型架构、训练目标、数据、迁移策略）。

### 三条路线对比

| 特性 | BERT | GPT | T5 |
|------|------|-----|-----|
| 架构 | Encoder-only | Decoder-only | Encoder-Decoder |
| 注意力 | 双向 | 单向（因果） | Encoder 双向/Decoder 单向 |
| 预训练任务 | MLM + NSP | 自回归 LM | Span Corruption |
| 擅长 | 理解类任务 | 生成类任务 | 序列到序列任务 |
| 代表模型 | BERT/RoBERTa | GPT/Llama | T5/BART |

## Hugging Face 生态

Hugging Face 已成为大模型时代的"基础设施"，核心库包括：

### Transformers

提供数千个预训练模型的统一接口：
- `AutoTokenizer`：自动加载对应分词器。
- `AutoModel`/`AutoModelForCausalLM`/`AutoModelForSequenceClassification`：自动加载模型。
- `pipeline()`：一行代码完成推理（文本分类、问答、生成等）。
- `Trainer`：封装训练循环，支持分布式训练、混合精度等。

### 其他核心库

| 库 | 用途 |
|----|------|
| **Tokenizers** | 高性能分词器（Rust 后端），支持 BPE/WordPiece/SentencePiece |
| **Datasets** | 数据集加载与处理，内存映射、缓存、流式读取 |
| **Evaluate** | 模型评估指标库 |
| **Accelerate** | 简化分布式训练和混合精度代码 |
| **PEFT** | 参数高效微调（LoRA 等） |
| **BitsAndBytes** | 量化加载（4-bit/8-bit） |

### 使用范式

```python
from transformers import AutoTokenizer, AutoModelForCausalLM

tokenizer = AutoTokenizer.from_pretrained("gpt2")
model = AutoModelForCausalLM.from_pretrained("gpt2")
inputs = tokenizer("Hello, I'm", return_tensors="pt")
outputs = model.generate(**inputs, max_length=50)
```

### 代码示例

`code/C5/` 目录提供了：
- `01_bert_usage.py` — BERT 模型加载与使用
- `02_gpt_usage.py` — GPT 模型加载与文本生成
- `03_t5_usage.py` — T5 模型加载与文本到文本任务
- `03_bucket_id.py` — Bucket ID 机制
- `04_hf_usage.ipynb` — Hugging Face 综合实战

### 模型缓存与 Bucket ID

Hugging Face 模型默认缓存到本地（`~/.cache/huggingface/`）。Bucket ID 是 Hugging Face Hub 上模型的唯一标识（如 `bert-base-uncased`、`gpt2`、`t5-small`），用于自动下载和加载模型。

## 延伸阅读

- 前置：[Transformer 架构](transformer.md)——三条路线的共同基础
- 后续：[大模型架构深入](llm-architecture.md)——Decoder-only 路线的现代演进
- 微调：[参数高效微调与人类对齐](finetuning-alignment.md)
- 示例代码：[C5 预训练模型代码](../examples/index.md#c5-预训练模型)
