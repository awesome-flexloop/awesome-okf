---
type: reference
title: "数据模型、分页与资源管理参考"
description: "CozeModel 基类、DynamicStrEnum、三种分页器、文件/数据集/工作空间/模板/连接器/文件夹等资源客户端的完整 API 参考。"
tags: [model, pydantic, pagination, dataset, file, workspace, bot, enum]
generated: { by: "process:source-code-to-okf-wiki", at: "2026-08-23T02:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T02:00:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: F-cp-005
    resource: /references/data-pagination.md
    title: "数据模型、分页与资源管理参考"
---

# 数据模型、分页与资源管理参考

本文档登记 SDK 数据模型基类、动态枚举、分页器体系，以及文件、数据集、工作空间、模板、连接器、文件夹等资源管理模块。

## 数据模型基类

### CozeModel

**所有数据模型的基类**，继承自 Pydantic BaseModel。cozepy 中所有数据模型（Chat、Message、Bot、Workflow、Conversation、File、Dataset 等）都继承自 `CozeModel`。

核心能力：
- 基于 Pydantic 的数据验证和序列化
- 支持 `model_dump()` / `model_validate()` 等标准 Pydantic v2 方法
- `dump_exclude_none()` 工具函数序列化时自动排除 None 值字段

### DynamicStrEnum

**动态字符串枚举基类**，同时继承 `str` 和 `Enum`。被 SDK 中 30+ 个枚举类使用，包括：

- `MessageRole`（USER / ASSISTANT）
- `ChatStatus`
- `ChatEventType`
- `WebsocketsEventType`
- `BotMode`
- `PublishStatus`
- `SuggestReplyMode`
- `UserInputType`
- `VariableType`
- `VariableChannel`
- `DatasetStatus`
- `DocumentStatus` / `FormatType` / `SourceType` / `UpdateType` / `ChunkStrategy`
- `PhotoStatus`
- `WorkspaceRoleType` / `WorkspaceType`
- `FeedbackType`
- `VoiceState` / `VoiceModelType`
- `RoomMode`
- `LiveType`
- `WorkflowMode`
- `CozePKCEAuthErrorType`

特性：字符串比较直接可用（`event.event_type == "conversation.chat.completed"`），同时支持枚举成员访问。

## 分页体系

SDK 提供三种分页模式，每种都有同步和异步版本：

```
PagedBase (同步分页基类)
├── NumberPaged      — 页码分页（page_number / page_size）
├── TokenPaged       — Token/Cursor 分页
└── LastIDPaged      — Last-ID 分页

AsyncPagedBase (异步分页基类)
├── AsyncNumberPaged
├── AsyncTokenPaged
└── AsyncLastIDPaged
```

### NumberPaged / AsyncNumberPaged

页码分页，通过 `page_num` 和 `page_size` 参数翻页。

**迭代方式**：

```python
# 遍历所有项目（自动翻页）
for item in paged_result:
    print(item)

# 逐页遍历
for page in paged_result.iter_pages():
    for item in page.items:
        print(item)
```

### TokenPaged / AsyncTokenPaged

Token/Cursor 分页，通过 next-page-token/cursor 翻页。适用于数据量较大、不适合用页码的场景。迭代接口与 NumberPaged 一致。

### LastIDPaged / AsyncLastIDPaged

Last-ID 分页，通过上一页最后一条记录的 ID 进行翻页。迭代接口同上。

### 分页迭代协议

所有分页器均支持两种迭代模式：

| 迭代方式 | 用法 | 说明 |
|----------|------|------|
| 项目迭代 | `for item in page:` | 自动翻页，遍历所有项目 |
| 页面迭代 | `for page in page.iter_pages():` | 逐页迭代，每页访问 `.items` 列表 |

---

## Bot 管理

### BotsClient / AsyncBotsClient

通过 `coze.bots` 访问。

#### Bot 模型

Bot 核心模型包含以下子模型：

| 子模型 | 说明 |
|--------|------|
| `BotModelInfo` | 模型配置信息（使用的模型 ID 等） |
| `BotPromptInfo` | Prompt 配置（人设与回复逻辑） |
| `BotKnowledge` | 知识库配置 |
| `BotPluginInfo` | 插件配置 |
| `BotPluginAPIInfo` | 插件 API 信息 |
| `BotOnboardingInfo` | 开场白/推荐问题配置 |
| `BotVoiceInfo` | 语音配置 |
| `BotWorkflowInfo` | 工作流配置 |
| `BotSuggestReplyInfo` | 推荐回复配置 |
| `BotVariable` | Bot 变量 |
| `BotBackgroundImageInfo` | 背景图片信息 |

#### Bot 相关枚举

| 枚举 | 说明 |
|------|------|
| `BotMode` | Bot 运行模式 |
| `PublishStatus` | 发布状态 |
| `SuggestReplyMode` | 推荐回复模式 |
| `UserInputType` | 用户输入类型 |
| `VariableType` | 变量类型 |
| `VariableChannel` | 变量渠道 |

#### 子客户端

| 属性 | 说明 |
|------|------|
| `.collaborators` | 协作者管理 |
| `.collaboration_modes` | 协作模式管理 |
| `.versions` | 版本管理 |

#### 核心方法

| 方法 | HTTP | 返回 | 说明 |
|------|------|------|------|
| `list()` | GET | `NumberPaged[Bot]` | 列出 Bot |
| `create()` | POST | `Bot` | 创建 Bot |
| `update()` | PUT | `Bot` | 更新 Bot |
| `retrieve()` | GET | `Bot` | 获取 Bot 详情 |
| `publish()` | POST | - | 发布 Bot |
| `unpublish()` | POST | - | 取消发布 Bot |

---

## Conversations（会话）

### ConversationsClient / AsyncConversationsClient

通过 `coze.conversations` 访问。

#### 数据模型

| 模型 | 说明 |
|------|------|
| `Conversation` | 会话模型 |
| `Section` | 分段/节模型 |
| `DeleteConversationResp` | 删除会话响应 |

#### 子客户端

| 属性 | 类型 | 说明 |
|------|------|------|
| `.message` | `MessagesClient` / `AsyncMessagesClient` | 消息管理 |
| `.message.feedback` | `ConversationsMessagesFeedbackClient` / `AsyncMessagesFeedbackClient` | 消息反馈 |

#### 核心方法

| 方法 | 说明 |
|------|------|
| `create()` | 创建会话 |
| `list()` | 列出会话（分页） |
| `retrieve()` | 获取会话详情 |
| `update()` | 更新会话 |
| `delete()` | 删除会话 |

#### FeedbackType（枚举）

消息反馈类型枚举（点赞/点踩等）。

---

## Files（文件管理）

### FilesClient / AsyncFilesClient

通过 `coze.files` 访问。

#### File 模型

文件元数据模型。

#### 内部工具

- `_try_fix_file()`：文件上传处理工具函数，处理文件路径/MIME 类型等兼容性问题。

---

## Datasets（数据集/知识库）

### DatasetsClient / AsyncDatasetsClient

通过 `coze.datasets` 访问（替代已废弃的 `.knowledge`）。

#### Dataset 模型

数据集（知识库）模型。

#### DatasetStatus（枚举）

数据集状态枚举。

#### DocumentProgress（文档处理进度）

#### 子客户端

| 属性 | 说明 |
|------|------|
| `.documents` | 文档管理 |
| `.images` | 图片管理 |

#### Documents 子模块

**Document 模型**及相关模型：

| 模型 | 说明 |
|------|------|
| `Document` | 文档模型 |
| `DocumentBase` | 文档基础信息 |
| `DocumentSourceInfo` | 文档来源信息 |

文档相关枚举：

| 枚举 | 说明 |
|------|------|
| `DocumentStatus` | 文档处理状态 |
| `FormatType` | 文档格式类型 |
| `SourceType` | 文档来源类型 |
| `UpdateType` | 更新类型 |
| `ChunkStrategy` | 分块策略 |

#### Images 子模块

**Photo 模型**：图片模型。

**PhotoStatus（枚举）**：图片状态枚举。

---

## Workspaces（工作空间）

### WorkspacesClient / AsyncWorkspacesClient

通过 `coze.workspaces` 访问。

#### Workspace 模型

工作空间模型。

#### 枚举

| 枚举 | 说明 |
|------|------|
| `WorkspaceRoleType` | 工作空间角色类型 |
| `WorkspaceType` | 工作空间类型 |

#### 子客户端

| 属性 | 说明 |
|------|------|
| `.members` | 工作空间成员管理 |

---

## 其他资源客户端

### TemplatesClient / AsyncTemplatesClient

模板管理客户端，通过 `coze.templates` 访问。

### UsersClient / AsyncUsersClient

用户信息客户端，通过 `coze.users` 访问。

### VariablesClient / AsyncVariablesClient

变量管理客户端，通过 `coze.variables` 访问。

### FoldersClient / AsyncFoldersClient

文件夹管理客户端，通过 `coze.folders` 访问。

### ConnectorsClient / AsyncConnectorsClient

连接器客户端，通过 `coze.connectors` 访问。包含 `.bots` 子客户端。

### KnowledgeClient / AsyncKnowledgeClient（已废弃）

通过 `coze.knowledge` 访问。**已废弃**，使用时会发出 `DeprecationWarning`，请改用 `.datasets`。

### Enterprises 相关客户端

通过 `coze.enterprises` 访问，包含 `.members` 和 `.organizations` 子客户端。

---

## 模块导出

- `__all__` 包含 300+ 导出符号，覆盖所有公开 API
- `py.typed` 文件存在，符合 PEP 561 类型标记规范，支持 mypy/pyright 等类型检查器
- 所有服务客户端方法均接受 `**kwargs`，支持自定义 `headers: Optional[dict]` 传递额外请求头
