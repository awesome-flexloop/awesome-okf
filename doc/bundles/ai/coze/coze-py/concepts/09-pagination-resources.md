---
type: concept
title: "分页模式与资源管理"
description: "掌握三种分页器（NumberPaged/TokenPaged/LastIDPaged）的使用方式，以及文件、数据集（知识库）、工作空间、模板、变量、文件夹、连接器等资源客户端的用法。"
tags: [pagination, paged, file, dataset, workspace, template, connector, folder, knowledge]
generated: { by: "process:source-code-to-okf-wiki", at: "2026-08-23T02:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T02:00:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: F-cp-005
    resource: /references/data-pagination.md
    title: "数据模型、分页与资源管理参考"
  - id: F-cp-001
    resource: /references/coze-client.md
    title: "Coze 客户端入口与基础设施参考"
---

# 分页模式与资源管理

cozepy 中的列表查询接口统一返回分页对象，而非直接返回列表。SDK 抽象了三种分页模式——页码分页、Token/游标分页和 Last-ID 分页，它们共享一致的迭代协议。本文档介绍分页器的使用方式，以及文件、数据集（知识库）、工作空间等辅助资源的管理。

## CozeModel 与 DynamicStrEnum

在讨论分页之前，先了解两个基础构建块。

### CozeModel

所有数据模型的基类，继承自 Pydantic v2 的 `BaseModel`。它提供：
- 类型安全的数据验证
- JSON 序列化/反序列化
- `model_dump()` 导出为字典
- `model_validate()` 从字典构建模型

所有 API 返回的数据对象（`Bot`、`Chat`、`Message`、`File`、`Dataset`、`Conversation`、`Workspace` 等）都是 `CozeModel` 的子类。

### DynamicStrEnum

一个同时继承 `str` 和 `Enum` 的枚举基类，SDK 中 30+ 个枚举都基于它。特性是：

```python
from cozepy import MessageRole

# 可以当作字符串使用
assert MessageRole.USER == "user"
assert MessageRole.ASSISTANT == "assistant"

# 也可以当作枚举使用
role = MessageRole("user")  # 从字符串解析

# 在 API 中直接传递字符串也能通过类型检查
```

这种设计使得枚举值既可以参与字符串比较和序列化，又保留了枚举的类型安全性。

## 三种分页器

SDK 提供三种分页模式，每种都有同步和异步版本：

| 分页器 | 异步版本 | 翻页依据 | 适用场景 |
|--------|---------|---------|---------|
| `NumberPaged[T]` | `AsyncNumberPaged[T]` | page_num + page_size | 数据量可预测，需要跳页 |
| `TokenPaged[T]` | `AsyncTokenPaged[T]` | next_page_token/cursor | 数据量大，顺序遍历 |
| `LastIDPaged[T]` | `AsyncLastIDPaged[T]` | last_id | 基于 ID 游标遍历 |

它们共享基类 `PagedBase`（同步）/ `AsyncPagedBase`（异步）。

### 迭代模式一：遍历所有项目（自动翻页）

最简单的用法，直接 `for item in paged` 遍历所有结果，SDK 自动在后台翻页：

```python
from cozepy import Coze, TokenAuth, COZE_CN_BASE_URL

coze = Coze(auth=TokenAuth(token="your_token"), base_url=COZE_CN_BASE_URL)

# NumberPaged 示例：列出所有 Bot
for bot in coze.bots.list(space_id="space_id"):
    print(f"Bot: {bot.bot_id} - {bot.bot_name}")

# 异步版本
# async for bot in async_coze.bots.list(space_id="space_id"):
#     ...
```

### 迭代模式二：逐页遍历

需要控制每页大小时，使用 `iter_pages()` 逐页处理：

```python
paged = coze.bots.list(space_id="space_id", page_size=20)

for page in paged.iter_pages():
    print(f"--- 第 {page.page_num} 页，共 {len(page.items)} 条 ---")
    for bot in page.items:
        print(f"  {bot.bot_name}")
    # 可在此处插入分页间隔逻辑（如进度条、批量处理）
```

`page.items` 是当前页的项目列表。页码分页器还有 `page_num`、`total` 等属性。

### 三种分页器的方法对比

| 操作 | NumberPaged | TokenPaged | LastIDPaged |
|------|-------------|------------|-------------|
| `for item in page` | ✅ 自动翻页 | ✅ 自动翻页 | ✅ 自动翻页 |
| `for page in page.iter_pages()` | ✅ | ✅ | ✅ |
| 跳转到指定页 | ✅（通过 page_num） | ❌ | ❌ |
| 获取总数 | ✅（total 字段） | 取决于 API | 取决于 API |

## 文件管理（Files）

`FilesClient` 通过 `coze.files` 访问，提供文件上传能力。文件上传是使用知识库、图片理解等功能的前置步骤。

```python
# 上传文件
with open("document.pdf", "rb") as f:
    file_obj = coze.files.create(file=f)
    print(f"文件 ID: {file_obj.id}")
```

### File 模型

文件元数据模型，包含文件 ID、文件名、大小、类型等信息。

### _try_fix_file()

内部工具函数，自动处理文件上传时的兼容性问题——如推断 MIME 类型、处理路径格式等。你通常不需要直接调用它。

## 数据集/知识库（Datasets）

`DatasetsClient` 通过 `coze.datasets` 访问（替代已废弃的 `coze.knowledge`）。数据集（Dataset）是 Coze 知识库的核心概念，用于存储和管理向量化的文档和图片。

> ⚠️ `coze.knowledge` 已废弃，使用时会发出 `DeprecationWarning`。请统一使用 `coze.datasets`。

### Dataset 模型

数据集模型包含 ID、名称、描述、状态等信息。

### DatasetStatus（枚举）

数据集处理状态枚举（如处理中、就绪、失败等）。

### DocumentProgress

文档处理进度模型，追踪文档的向量化进度。

### 子客户端

```
DatasetsClient
├── .documents    → 文档管理
└── .images       → 图片管理
```

#### 文档管理（Documents）

管理知识库中的文本文档。

| 模型/枚举 | 说明 |
|-----------|------|
| `Document` | 文档模型 |
| `DocumentBase` | 文档基础信息 |
| `DocumentSourceInfo` | 文档来源信息（本地文件/URL等） |
| `DocumentStatus` | 文档处理状态枚举 |
| `FormatType` | 文档格式类型（PDF/TXT/DOCX等） |
| `SourceType` | 文档来源类型枚举 |
| `UpdateType` | 文档更新类型枚举 |
| `ChunkStrategy` | 文档分块策略枚举 |

#### 图片管理（Images）

管理知识库中的图片资源。

| 模型/枚举 | 说明 |
|-----------|------|
| `Photo` | 图片模型 |
| `PhotoStatus` | 图片处理状态枚举 |

```python
# 列出数据集
for ds in coze.datasets.list(space_id="space_id"):
    print(f"数据集: {ds.id} - {ds.name} (状态: {ds.status})")

# 列出数据集中的文档
for doc in coze.datasets.documents.list(dataset_id="ds_id"):
    print(f"文档: {doc.id} - {doc.name} (状态: {doc.status})")
```

## 工作空间（Workspaces）

`WorkspacesClient` 通过 `coze.workspaces` 访问。工作空间是 Coze 中组织资源（Bot、数据集、工作流等）的顶级容器。

### Workspace 模型

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | `str` | 工作空间 ID |
| `name` | `str` | 工作空间名称 |
| `workspace_type` | `WorkspaceType` | 类型（个人/团队） |
| `role_type` | `WorkspaceRoleType` | 当前用户的角色 |

### 枚举

| 枚举 | 说明 |
|------|------|
| `WorkspaceType` | 工作空间类型（个人/团队） |
| `WorkspaceRoleType` | 角色类型（所有者/编辑者/查看者等） |

### 成员管理

通过 `workspaces.members` 子客户端管理工作空间成员。

```python
# 列出工作空间
for ws in coze.workspaces.list():
    print(f"工作空间: {ws.id} - {ws.name} ({ws.workspace_type})")
```

创建 Bot、数据集等资源时都需要指定 `space_id`（工作空间 ID），通常你需要首先查询可用的工作空间。

## 其他资源客户端

### 模板（Templates）

`TemplatesClient` 通过 `coze.templates` 访问，管理 Bot 模板和提示词模板。

### 用户（Users）

`UsersClient` 通过 `coze.users` 访问，查询当前用户信息和用户相关操作。

### 变量（Variables）

`VariablesClient` 通过 `coze.variables` 访问，管理 Bot 变量和全局变量。变量可以在 Bot 配置和对话中动态替换。

### 文件夹（Folders）

`FoldersClient` 通过 `coze.folders` 访问，提供文件夹管理能力，用于组织 Bot 和资源。

### 连接器（Connectors）

`ConnectorsClient` 通过 `coze.connectors` 访问，包含 `.bots` 子客户端。连接器用于对接外部平台和服务。

### 企业（Enterprises）

通过 `coze.enterprises` 访问，包含 `.members` 和 `.organizations` 子客户端，用于企业级管理。

### API 应用（API Apps）

通过 `coze.api_apps` 访问，管理 API 应用。

### 应用（Apps）

通过 `coze.apps` 访问，包含 `.collaborators` 子客户端，管理 Coze 应用。

### 权益（Benefits）

通过 `coze.benefits` 和 `coze.benefit_limitations` 访问，查询账户权益和权益限制。

### 账单任务（Bill Tasks）

通过 `coze.bill_tasks` 访问，查询计费相关任务。

## 类型安全与自定义头

SDK 的 `py.typed` 文件标记（PEP 561）确保了类型检查器可以验证代码。所有客户端方法都接受 `**kwargs`，其中 `headers` 参数可传递自定义请求头：

```python
# 在任意 API 调用中添加自定义 header
for bot in coze.bots.list(
    space_id="space_id",
    headers={"X-Custom-Trace-ID": "trace-123"},
):
    ...
```

## 相关概念

- [整体架构概览](/concepts/00-overview-architecture.md) — 服务属性一览
- [Bot 管理](/concepts/04-bot-management.md) — Bot 列表分页的使用
- [会话管理](/concepts/06-conversations.md) — 会话和消息列表分页
- [认证体系](/concepts/01-auth-system.md) — 不同认证方式的权限差异
- [数据模型、分页与资源管理参考](/references/data-pagination.md) — 所有模型和枚举的完整 API
