---
type: reference
title: "第七章 大模型应用"
bundle: /datawhale/happy-llm
description: "LLM 评测体系、RAG 检索增强生成、Agent 智能体三大应用主题"
source: https://github.com/datawhalechina/happy-llm/blob/main/docs/chapter7/第七章%20大模型应用.md
path: docs/chapter7/第七章 大模型应用.md
code:
  - docs/chapter7/RAG/
  - docs/chapter7/Agent/
tags: [evaluation, rag, agent, mmlu, leaderboard]
status: stable
---

# 第七章 大模型应用

## 信源信息

- **文件路径**：`docs/chapter7/第七章 大模型应用.md`
- **RAG 代码**：`docs/chapter7/RAG/`
- **Agent 代码**：`docs/chapter7/Agent/`
- **GitHub**：https://github.com/datawhalechina/happy-llm/blob/main/docs/chapter7/第七章%20大模型应用.md

## 内容概要

本章涵盖 LLM 应用的三大主题：

### 7.1 LLM 的评测

- **评测数据集**：
  - 通用：MMLU（多任务语言理解）
  - 工具使用：BFCL V2
  - 数学：GSM8K（小学数学）、MATH（复杂数学）
  - 推理：ARC Challenge、GPQA、HellaSwag
  - 长文本：InfiniteBench、NIH/Multi-needle
  - 多语言：MGSM

- **主流评测榜单**：
  - Open LLM Leaderboard（HuggingFace）
  - Lmsys Chatbot Arena Leaderboard（真实用户对战）
  - OpenCompass（国内榜单，中文侧重）

- **垂直领域榜单**：金融（CFBenchmark）、安全（Flames）、通识（BotChat）、法律（LawBench）、医疗（MedBench）

### 7.2 RAG 检索增强生成

- RAG 原理：先检索外部文档再生成回答
- 解决问题：幻觉、知识过时、领域知识不足
- TinyRAG 实现：
  - `Embeddings.py`：文本向量化
  - `VectorBase.py`：向量存储与检索
  - `LLM.py`：大模型调用
  - `demo.py`：完整 RAG 流程演示

### 7.3 Agent 智能体

- Agent 工作原理：LLM 推理 + 工具调用循环
- ReAct 范式：Thought→Action→Observation 交替
- TinyAgent 实现：
  - `src/core.py`：Agent 核心推理循环
  - `src/tools.py`：工具定义与注册
  - `demo.py`：命令行演示
  - `web_demo.py`：Streamlit Web 界面

## 对应概念

- [RAG 检索增强生成](../concepts/rag-retrieval-augmented-generation.md)
- [Agent 智能体](../concepts/agent-intelligent-agent.md)
- [TinyRAG 示例](../examples/rag-tinyrag.md)
- [TinyAgent 示例](../examples/agent-tinyagent.md)
