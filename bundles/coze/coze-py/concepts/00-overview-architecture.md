---
type: concept
title: "整体架构概览"
description: "理解 cozepy SDK 的同步/异步双轨设计、懒加载服务组合模式、模块组织和 HTTP/WebSocket 双通道架构。"
tags: [architecture, sync, async, lazy-loading, module, overview]
generated: { by: "process:source-code-to-okf-wiki", at: "2026-08-23T02:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T02:00:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: F-cp-001
    resource: /references/coze-client.md
    title: "Coze 客户端入口与基础设施参考"
  - id: F-cp-005
    resource: /references/data-pagination.md
    title: "数据模型、分页与资源管理参考"
---

# 整体架构概览

cozepy 是 Coze 开放平台的官方 Python SDK（v0.20.0），提供了从对话、Bot 管理、工作流到实时音频的完整 API 封装。SDK 的架构设计围绕"双轨并行、懒加载组合、统一抽象"三个核心原则展开，使得同步和异步两种编程模型拥有几乎完全一致的接口，开发者只需掌握一套 API 即可在两种模式间切换。

## 同步/异步双轨设计

SDK 最显著的架构特征是**同步/异步双轨并行**：每个功能模块都同时提供 `XxxClient`（同步）和 `AsyncXxxClient`（异步）两套实现。它们共享相同的方法签名和数据模型，仅 I/O 操作方式不同。

```
Coze (同步入口)                    AsyncCoze (异步入口)
├── .bots   → BotsClient          ├── .bots   → AsyncBotsClient
├── .chat   → ChatClient          ├── .chat   → AsyncChatClient
├── .audio  → AudioClient         ├── .audio  → AsyncAudioClient
├── .websockets → WebsocketsClient ├── .websockets → AsyncWebsocketsClient
└── ...                            └── ...
```

选择同步还是异步入口很简单：脚本、Jupyter Notebook 等场景使用 `Coze`；FastAPI、aiohttp 等异步 Web 框架使用 `AsyncCoze`。数据模型（如 `Chat`、`Message`、`Bot`）在两种模式下完全复用，无需额外转换。

## 懒加载服务组合

`Coze` 和 `AsyncCoze` 类本身并不直接实现业务逻辑，而是作为**服务组合容器**，通过 20 个懒加载属性暴露各业务客户端。所谓"懒加载"是指服务客户端只在首次访问属性时才实例化，避免了启动时一次性加载所有模块的开销：

```python
from cozepy import Coze, TokenAuth

coze = Coze(auth=TokenAuth(token="your_token"))
# 此时没有创建任何服务客户端

bots = coze.bots  # 首次访问 .bots 时，BotsClient 才被创建
chat = coze.chat  # 首次访问 .chat 时，ChatClient 才被创建
```

20 个服务属性覆盖了 Coze 平台的所有能力域：

| 能力域 | 入口属性 | 功能 |
|--------|----------|------|
| 对话 | `.chat` | 与 Bot 对话（SSE 流式/轮询） |
| Bot 管理 | `.bots` | Bot 的 CRUD、发布、版本管理 |
| 工作流 | `.workflows` | 工作流执行、聊天、异步运行 |
| 会话 | `.conversations` | 会话生命周期、消息、反馈 |
| 实时通信 | `.websockets` | WebSocket 实时对话和音频 |
| 音频 | `.audio` | TTS、ASR、房间、直播、声纹 |
| 知识库 | `.datasets` | 数据集、文档、图片管理 |
| 文件 | `.files` | 文件上传 |
| 其他 | `.workspaces`, `.templates`, `.users`, `.variables`, `.folders`, `.connectors` 等 | 工作空间、模板、用户、变量等 |

> ⚠️ `.knowledge` 属性已废弃（发出 `DeprecationWarning`），请使用 `.datasets` 替代。

## 模块组织

源码采用**按业务域组织**的包结构，每个业务域是一个独立子包：

```
cozepy/
├── coze.py          # Coze / AsyncCoze 入口类
├── auth/            # 认证体系（Token/JWT/OAuth）
├── chat/            # 对话模块（含 message/ 子模块）
├── bots/            # Bot 管理（含 collaborators/、versions/）
├── workflows/       # 工作流（含 chat/、runs/、versions/）
├── conversations/   # 会话（含 message/、feedback/）
├── websockets/      # WebSocket 实时通信
│   ├── ws.py        # WS 基础设施（基类、事件工厂）
│   ├── chat/        # 实时对话 WS
│   └── audio/       # 实时音频 WS（speech/、transcriptions/）
├── audio/           # 音频 HTTP API
│   ├── speech/      # TTS
│   ├── transcriptions/  # ASR
│   ├── voices/      # 声音管理
│   ├── rooms/       # 实时音视频房间
│   ├── live/        # 直播
│   └── voiceprint_groups/  # 声纹组
├── datasets/        # 数据集/知识库（含 documents/、images/）
├── files/           # 文件管理
├── workspaces/      # 工作空间
├── knowledge/       # ⚠️ 已废弃
├── config.py        # 配置常量
├── exception.py     # 异常体系
├── log.py           # 日志工具
├── model.py         # CozeModel 基类、分页器
├── request.py       # HTTP 层、Requester
├── util.py          # 工具函数
└── version.py       # 版本号
```

## HTTP 与 WebSocket 双通道

SDK 提供两种通信通道：

1. **HTTP 通道**（基于 httpx）：用于常规 CRUD 操作、SSE 流式对话、文件上传下载。`SyncHTTPClient`/`AsyncHTTPClient` 封装 httpx，`Requester` 统一处理认证注入和请求发送。SSE 流式响应由 `Stream[T]`/`AsyncStream[T]` 包装，提供迭代器接口。

2. **WebSocket 通道**：用于实时对话和实时音频场景。基于 Builder 模式创建连接，使用事件驱动模型（EventHandler）处理服务端推送事件。所有 WS 客户端共享 `WebsocketsBaseClient` 基类和 `WebsocketsEventFactory` 事件工厂。

```
┌─────────────────────────────────────────────┐
│              Coze / AsyncCoze               │
│         (20 个懒加载服务属性组合)              │
├──────────────────┬──────────────────────────┤
│   HTTP 通道       │    WebSocket 通道         │
│  (httpx 封装)     │    (ws 连接 + 事件循环)    │
│                  │                          │
│ • REST API       │ • 实时对话 (v1/chat)       │
│ • SSE 流式对话    │ • 实时 TTS (v1/audio/speech)│
│ • 文件上传/下载   │ • 实时 ASR (v1/audio/      │
│ • 分页迭代        │   transcriptions)          │
└──────────────────┴──────────────────────────┘
```

## 统一数据模型

所有数据模型继承自 `CozeModel`（基于 Pydantic v2），提供类型安全的数据验证和序列化。枚举类型统一继承 `DynamicStrEnum`（同时是 `str` 和 `Enum`），使得枚举值可以直接与字符串比较，也可以作为枚举成员使用。

分页结果统一抽象为三种分页器：`NumberPaged`（页码分页）、`TokenPaged`（游标分页）、`LastIDPaged`（Last-ID 分页），它们共享一致的迭代协议——既可以 `for item in page` 遍历所有项目（自动翻页），也可以 `for page in page.iter_pages()` 逐页处理。

## 类型安全与兼容性

SDK 包含 `py.typed` 文件（PEP 561），完全支持 mypy、pyright 等静态类型检查器。所有公开接口都有完整的类型注解。所有服务客户端方法都接受 `**kwargs`，其中 `headers` 参数可用于传递自定义请求头，方便在需要时添加额外的 HTTP 头部。

## 相关概念

- [认证体系](/concepts/01-auth-system.md) — 理解 Token/JWT/OAuth 四种认证方式的选择和使用
- [客户端初始化](/concepts/02-client-init.md) — 配置 base_url、超时、自定义 http_client、日志
- [对话与流式](/concepts/03-chat-streaming.md) — SSE 流式对话的核心机制
- [WebSocket 实时通信](/concepts/07-websockets-realtime.md) — 实时对话与音频的 WebSocket 通道
- [Coze 客户端入口与基础设施参考](/references/coze-client.md) — 配置常量、异常体系、HTTP 层 API
