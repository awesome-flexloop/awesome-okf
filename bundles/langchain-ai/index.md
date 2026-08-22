---
type: bundle
okf_version: "0.2"
scope: langchain-ai
name: langchain-ai
version: "0.1.0"
source: https://github.com/langchain-ai
description: LangChain-AI 开源 LLM 应用开发框架生态源码中文教程——LangChain/LangGraph 核心框架（Python 与 JS）、关键集成组件、开发工具、Agent 框架与基础设施仓库
---

# LangChain-AI 生态系统（LangChain-AI Ecosystem）

本分组提供 LangChain-AI 组织开源的 LLM 应用开发框架生态的源码级中文学习文档。LangChain-AI 是当前 LLM 应用与 AI Agent 开发的事实标准之一，本分组覆盖其核心框架（LangChain、LangGraph 的 Python 与 JavaScript/TypeScript 双语言版本）、关键集成组件（Google、MongoDB、LangSmith 等）、深度研究 Agent 框架（deepagents）、以及配套的评测、运维与基础设施仓库。

## 生态关系概览

```
┌──────────────────────────────────────────────────────────────┐
│               🦜🔗 LangChain-AI 框架生态                      │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │                   编排层（Orchestration）               │  │
│  │   langgraph(Python) · langgraphjs(JS)                  │  │
│  │   有向状态图 · State/Schema · checkpoint · 长期记忆      │  │
│  └───────────────────────┬────────────────────────────────┘  │
│                          │ 构建于                            │
│  ┌───────────────────────▼────────────────────────────────┐  │
│  │                   核心框架层（Core Framework）           │  │
│  │   langchain(Python) · langchainjs(JS/TS)               │  │
│  │   Runnable组合协议 · Message/Tool · Prompt · 检索        │  │
│  └───────────────┬────────────────────────────────────────┘  │
│                  │ 集成与观测                                │
│  ┌───────────────▼────────────────────────────────────────┐  │
│  │              集成与可观测性层                            │  │
│  │  langchain-google · langchain-mongodb                  │  │
│  │  langsmith-sdk · langsmith-cli (LangSmith可观测)        │  │
│  └───────────────┬────────────────────────────────────────┘  │
│                  │ 上层应用                                  │
│  ┌───────────────▼────────────────────────────────────────┐  │
│  │                  Agent 框架与应用层                      │  │
│  │  deepagents(+lca) · deepagentsjs · open-swe            │  │
│  │  openevals(评测) · openwiki · openwork                  │  │
│  │  chat-langchain · social-media-agent                    │  │
│  └───────────────┬────────────────────────────────────────┘  │
│                  │ 部署运维                                  │
│  ┌───────────────▼────────────────────────────────────────┐  │
│  │              基础设施层（Infrastructure）                │  │
│  │  docs(文档站) · helm(Helm Chart) · terraform(配置)      │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

## 知识束导航

### 核心框架（深度 bundle）

| 知识束 | 简介 |
|--------|------|
| [langchain](langchain/index.md) | LangChain 核心框架（Python）——Runnable 组合协议、Message/Tool 抽象、Prompt 分层、输出解析、回调、检索（langchain-core） |
| [langgraph](langgraph/index.md) | LangGraph Agent 编排框架（Python）——StateGraph/节点/边、State 与 Schema、checkpoint 持久化、Stream、CLI |
| [langchainjs](langchainjs/index.md) | LangChain 核心框架（JavaScript/TypeScript）——JS 版 Runnable/Message/Tool、pnpm+turbo 工作区布局 |
| [langgraphjs](langgraphjs/index.md) | LangGraph 编排框架（JavaScript/TypeScript）——JS 版 StateGraph/checkpoint/通道，与 langchainjs 集成 |

### 关键集成与可观测性

| 知识束 | 简介 |
|--------|------|
| [langchain-google](langchain-google/index.md) | Google GenAI/VertexAI 集成——ChatModel、Embeddings、provider 抽象与鉴权 |
| [langchain-mongodb](langchain-mongodb/index.md) | MongoDB 集成——向量存储、Atlas Vector Search、集合索引与文档写入 |
| [langsmith-sdk](langsmith-sdk/index.md) | LangSmith 可观测性 SDK（js/ + python/）——Trace/Run/Feedback 上报、评测接口 |
| [langsmith-cli](langsmith-cli/index.md) | LangSmith 命令行工具（Go）——CLI 命令结构、与 LangSmith API 对接 |

### Agent 框架与应用

| 知识束 | 简介 |
|--------|------|
| [deepagents](deepagents/index.md) | 深度研究 Agent 框架（Python，含 lca-deepagents 变体）——planning/sub-agent/todo/context 管理 |
| [deepagentsjs](deepagentsjs/index.md) | 深度研究 Agent 框架（TypeScript）——JS 版实现与 deepagents 对应关系 |
| [open-swe](open-swe/index.md) | 开源 SWE（软件工程）Agent——agent/dispatch/reviewer/reconcile/scheduler、基于 langgraph 编排 |
| [openevals](openevals/index.md) | LLM 评测库（js/ + python/）——exact/llm-as-judge 评测器与评判协议 |
| [openwiki](openwiki/index.md) | Wiki/文档 Agent（TypeScript）——agent/cli/config、认证与 token 管理 |
| [openwork](openwork/index.md) | 工作流 CLI 工具（TypeScript）——命令行结构与类型定义 |
| [chat-langchain](chat-langchain/index.md) | 基于 LangChain 的对话 Demo 应用——agent.py、identity.py |
| [social-media-agent](social-media-agent/index.md) | 社交媒体 Agent（Python）——内容生成与发布流程 |

### 基础设施与文档（参考 bundle）

| 知识束 | 简介 |
|--------|------|
| [docs](docs/index.md) | LangChain 官方文档站——src/*.mdx 文档结构索引 |
| [helm](helm/index.md) | Helm Chart 部署配置——Kubernetes 部署结构 |
| [terraform](terraform/index.md) | Terraform 基础设施配置——云资源编排 |

## 推荐学习路径

### 路径1：Python 开发者入门 LangChain 生态

```
langchain (核心框架：Runnable/Message/Tool/Prompt)
    → langgraph (Agent 编排：StateGraph/checkpoint)
    → langsmith-sdk (可观测性：Trace/评测)
    → deepagents (深度研究 Agent 实战)
```

### 路径2：JavaScript/TypeScript 开发者

```
langchainjs (核心框架)
    → langgraphjs (Agent 编排)
    → deepagentsjs (深度研究 Agent)
    → open-swe (SWE Agent 框架)
```

### 路径3：集成与评估

```
langchain (核心框架)
    → langchain-google / langchain-mongodb (外部服务集成)
    → openevals (LLM 评测)
    → langsmith-cli (可观测运维)
```

## 版本信息

- **文档生成日期**：2026-08-23
- **源码来源**：https://github.com/langchain-ai
- **许可证**：各项目采用 MIT 或其他开源许可（详见各 bundle）