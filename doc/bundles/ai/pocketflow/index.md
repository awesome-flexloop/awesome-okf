---
okf_version: "0.2"
type: group
title: "⚡ PocketFlow 极简LLM应用框架"
description: "PocketFlow——100行代码的极简LLM Agent框架。核心API、6大设计模式、3个实战教程的源码级中文教程"
total_bundles: 5
---

# ⚡ PocketFlow 极简LLM应用框架

PocketFlow 是一个仅约100行核心代码的极简 LLM Agent 框架，由 ThePocket 开源社区维护。它将 Agent 抽象为**节点（Node）+ 流程（Flow）**两个核心概念，通过运算符重载（`>>`/`-`）提供声明式 DSL，支持线性管道、条件分支、循环、嵌套、重试降级、批量处理和异步并行，零第三方依赖。本组包含核心 API 参考、6 大设计模式和 3 个官方教程应用的源码级中文教程。

## 推荐学习路径

```
📦 pocketflow-core      核心框架（12个类/API参考/6个核心概念）—— 必读起点
  ↓
🧩 pocketflow-patterns  6大设计模式（Agent/多Agent/RAG/MapReduce/HITL/Tool Use）
  ↓
┌────────────────────────────────────────────────────────────┐
│  选一个实战教程动手实践：                                    │
│  📚 codebase-knowledge  代码库知识生成器（6节点LLM流水线）   │
│  🎬 wan-video           万相AI视频生成器（自环迭代+批量）    │
│  💬 video-qa            极简问答应用（线性管道+LLM集成）     │
└────────────────────────────────────────────────────────────┘
```

---

## 知识束导航

### 📦 核心框架

| 知识束 | 文档数 | 一句话简介 |
|--------|--------|-----------|
| [pocketflow-core](pocketflow-core/index.md) | 6+6+1=13 | 核心API——12个类（BaseNode/Node/BatchNode/Flow/BatchFlow/AsyncNode族）、prep→exec→post三阶段生命周期、运算符DSL、重试降级、批量处理、异步并行 |

### 🧩 设计模式

| 知识束 | 文档数 | 一句话简介 |
|--------|--------|-----------|
| [pocketflow-patterns](pocketflow-patterns/index.md) | 6+1+1=8 | 6大设计模式——Agent循环（ReAct）、多智能体协作（Queue通信/Supervisor/Debate）、RAG（离线+在线双Flow）、MapReduce分治（BatchNode/嵌套BatchFlow）、Workflow/HITL（CLI/FastAPI/Gradio人机交互）、Tool Use（工具调用/MCP集成），覆盖40+ cookbook示例 |

### 🎬 实战教程

| 知识束 | 类型 | 文档数 | 一句话简介 |
|--------|------|--------|-----------|
| [tutorial-codebase-knowledge](tutorial-codebase-knowledge/index.md) | 代码分析 | 2+7+1=10 | 代码库知识自动生成器——6节点流水线（FetchRepo→IdentifyAbstractions→AnalyzeRelationships→OrderChapters→WriteChapters→CombineTutorial），LLM驱动的代码分析与教程生成，支持GitHub和本地代码库 |
| [tutorial-wan-video](tutorial-wan-video/index.md) | 视频生成 | 3+6+2=11 | 万相AI视频生成器——6节点流水线（GenerateScenes→GenerateScript→GenerateImage→GenerateAudio→AnimateVideo→Combine），自环迭代优化、批量图像/音频/视频生成、角色一致性策略 |
| [tutorial-video-qa](tutorial-video-qa/index.md) | 问答应用 | 2+4+1=7 | 极简AI问答导师——2节点线性管道（GetQuestionNode→AnswerNode），LLM集成模式、OpenAI API封装、多轮对话扩展 |

---

## 核心概念速查

| 概念 | 一句话定义 | 关键API |
|------|-----------|---------|
| 节点生命周期 | prep(读)→exec(算)→post(写) 三阶段 | Node.prep/exec/post |
| 流程编排 | while循环驱动有向图，post返回action决定流转 | Flow.run/_orch |
| 运算符DSL | `>>`默认边，`- "action" >>`条件边 | BaseNode.__rshift__/__sub__ |
| 重试降级 | exec失败自动重试max_retries次，耗尽后exec_fallback | Node(max_retries=N) |
| 批量处理 | BatchNode单节点批量，BatchFlow子流程级批量 | BatchNode/BatchFlow |
| 异步并行 | AsyncNode+asyncio.gather实现并发 | AsyncParallelBatchNode/Flow |

---

> **信任声明**：本分组索引基于 PocketFlow v0.0.x 核心源码（约200行）和 40+ cookbook 示例逐模块分析生成，所有 API 名称、类名、方法名均经 Grep 级源码验证。
> 
> **源码位置**：d:\spaces\SpecWeave\external\libs\ai\ThePocket\PocketFlow
> 
> **生成时间**：2026-08-23 | **维护者**：OKF Wiki Bot

```{toctree}
:hidden:

pocketflow-core/index
pocketflow-patterns/index
tutorial-codebase-knowledge/index
tutorial-wan-video/index
tutorial-video-qa/index
```
