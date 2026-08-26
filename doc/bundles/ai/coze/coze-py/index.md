---
okf_version: "0.2"
type: index
title: "cozepy (Coze Python SDK) Wiki"
description: "cozepy v0.20.0 的中文 Wiki——Coze 开放平台官方 Python SDK，涵盖对话、Bot 管理、工作流、WebSocket 实时通信、音频、认证、分页等完整 API 文档和示例。"
tags: [coze, python, sdk, chat, bot, workflow, websocket, audio, oauth]
generated: { by: "process:source-code-to-okf-wiki", at: "2026-08-23T02:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T02:00:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: F-cp-001
    resource: /references/coze-client.md
    title: "Coze 客户端入口与基础设施参考"
  - id: F-cp-002
    resource: /references/auth-model.md
    title: "认证体系参考"
  - id: F-cp-003
    resource: /references/chat-workflow.md
    title: "对话与工作流参考"
  - id: F-cp-004
    resource: /references/websockets-audio.md
    title: "WebSocket 实时通信与音频参考"
  - id: F-cp-005
    resource: /references/data-pagination.md
    title: "数据模型、分页与资源管理参考"
---

# cozepy (Coze Python SDK) Wiki

**cozepy** 是 [Coze（扣子）](https://www.coze.cn) 开放平台的官方 Python SDK（当前版本 **v0.20.0**），提供同步（`Coze`）和异步（`AsyncCoze`）双轨 API，覆盖对话（Chat）、Bot 管理、工作流（Workflow）、WebSocket 实时通信、音频处理（TTS/ASR/房间/直播/声纹）、知识库（Datasets）、文件管理、OAuth 认证等完整功能。

## 快速开始

```python
from cozepy import Coze, TokenAuth, Message, ChatEventType, COZE_CN_BASE_URL

coze = Coze(auth=TokenAuth(token="your_pat_token"), base_url=COZE_CN_BASE_URL)

for event in coze.chat.stream(
    bot_id="your_bot_id",
    user_id="user_001",
    additional_messages=[Message.build_user_question_text("你好")],
):
    if event.event == ChatEventType.CONVERSATION_MESSAGE_DELTA:
        print(event.message.content, end="", flush=True)
```

安装：`pip install cozepy`

## 文档导航

### 📚 概念文档（按学习路径排列）

| 序号 | 主题 | 说明 |
|------|------|------|
| 00 | [整体架构概览](/concepts/00-overview-architecture.md) | 同步/异步双轨、懒加载服务组合、模块组织 |
| 01 | [认证体系](/concepts/01-auth-system.md) | PAT Token、JWT、Web OAuth、PKCE、设备码 |
| 02 | [客户端初始化与配置](/concepts/02-client-init.md) | base_url、超时、自定义 http_client、日志 |
| 03 | [对话与流式处理](/concepts/03-chat-streaming.md) | SSE 流式对话、ChatEvent、Message、工具调用 |
| 04 | [Bot 管理](/concepts/04-bot-management.md) | Bot CRUD、发布、版本、配置模型 |
| 05 | [工作流](/concepts/05-workflows.md) | 工作流执行、流式对话、异步运行、中断恢复 |
| 06 | [会话管理](/concepts/06-conversations.md) | 会话生命周期、消息、反馈 |
| 07 | [WebSocket 实时通信](/concepts/07-websockets-realtime.md) | Builder 模式、EventHandler、实时对话/语音 |
| 08 | [音频与语音](/concepts/08-audio-voice.md) | TTS、ASR、声音、房间、直播、声纹 |
| 09 | [分页模式与资源管理](/concepts/09-pagination-resources.md) | 三种分页器、文件、数据集、工作空间等 |

### 💡 示例文档

| 示例 | 说明 |
|------|------|
| [基础对话](/examples/basic-chat.md) | TokenAuth → SSE 流式对话 → 事件处理 → 多轮对话 |
| [工作流执行](/examples/workflow-execution.md) | 工作流聊天 → runs 流式 → 中断恢复 |
| [WebSocket 语音对话](/examples/websocket-voice-chat.md) | EventHandler → Builder 模式 → 实时 TTS/ASR |
| [OAuth PKCE 与设备码认证](/examples/oauth-pkce-auth.md) | PKCE 流程 → 设备码流程 → Token 管理 |

### 📖 API 参考

| 参考文档 | 覆盖范围 |
|----------|---------|
| [客户端入口与基础设施](/references/coze-client.md) | Coze/AsyncCoze、配置常量、HTTP 层、Stream、异常、日志 |
| [认证体系](/references/auth-model.md) | TokenAuth、JWTAuth、OAuthApp 家族、OAuthToken、DeviceAuthCode |
| [对话与工作流](/references/chat-workflow.md) | ChatClient、Message、ChatEvent、工具调用、WorkflowsClient、WorkflowEvent |
| [WebSocket 与音频](/references/websockets-audio.md) | WS 基类、EventHandler、Chat/Audio WS、Audio HTTP 客户端 |
| [数据模型、分页与资源](/references/data-pagination.md) | CozeModel、DynamicStrEnum、分页器、Bot/Conversation/File/Dataset/Workspace 等 |

## SDK 能力速查

| 能力域 | 同步入口 | 异步入口 | 传输方式 |
|--------|---------|---------|---------|
| 对话（Chat） | `coze.chat` | `async_coze.chat` | HTTP SSE |
| Bot 管理 | `coze.bots` | `async_coze.bots` | HTTP REST |
| 工作流 | `coze.workflows` | `async_coze.workflows` | HTTP SSE |
| 会话管理 | `coze.conversations` | `async_coze.conversations` | HTTP REST |
| WebSocket 对话 | `coze.websockets.chat` | `async_coze.websockets.chat` | WebSocket |
| 实时音频 | `coze.websockets.audio` | `async_coze.websockets.audio` | WebSocket |
| TTS/ASR（HTTP） | `coze.audio.speech/transcriptions` | 异步版本 | HTTP (multipart) |
| 文件管理 | `coze.files` | `async_coze.files` | HTTP |
| 数据集/知识库 | `coze.datasets` | `async_coze.datasets` | HTTP |
| 工作空间 | `coze.workspaces` | `async_coze.workspaces` | HTTP |

## 链接索引

- [概念文档索引](/concepts/index.md)
- [示例文档索引](/examples/index.md)
- [API 参考索引](/references/index.md)

```{toctree}
:maxdepth: 7

concepts/index
examples/index
references/index
log
```
