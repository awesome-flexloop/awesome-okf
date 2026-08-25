---
okf_version: "0.2"
title: "Second Me"
description: "个人AI数字分身 - 三层记忆HMM架构+LoRA个性化的本地个人智能体框架"
tags:
  - ai-agent
  - personal-ai
  - digital-twin
  - memory
  - lora
  - python
generated: true
status: active
stale_after: P3M
sources:
  - https://github.com/mindverse/Second-Me
related:
  - "[[ai-agent-fundamentals]]"
  - "[[veadk-python]]"
  - "[[book-to-skill]]"
  - "[[i-have-adhd]]"
---

# Second Me

Second Me 是构建个人AI数字分身的开源框架，核心创新是三层记忆HMM架构：L0原始记忆层→L1语义网络层→L2推理模型层，通过SFT+LoRA微调和DPO偏好对齐将个人记忆内化到模型权重，经GGUF量化后由llama.cpp本地推理。支持14步自动化训练流水线、Flask API服务、Space策略模式多Agent讨论。

## 🧩 概念导航（Concepts）

- [three-layer-memory-hmm](concepts/three-layer-memory-hmm.md) — 三层记忆HMM架构：L0→L1→L2递进抽象
- [l0-raw-memory](concepts/l0-raw-memory.md) — L0原始记忆层：文件摄入、Chunking、LLM洞察、ChromaDB存储
- [l1-semantic-network](concepts/l1-semantic-network.md) — L1语义网络层：Note/Chunk/Cluster/Shade/Bio人格侧面提取
- [l2-inference-model](concepts/l2-inference-model.md) — L2推理模型层：SFT+LoRA微调、DPO对齐、GGUF量化、llama.cpp推理
- [training-pipeline](concepts/training-pipeline.md) — 训练流水线：14步ProcessStep编排、断点续训、SSE实时日志
- [flask-api-server](concepts/flask-api-server.md) — Flask API服务架构：REST端点、模型服务、前后端通信
- [space-strategy](concepts/space-strategy.md) — Space策略模式与多智能体讨论：策略模式配置角色、AI多方对话

## 🎯 示例导航（Examples）

- [train-personal-ai](examples/train-personal-ai.md) — 训练个人AI：三层记忆完整训练流程
- [deploy-second-me](examples/deploy-second-me.md) — 部署Second Me：Docker Compose部署、API调用
- [use-space-strategy](examples/use-space-strategy.md) — 使用Space策略：多Agent讨论与协作

## 📚 参考导航（References）

- [second-me-sources](references/second-me-sources.md) — Second Me源码路径、技术栈、核心目录、API路由索引

## 🔗 关联 Bundle

- [ai-agent-fundamentals](../ai-agent-fundamentals/index.md) — AI Agent基础概念与记忆架构模式
- [veadk-python](../veadk-python/index.md) — VEADK Python模型接入参考
- [book-to-skill](../book-to-skill/index.md) — 书籍转技能可扩展训练数据
- [i-have-adhd](../i-have-adhd/index.md) — ADHD认知助手个人Agent设计

---

> **信任声明**：本文档基于 Second Me 源码逐模块分析，经 OKF 五阶段流程生成。
> 
> **生成时间**：2026-08-23 | **下次审查**：2026-11-23 | **维护者**：OKF Wiki Bot

```{toctree}
:hidden:

concepts/flask-api-server
concepts/l0-raw-memory
concepts/l1-semantic-network
concepts/l2-inference-model
concepts/space-strategy
concepts/three-layer-memory-hmm
concepts/training-pipeline
examples/deploy-second-me
examples/train-personal-ai
examples/use-space-strategy
references/second-me-sources
```
