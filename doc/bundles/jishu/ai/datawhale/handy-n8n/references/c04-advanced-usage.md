---
type: reference
title: "C04 n8n 高阶用法"
bundle: /datawhale/handy-n8n
description: "子工作流与错误处理、集群节点（Chain/Agent）、Memory 记忆、RAG 向量检索、Tools 工具、MCP 协议"
source: https://github.com/datawhalechina/handy-n8n/blob/main/c04/README.md
path: c04/
tags: [sub-workflow, error-handling, ai, agent, rag, mcp, memory, tools]
status: stable
---

# C04 n8n 高阶用法

## 信源信息

- **文件路径**：`c04/README.md`（含 2 个子文档）
- **GitHub**：https://github.com/datawhalechina/handy-n8n/blob/main/c04/
- **sidebar 标题**：C04 - n8n 高阶用法

## 内容概要

在基础用法之上，本章介绍子工作流、错误处理以及 AI 相关的高阶功能：集群节点、MCP、Human in the Loop 等。

## 子文档

### n8n 子工作流与错误处理（`n8n-sub-workflows-and-error-handling.md`）

**子工作流**：
- Execute Workflow 节点调用子工作流
- Execute Sub-Workflow Trigger（"When Executed by Another Workflow"）接收调用
- 支持参数定义和传递
- 以计算器（加减乘除）为例，通过 Switch 节点路由运算
- 主/子工作流执行日志独立可查

**错误处理**：
- Error Trigger 节点触发独立的错误处理工作流
- 工作流 Settings → Error Workflow 绑定错误处理工作流
- Error Trigger 输出错误上下文（工作流名称、执行 URL 等），可通过表达式引用
- 以 SMTP 邮件通知为例（网易邮箱 smtp.163.com:465，授权码），也可使用飞书/企微

### n8n AI 相关概念（`n8n-ai-concepts.md`）

**集群节点（Cluster Nodes）**：
- 根节点（root）+ 子节点（sub-nodes）组成
- Chain 类型：Basic LLM Chain、Retrieval Q&A Chain、Summarization Chain、Sentiment Analysis、Text Classifier
- Agent 类型：可访问工具、根据上下文自主决策执行，是"知道如何决策的 Chain"

**Memory 记忆**：
- Simple Memory、MongoDB/Redis/Postgres Chat Memory
- 两次交互：loadMemoryVariables（加载）+ saveContext（保存）
- Simple Memory 在队列模式下不可靠，生产环境使用外部记忆体

**RAG**：
- Vector Store + Embedding Model + Document Loader
- 两阶段：内容上传（Form Trigger → Data Loader → Embedding → Vector Store Insert）和内容检索（Chat Trigger → Agent + Vector Store as Tool）
- 以"chat 嬛嬛.txt"为示例文档

**Tools 工具**：
- Agent 可关联多个工具（Date & Time Tool、Calculator 等）
- HTTP Request 节点也可作为 Agent 工具

**MCP（Model Context Protocol）**：
- 标准化 LLM 上下文提供的开放协议，类比"AI 应用的 USB-C"
- 通讯机制：stdio 和 Streamable HTTP（n8n 主要使用后者）
- n8n 双向支持：MCP Client Tool（作为 Agent 工具连接外部 Server）+ MCP Server Trigger（将 n8n 节点如 GitHub 暴露为 MCP 服务）
- 以 GitHub API 为完整示例：申请 token → MCP Server Trigger 配置 GitHub 工具 → Chat Trigger + Agent + MCP Client → 对话获取仓库信息

## 配套工作流

`workflows/c04/` 目录下 6 个 JSON 文件：n8n_sub_workflow.json、n8n_chat_with_memory.json、n8n_rag.json、n8n_tools.json、n8n_mcp.json、n8n_root_nodes.json。另含示例数据 `data/chat嬛嬛.txt`。

## 对应概念

- [AI 与 API 集成](../concepts/ai-api-integration.md)——集群节点、Memory、RAG、Tools、MCP
- [高级实战](../concepts/advanced-practice.md)——子工作流与错误处理
- [RAG 知识库对话示例](../examples/rag-knowledge-chat.md)——RAG 完整实践
