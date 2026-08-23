# 实战示例

本目录包含 4 个实战示例，对应 Happy-LLM 教程中的核心代码实践，覆盖从架构手写、模型训练到应用开发的完整链路。

* [手写 Transformer 注意力机制](transformer-handwritten.md) — 第二章 `code/transformer.py`：纯 PyTorch 实现 Multi-Head Attention 和完整 Encoder-Decoder 结构。对应概念：[Transformer 架构](../concepts/transformer-architecture.md)。
* [LLaMA2 模型构建与预训练](llama2-pretrain-sft.md) — 第五章 `code/`：ModelConfig、RMSNorm、RoPE、GQA、Tokenizer 训练、DDP 预训练与 SFT 全流程。对应概念：[LLaMA2 手写实现](../concepts/llama2-implementation.md)、[模型训练](../concepts/model-training.md)。
* [TinyRAG 检索增强生成](rag-tinyrag.md) — 第七章 `RAG/`：Embeddings、VectorBase、LLM 调用的完整 RAG 链路。对应概念：[RAG 检索增强生成](../concepts/rag-retrieval-augmented-generation.md)。
* [TinyAgent 智能体工具调用](agent-tinyagent.md) — 第七章 `Agent/`：核心推理循环、工具注册、ReAct 范式、Streamlit Web Demo。对应概念：[Agent 智能体](../concepts/agent-intelligent-agent.md)。
