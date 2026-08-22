# insights.md — base-llm 核心洞察

> 基于 facts.md 提炼，四阶段方法论 I 阶段产出。

## I-01：从 NLP 到 LLM 的演进是一条"表示能力→序列建模→并行架构→规模涌现"的必然脉络

base-llm 并非简单堆砌技术名词，而是沿着一条清晰的内在逻辑展开：词向量（Word2Vec）解决了"词语如何表示为计算机可处理的稠密向量"问题；RNN/LSTM 解决了"序列信息如何顺序传递"问题，但受限于顺序计算和长距离依赖衰减；Attention 机制通过动态加权缓解了信息瓶颈；Transformer 以自注意力彻底抛弃循环结构，实现并行计算和全局依赖建模，成为大模型的架构基石；BERT/GPT/T5 三条预训练路线验证了"大规模预训练+下游微调"范式的有效性；最终 GPT-3/ChatGPT 通过规模涌现和 RLHF 对齐迈入 LLM 时代。每一步技术跃迁都在解决前一代的核心瓶颈，这条脉络是理解整个教程的主线。

## I-02：Transformer 是贯穿全文的架构中枢，理论篇与实战篇均围绕其展开

Transformer 在教程中处于承上启下的核心位置。第 4 章深入剖析自注意力（Q/K/V 同源）、多头注意力、位置编码、Encoder-Decoder 架构和前馈网络；第 5 章的 BERT/GPT/T5 本质上是 Transformer 架构的三种变体（Encoder-only/Decoder-only/Encoder-Decoder）；第 6 章手搓 Llama2 是在 Decoder-only 路线上引入 RoPE、RMSNorm、SwiGLU、GQA 等现代改进；MoE 则是在 Transformer 基础上引入稀疏激活扩展参数规模。代码目录 code/C4/transformer/ 和 code/C6/llama2/ 提供了从标准 Transformer 到现代 LLM 的手写实现对照，使读者能直观看到架构演进。

## I-03：微调技术形成"全量微调→PEFT→LoRA/QLoRA→RLHF/DPO"的效率与对齐双维谱系

教程第三部分（chapter11-13）展现了微调技术的两个演进维度。在参数效率维度：全量微调需更新所有参数，成本高昂；PEFT 通过 Adapter/Prompt Tuning 等方式冻结原模型只训练少量参数；LoRA 以低秩分解 ΔW=BA 直接作用于权重矩阵，实现千分之一参数量且零推理延迟（训练后可合并）；QLoRA 进一步结合 4-bit 量化降低显存。在对齐维度：SFT 让模型学会指令遵循；RLHF 通过奖励模型+PPO 让模型输出符合人类偏好；DPO 作为 RLHF 的简化方案绕过显式奖励模型。LLaMA-Factory 提供了这些技术的工程化实践框架。

## I-04：部署优化路径遵循"模型压缩→服务化→容器化→自动化"的工程递进

第四部分（chapter14-15）构建了从模型到生产服务的完整工程链路。模型压缩层：量化（INT8/INT4）和 DeepSpeed 分布式训练降低资源门槛；服务化层：FastAPI 将模型封装为 HTTP 接口，支持同步/异步推理；容器化层：Docker Compose 实现环境一致性和多服务编排；云部署层：uv 在 Linux 云服务器上管理 Python 环境和进程；自动化层：Git 版本控制+Jenkins CI/CD 实现模型服务的持续集成与部署。code/C14/ner_deployment/ 是一个完整的 NER 服务部署范例，包含 Dockerfile、docker-compose.yml 和 FastAPI 应用，体现了"训练→部署"的闭环。

## I-05：安全与多模态代表 LLM 的两个前沿延伸——可靠性保障与能力边界拓展

第五、六部分（chapter16, 19-20）探讨 LLM 走出实验室后面临的两大方向。安全维度从全景概览到威胁建模（STRIDE 等方法论），识别提示注入、数据泄露、越狱等风险，后续将延伸至行为对齐工程和安全架构设计。多模态维度则沿着"视觉编码器（ViT）→图文对齐（CLIP）→视觉语言模型（BLIP-2/LLaVA）→原生统一架构→从零训练 Omni 模型"的路线递进，code/C20/seeker-omni/ 提供了包含数据准备、模型定义（attention/block/lm/projector/resampler）、训练循环（SFT/e2e distill）的完整多模态模型训练项目，展示了 LLM 从纯文本走向图文统一的技术路径。

## 知识地图

```
base-llm 知识束
│
├── 概念层（8 篇）
│   ├── nlp-basics          ← C1: NLP 概述/发展历程/技术层次
│   ├── word-vectors-rnn    ← C2+C3: 分词/词向量/Word2Vec/RNN/LSTM
│   ├── transformer         ← C4: Seq2Seq/Attention/Transformer
│   ├── pretrained-models   ← C5: BERT/GPT/T5/HuggingFace
│   ├── llm-architecture    ← C6: Llama2/MoE/生成策略/ICL
│   ├── finetuning-alignment← C11+C12: PEFT/LoRA/QLoRA/RLHF/DPO
│   ├── inference-deployment← C13+C14+C15: 量化/DeepSpeed/FastAPI/Docker/CI-CD
│   └── safety-multimodal   ← C16+C19+C20: 安全/ViT-CLIP/BLIP2-LLaVA/Omni
│
├── 示例层（登记 code/ 下代码）
│   └── examples/index.md   ← C2-C20 共 11 个代码目录
│
└── 信源层（登记 docs/ 章节）
    └── references/index.md ← 六大部分 20+ 章节
```
