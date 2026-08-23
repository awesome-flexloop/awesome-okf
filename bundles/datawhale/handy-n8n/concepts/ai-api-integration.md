---
type: concept
title: "AI 与 API 集成"
bundle: /datawhale/handy-n8n
description: "集群节点（Chain/Agent）、Memory 记忆、RAG 向量检索、Tools 工具调用、MCP 协议（Client/Server 双向）、HTTP Request 通用 API 连接"
sources: https://github.com/datawhalechina/handy-n8n/blob/main/c04/n8n-ai-concepts.md
related:
  - /datawhale/handy-n8n/concepts/workflow-design
  - /datawhale/handy-n8n/concepts/advanced-practice
  - /datawhale/handy-n8n/references/c04-advanced-usage
tags: [ai, agent, rag, mcp, memory, tools]
status: stable
---

# AI 与 API 集成

## 核心理解

n8n 的 AI 集成并非将 AI 作为独立产品，而是将 AI 能力**节点化**，使其与数据流、控制流、HTTP 请求等传统自动化节点协同工作。核心架构是**集群节点（Cluster Nodes）**——由根节点和子节点组成的节点组，实现从简单 LLM 调用到自主 Agent 的能力递进。n8n 同时通过 HTTP Request 节点提供通用 API 连接能力，通过 MCP 协议实现 AI 工具的标准化互操作。

## 集群节点（Cluster Nodes）

集群节点由**根节点（root node）**和一个或多个**子节点（sub-nodes）**组成，子节点扩展根节点的功能。AI 相关功能全部通过集群节点实现。

### Chain 根节点
Chain 是简单的 LLM 集成方式，串联工作流中的节点，**不支持记忆功能**。内置 Chain 节点：

- **Basic LLM Chain**：基础 LLM 调用链
- **Retrieval Q&A Chain**：检索问答链
- **Summarization Chain**：文本摘要链
- **Sentiment Analysis**：情感分析
- **Text Classifier**：文本分类

### Agent 根节点
Agent 是"知道如何做出决策的 Chain"，能够：
- 访问多个工具（Tools）
- 根据用户输入和上下文信息执行任务
- 通过工具返回的信息做执行决策
- 支持多轮对话和记忆

Chain → Agent 的递进对应了 AI 应用从"固定流程"到"自主决策"的复杂度跃迁。

## Memory 记忆

记忆允许 AI 模型记住之前的对话内容，在后续对话中使用上下文信息。

### 记忆体类型

| 类型 | 适用场景 | 注意事项 |
|------|---------|---------|
| Simple Memory | 测试、单实例部署 | 使用进程内存，队列模式不可靠 |
| MongoDB Chat Memory | 生产环境 | 外部持久化存储 |
| Redis Chat Memory | 生产环境、队列模式 | 高性能，推荐队列模式使用 |
| Postgres Chat Memory | 已有 PG 基础设施 | 复用数据库 |

### 工作机制
一次对话交互中，Agent 与 Memory 交互两次：
1. `loadMemoryVariables`：加载历史记忆
2. `saveContext`：保存当前对话上下文

> **重要**：Simple Memory 在 n8n Queue 部署模式下无法确保请求分发到同一 worker，生产环境必须使用外部记忆体。

## RAG 检索增强生成

RAG（Retrieval-Augmented Generation）结合检索和生成，从大量文本数据中检索相关信息，注入 LLM 生成准确回答。

### 核心组件
- **Vector Store（向量存储）**：存储 embedding 向量，支持相似度检索。n8n 提供 Simple Vector Store 等集群节点
- **Embedding Model**：将文档转化为向量（如 Gemini text-embedding-004）
- **Document Loader**：加载和解析文档（如 Default Data Loader）

### 两阶段架构

**阶段一：内容上传**
```
Form Trigger（文件上传）
  → Default Data Loader（解析文档）
  → Embedding Model（向量化）
  → Simple Vector Store（Insert Documents 存储）
```

**阶段二：内容检索**
```
Chat Trigger（用户提问）
  → AI Agent（关联 Vector Store 作为 Tool）
    → Embedding Model（问题向量化）
    → Vector Store（相似度检索）
  → LLM（基于检索结果生成回答）
```

Simple Vector Store 的 Retrieve Documents 操作配置为 "As Tool for AI Agent"，Agent 自主决定何时调用检索工具。

## Tools 工具

工具扩展 AI Agent 的能力边界，使 LLM 能够执行其本身不支持的操作：
- 搜索引擎搜索
- 数据库查询
- 天气信息查询
- 日期时间计算
- 计算器
- HTTP API 调用

一个 AI Agent 可关联多个工具，Agent 根据用户意图自主选择调用哪个工具。HTTP Request 节点也可附加到 Agent 作为工具，连接任意 REST API。

## MCP（Model Context Protocol）

MCP 是标准化应用程序如何为 LLM 提供上下文的开放协议，类比为"AI 应用的 USB-C 端口"。

### 通讯机制
- **stdio**：标准输入输出通信
- **Streamable HTTP**：流式 HTTP 请求响应（n8n 主要使用）

### n8n 的双向 MCP 角色

n8n 同时支持 MCP 的两端：

**MCP Client（作为 Agent 工具）**
- 在 AI Agent 的工具选项中添加 MCP Client
- 配置 SSE Endpoint 指向 MCP Server 地址
- Agent 通过 MCP Client 调用外部 MCP Server 的工具

**MCP Server Trigger（暴露 n8n 能力）**
- 添加 MCP Server Trigger 节点，生成 MCP 服务地址（`https://n8n.example.com/mcp/UUID`）
- 将 n8n 集成的节点（如 GitHub、HTTP Request）配置为 MCP 工具
- 外部 MCP Client 可调用这些工具
- 支持 "Let the model define this parameter" 让 AI Agent 自主填充参数

### MCP vs Tools
MCP 可视为"特殊的工具"——Tools 是 n8n 内部的工具注册机制，MCP 是跨进程/跨服务的标准化工具协议。MCP 使 n8n 既能消费外部 AI 能力，也能将自身的自动化能力暴露给 AI 生态。

## HTTP Request 节点

HTTP Request 节点是 n8n 最通用的 API 连接器：
- 支持所有 HTTP 方法、自定义请求头、请求体、认证
- 可作为独立节点调用任意 REST API
- 可附加到 AI Agent 作为工具，让 Agent 具备 API 调用能力
- 是连接无原生 n8n 节点支持的第三方服务的"万能接口"

## 在 handy-n8n 中的位置

C04 的"n8n AI 相关概念"子文档系统讲解了集群节点、Memory、RAG、Tools 和 MCP，配套 5 个工作流 JSON：
- `n8n_chat_with_memory.json`：带记忆的聊天
- `n8n_rag.json`：RAG 知识库
- `n8n_tools.json`：Agent 工具调用
- `n8n_mcp.json`：MCP GitHub 工具
- `n8n_root_nodes.json`：集群根节点展示

此外，`LangChain Code Node` 可编写自定义 LangChain 代码实现更复杂的 AI 应用。

## 延伸阅读

- [工作流设计](workflow-design.md)——触发器和核心节点基础
- [高级实战](advanced-practice.md)——子工作流、错误处理、自定义节点
- [RAG 知识库对话示例](../examples/rag-knowledge-chat.md)——RAG 完整实践
- [C04 n8n 高阶用法](../references/c04-advanced-usage.md)——完整信源
