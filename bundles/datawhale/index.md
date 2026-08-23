---
okf_version: "0.2"
type: group
title: "🐳 Datawhale 开源 AI 学习社区"
description: "Datawhale（datawhalechina）——国内最大的开源 AI 学习社区之一。涵盖 LLM 教程、RAG、Agent、向量数据库、推荐系统、机器学习理论等 18 个项目的源码级中文教程"
total_bundles: 18
generated:
  by: "okf-wiki-bot"
  at: "2026-08-23T00:00:00Z"
verified:
  by: "process:seven-concepts-v"
  at: "2026-08-23T00:00:00Z"
status: stable
---

# 🐳 Datawhale 开源 AI 学习社区

[Datawhale](https://github.com/datawhalechina) 是国内最大的开源 AI 学习社区之一，以"和鲸科技"为运营主体，汇聚了大量高校学生与工程师贡献者。本组将 `external/libs/ai/datawhalechina` 下收录的 18 个仓库系统化转译为 OKF v0.2 知识束，覆盖代码框架（推荐系统、多语言 Agent 平台）与教程书籍（LLM 全栈、RAG、Agent、向量数据库、机器学习理论等）两大类。

## 推荐学习路径

```
📚 理论基础
  ├── key-book        机器学习理论钥匙书（可学性/泛化界/稳定性）
  └── pumpkin-book    南瓜书（西瓜书公式推导伴读）
        ↓
🧠 大模型核心
  ├── base-llm        从 NLP 到 LLM 全栈教程
  ├── happy-llm       从零构建大模型（手写 LLaMA2）
  └── tiny-universe   大模型白盒子构建（手搓 Tiny 系列）
        ↓
🤖 Agent 与应用
  ├── hello-agents    从零构建智能体（16 章）
  ├── all-in-rag      RAG 技术全栈指南
  ├── easy-vecdb      向量数据库原理与实践
  └── deepagents      多语言 Agent 平台 monorepo
        ↓
🔧 工具与实战
  ├── torch-rechub    推荐系统框架（30+ 模型）
  ├── handy-ollama    本地大模型部署
  ├── handy-n8n       工作流自动化
  └── easy-vibe/vibe-vibe  Vibe Coding 教程
```

---

## 知识束导航

### 🏗️ 代码框架类（源码驱动）

| 知识束 | 语言 | 一句话简介 |
|--------|------|-----------|
| [torch-rechub](torch-rechub/index.md) | Python/PyTorch | 推荐系统框架——30+ 模型（DSSM/DeepFM/DIN/MMoE 等）、CTR/Match/MTL 三类 Trainer、ONNX 导出 |
| [deepagents](deepagents/index.md) | TS+Rust+Go | 多语言 Agent 平台 monorepo——libs/（acp/cli/code/evals/talon）+ openwiki |

### 📖 教程书籍类（文档驱动）

| 知识束 | 主题 | 一句话简介 |
|--------|------|-----------|
| [base-llm](base-llm/index.md) | LLM 全栈 | 从 NLP 到 LLM——分词/Word2Vec/RNN/Transformer/BERT/GPT/LoRA/RLHF/量化/部署 |
| [happy-llm](happy-llm/index.md) | 手写大模型 | 从零构建大模型——Transformer/PLM/LLaMA2 手写/GRPO/RAG/Agent |
| [hello-agents](hello-agents/index.md) | Agent 教程 | 从零构建智能体——16 章：ReAct/框架/记忆/上下文工程/通信协议/Agentic-RL |
| [all-in-rag](all-in-rag/index.md) | RAG 全栈 | RAG 技术全栈——数据准备/索引构建/检索进阶/生成评估/项目实战 |
| [easy-vecdb](easy-vecdb/index.md) | 向量数据库 | 向量数据库原理与实践——IVF/PQ/HNSW/LSH/Annoy/Faiss/Milvus |
| [key-book](key-book/index.md) | ML 理论 | 机器学习理论钥匙书——可学性/复杂度/泛化界/稳定性/一致性/收敛率/遗憾界 |
| [pumpkin-book](pumpkin-book/index.md) | 公式推导 | 南瓜书——西瓜书公式推导伴读 |
| [tiny-universe](tiny-universe/index.md) | 白盒构建 | 大模型白盒子构建指南——TinyDiffusion/TinyRAG/TinyAgent/TinyLLM 手搓 |
| [handy-ollama](handy-ollama/index.md) | 本地部署 | Ollama 本地大模型部署教程 |
| [handy-n8n](handy-n8n/index.md) | 工作流 | n8n 工作流自动化教程（c01-c06） |
| [easy-vibe](easy-vibe/index.md) | Vibe Coding | Vibe coding 多语言文档站 |
| [vibe-vibe](vibe-vibe/index.md) | Vibe 开发 | Vibe 开发教程（Basic/zh/en 多文档站） |
| [code-your-own-llm](code-your-own-llm/index.md) | 手写 LLM | 手写 LLM 精简便签（README+AGENTS.md） |
| [Agent-Learning-Hub](Agent-Learning-Hub/index.md) | Agent 路线 | Agent 学习路线（README+index.html） |
| [deepagents-in-action](deepagents-in-action/index.md) | deepagents 实战 | deepagents 实战教程（README） |
| [members-visualization](members-visualization/index.md) | 占位收录 | Datawhale 成员可视化（仅 .npmrc，占位收录） |

---

## 项目统计

| 分类 | 数量 | 项目 |
|------|------|------|
| 代码框架 | 2 | torch-rechub、deepagents |
| LLM/大模型教程 | 4 | base-llm、happy-llm、tiny-universe、code-your-own-llm |
| Agent 教程 | 3 | hello-agents、Agent-Learning-Hub、deepagents-in-action |
| RAG/向量库 | 2 | all-in-rag、easy-vecdb |
| ML 理论 | 2 | key-book、pumpkin-book |
| 工具/部署 | 3 | handy-ollama、handy-n8n、members-visualization |
| Vibe Coding | 2 | easy-vibe、vibe-vibe |

---

> **信任声明**：本分组索引基于 Datawhale 18 个 GitHub 公开仓库逐项目分析生成。代码框架类 bundle 的 API 名称经 Grep 级源码验证；教程类 bundle 的概念覆盖与原文章节结构一一对应。
>
> **源码位置**：`external/libs/ai/datawhalechina/`
>
> **生成时间**：2026-08-23 | **维护者**：OKF Wiki Bot
