---
type: concept
title: "Bot 管理"
description: "掌握 Bot 的创建、查询、更新、发布/取消发布全生命周期，以及版本管理、协作者和 Bot 配置模型的使用。"
tags: [bot, crud, publish, version, collaborator, configuration]
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

# Bot 管理

Bot（机器人）是 Coze 平台的核心实体，承载了人设、知识库、插件、工作流等配置。`BotsClient` 提供了 Bot 的完整生命周期管理能力，包括创建、查询、更新、发布和版本管理。Bot 管理操作通过 `coze.bots` 访问。

## Bot 模型结构

Bot 是一个复杂的聚合模型，包含多个子模型来描述不同方面的配置：

```
Bot
├── BotModelInfo          — 模型配置（使用哪个 LLM）
├── BotPromptInfo         — Prompt 配置（人设与回复逻辑）
├── BotKnowledge          — 绑定的知识库
├── BotPluginInfo         — 绑定的插件
│   └── BotPluginAPIInfo  — 插件 API 详情
├── BotOnboardingInfo     — 开场白和推荐问题
├── BotVoiceInfo          — 语音配置
├── BotWorkflowInfo       — 绑定的工作流
├── BotSuggestReplyInfo   — 推荐回复配置
├── BotVariable           — Bot 变量
└── BotBackgroundImageInfo — 背景图片
```

### Bot 相关枚举

| 枚举 | 说明 |
|------|------|
| `BotMode` | Bot 运行模式（如单轮/多轮对话模式） |
| `PublishStatus` | 发布状态（已发布/未发布/审核中等） |
| `SuggestReplyMode` | 推荐回复模式 |
| `UserInputType` | 用户输入类型 |
| `VariableType` | 变量类型 |
| `VariableChannel` | 变量作用渠道 |

## Bot 列表查询

使用 `bots.list()` 获取 Bot 列表，返回 `NumberPaged[Bot]` 分页结果：

```python
from cozepy import Coze, TokenAuth, COZE_CN_BASE_URL

coze = Coze(auth=TokenAuth(token="your_token"), base_url=COZE_CN_BASE_URL)

# 遍历所有 Bot（自动翻页）
for bot in coze.bots.list(space_id="your_workspace_id"):
    print(f"Bot ID: {bot.bot_id}, 名称: {bot.bot_name}")

# 逐页遍历
for page in coze.bots.list(space_id="your_workspace_id").iter_pages():
    print(f"当前页有 {len(page.items)} 个 Bot")
    for bot in page.items:
        print(f"  - {bot.bot_name}")
```

`NumberPaged` 分页器支持两种迭代方式：直接 `for bot in page` 遍历所有项目（自动翻页），或 `for page in page.iter_pages()` 逐页处理。详见[分页模式与资源管理](09-pagination-resources.md)。

## 创建 Bot

使用 `bots.create()` 创建新 Bot：

```python
bot = coze.bots.create(
    space_id="your_workspace_id",
    name="我的助手",
    description="一个测试 Bot",
    # 可传入 model_info、prompt_info 等配置
)
print(f"创建成功，Bot ID: {bot.bot_id}")
```

创建时可以配置的核心参数包括：
- `space_id`：所属工作空间 ID
- `name`：Bot 名称
- `description`：Bot 描述
- `model_info`（`BotModelInfo`）：模型选择
- `prompt_info`（`BotPromptInfo`）：Prompt/人设配置
- 其他子模型配置按需传入

## 获取 Bot 详情

使用 `bots.retrieve()` 获取单个 Bot 的完整配置：

```python
bot = coze.bots.retrieve(bot_id="bot_id")
print(f"名称: {bot.bot_name}")
print(f"描述: {bot.description}")

# 查看模型配置
if bot.model_info:
    print(f"模型: {bot.model_info.model_id}")

# 查看 Prompt 配置
if bot.prompt_info:
    print(f"Prompt: {bot.prompt_info.prompt}")
```

## 更新 Bot

使用 `bots.update()` 修改 Bot 配置：

```python
updated_bot = coze.bots.update(
    bot_id="bot_id",
    name="更新后的名称",
    description="更新后的描述",
    # prompt_info=BotPromptInfo(prompt="新的人设..."),
)
```

更新操作是增量的，只修改传入的字段。

## 发布与取消发布

Bot 创建后处于草稿状态，需要发布后才能通过 API 对话：

```python
# 发布 Bot
coze.bots.publish(
    bot_id="bot_id",
    connector_ids=["1"],  # 发布渠道
)

# 取消发布
coze.bots.unpublish(bot_id="bot_id")
```

发布状态通过 `Bot.publish_status` 字段查询。`PublishStatus` 枚举标识了当前 Bot 的发布状态。

## 版本管理

通过 `bots.versions` 子客户端管理 Bot 版本。每次发布 Bot 会生成一个新版本，可以查看历史版本、回滚到特定版本。

```python
# 通过 versions 子客户端访问版本管理功能
versions_client = coze.bots.versions
# versions_client.list()  # 列出版本
# versions_client.retrieve()  # 获取特定版本
```

## 协作者管理

通过 `bots.collaborators` 子管理员管理 Bot 的协作者（编辑者、查看者等），实现多人协作开发 Bot。

```python
collaborators = coze.bots.collaborators
# 添加、移除、列出协作者
```

## 协作模式

通过 `bots.collaboration_modes` 子客户端管理 Bot 的协作模式设置，控制 Bot 的可见性和协作权限。

## 工作空间与 Bot

Bot 必须属于一个工作空间（Workspace）。创建 Bot 时需要指定 `space_id`，即工作空间 ID。可以通过 `coze.workspaces` 客户端查询可用的工作空间：

```python
# 列出工作空间
for ws in coze.workspaces.list():
    print(f"工作空间: {ws.id} - {ws.name} ({ws.workspace_type})")
```

## Bot 配置要点

配置一个可用的 Bot，核心需要设置：

1. **模型选择**（`BotModelInfo`）：选择底层 LLM，不同模型有不同的能力和价格
2. **人设 Prompt**（`BotPromptInfo`）：定义 Bot 的角色、回复风格、约束条件
3. **知识库**（`BotKnowledge`）：绑定知识库让 Bot 检索私有数据
4. **插件**（`BotPluginInfo`）：启用插件让 Bot 调用外部工具
5. **开场白**（`BotOnboardingInfo`）：设置用户首次对话时的欢迎语和推荐问题
6. **工作流**（`BotWorkflowInfo`）：绑定工作流实现复杂任务编排

这些配置在创建或更新 Bot 时通过对应的子模型参数传入。

## 完整使用流程

```
1. 查询工作空间 → 获取 space_id
2. 创建 Bot → 设置名称、人设、模型等
3. （可选）绑定知识库/插件/工作流
4. 发布 Bot → 才能通过 API 对话
5. 调用 chat.stream() → 与发布的 Bot 对话
6. （可选）更新配置 → 更新后重新发布
7. （可选）版本管理 → 查看历史版本、回滚
```

## 相关概念

- [整体架构概览](00-overview-architecture.md) — SDK 整体结构
- [对话与流式处理](03-chat-streaming.md) — 与 Bot 对话的核心机制
- [工作流](05-workflows.md) — 绑定到 Bot 的工作流
- [分页模式与资源管理](09-pagination-resources.md) — 分页器使用
- [工作空间模型](09-pagination-resources.md#工作空间workspaces) — Workspace 管理
- [数据模型、分页与资源管理参考](../references/data-pagination.md) — Bot 模型和枚举的完整 API
