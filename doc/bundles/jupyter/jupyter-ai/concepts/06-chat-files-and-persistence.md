---
type: Concept
title: 聊天文件与持久化
description: Jupyter AI 的 .chat 文件格式、YDoc 实时协作、聊天持久化机制和 RTC 后端
tags: [chat-file, persistence, ydoc, rtc, crdt, collaboration, yjs]
sources:
  - id: user-guide
    resource: external/libs/jupyter/jupyter-ai/docs/source/users/index.md
    title: users/index.md
  - id: jupyter-chat-deps
    resource: external/libs/jupyter/jupyter-ai/pyproject.toml
    title: pyproject.toml (jupyterlab_chat dependency)
  - id: contributors
    resource: external/libs/jupyter/jupyter-ai/docs/source/contributors/index.md
    title: contributors/index.md
status: stable
generated:
  by: reference_agent/source-code-to-okf-wiki
  at: 2026-08-22
---

# 聊天文件与持久化

Jupyter AI 采用了一种 Jupyter 原生的持久化方式：**聊天即文件**。聊天会话以 `.chat` 文件的形式存储在工作区中，结合 Yjs CRDT 实现实时协作。

## 聊天即文件（Chats are Files）

在 Jupyter AI 中，每个聊天都是一个存储在工作区中的 `.chat` 文件：

- **文件格式**：`<chat_name>.chat`
- **存储位置**：工作区目录中（与 Notebook 同级）
- **内容**：包含完整的聊天历史
- **持久化**：自动保存到磁盘，关闭 JupyterLab 后不丢失
- **恢复**：重新打开 `.chat` 文件即可恢复之前的聊天
- **删除**：直接删除对应的 `.chat` 文件
- **版本控制**：`.chat` 文件可纳入 Git 版本控制

这意味着你可以像管理 Notebook 一样管理聊天——创建、重命名、移动、删除、分享。

### 多聊天并发

可以同时创建和使用多个聊天来管理不同的对话线程。每个聊天是独立的 `.chat` 文件，拥有独立的上下文。

## 实时协作（RTC）

Jupyter AI 的聊天基于 `jupyterlab_chat` 和 `jupyter_server_documents` 提供的 RTC（Real-Time Collaboration）后端。

### Yjs CRDT

聊天文档使用 Yjs CRDT（Conflict-free Replicated Data Type）实现多用户实时协作：

- **自动并发处理**：多用户同时编辑/发送消息时自动合并冲突
- **实时同步**：其他用户的消息和输入状态实时显示
- **Awareness 协议**：跟踪用户在线状态、当前活动单元格、输入状态等
- **离线恢复**：网络重连后自动同步状态

### RTC 后端

`jupyter_server_documents` 包提供了改进的服务端文档处理：
- 基于 YDoc 的共享文档模型
- 改进的输出处理
- 内核管理和状态追踪

## Jupyternaut 对话记忆

Jupyternaut Persona 的对话记忆管理：

### 默认行为（内存记忆）

- 对话历史仅保存在服务进程内存中
- 服务重启后对话记忆丢失
- 默认保留最近 2 轮对话（4条消息：2问2答）作为上下文
- 通过 `--AiExtension.default_max_chat_history` 参数调整

### 持久化记忆（可选）

安装 persistence extra 后启用 SQLite 持久化：

```bash
pip install 'jupyter-ai-jupyternaut[persistence]'
```

- 使用 `langgraph-checkpoint-sqlite` 将对话记忆保存到本地 SQLite 数据库
- 服务重启后对话历史可恢复
- 注意：持久化的是 AI 模型的对话记忆（上下文窗口），不是 `.chat` 文件本身

## .chat 文件的注意事项

### 不保证前向兼容

`.chat` 文件格式可能随版本变化，**不保证前向兼容性**。跨版本升级后，旧版本创建的 `.chat` 文件可能无法在新版本中正常工作。

**建议**：升级前如需保留重要对话上下文，可以让 Agent 读取旧 `.chat` 文件并生成摘要，在新聊天中使用摘要作为上下文。

### Magic Commands 上下文

Magic Commands（%ai/%%ai）的对话上下文独立于聊天面板：
- 使用 `In[]`/`Out[]`/`Err[]` 特殊变量引用 Notebook 单元格
- 使用 `%ai reset` 清除 Magic 命令的对话历史
- 上下文窗口大小通过 `%config AiMagics.max_history` 配置

## 文档协作相关包

聊天和文档持久化依赖以下子包：

| 子包 | 职责 |
|---|---|
| `jupyterlab_chat` | 核心聊天 UI（React 组件 + Python 后端）、Yjs CRDT 同步、消息模型 |
| `jupyter_server_documents` | 服务端 YDoc 文档管理、输出处理、内核状态 |
| `jupyterlab_notebook_awareness` | 追踪当前 Notebook 和活动单元格，同步到 Awareness |

## 相关概念

- [聊天界面](02-chat-interface.md)
- [元包架构](03-metapackage-architecture.md)
- [ACP 与 MCP 双协议](04-protocols-acp-mcp.md)
- [AI Persona 系统](05-ai-personas.md)
- [配置系统](11-configuration-system.md)
