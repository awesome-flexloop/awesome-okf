---
type: concept
title: "工作流"
description: "理解 WorkflowsClient 的工作流执行、流式对话、异步运行与中断恢复机制，以及 WorkflowEvent 事件体系。"
tags: [workflow, stream, async, interrupt, resume, run, event]
generated: { by: "process:source-code-to-okf-wiki", at: "2026-08-23T02:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-08-23T02:00:00Z" }
status: stable
stale_after: 2027-08-23
sources:
  - id: F-cp-003
    resource: /references/chat-workflow.md
    title: "对话与工作流参考"
  - id: F-cp-001
    resource: /references/coze-client.md
    title: "Coze 客户端入口与基础设施参考"
---

# 工作流

工作流（Workflow）是 Coze 平台的任务编排能力，允许你将多个 LLM 调用、插件、代码节点、条件分支等组合成一个有向无环图（DAG），实现复杂的多步任务。与直接与 Bot 对话不同，工作流提供了更精确的输入/输出控制、异步执行、中断恢复等能力，适合数据处理、内容生成、多步骤推理等场景。

## WorkflowsClient 入口

`WorkflowsClient`（异步版本 `AsyncWorkflowsClient`）通过 `coze.workflows` 访问。它包含多个子客户端，分别负责不同方面：

```
WorkflowsClient
├── .chat            → WorkflowsChatClient      工作流式对话（复用 ChatEvent）
├── .runs            → WorkflowsRunsClient      工作流运行（流式/异步）
├── .run_histories   → WorkflowRunHistoriesClient 运行历史
├── .versions        → WorkflowVersionsClient   版本管理
└── .collaborators   → WorkflowCollaboratorsClient 协作者管理
```

## 工作流流式对话

`workflows.chat.stream()` 方法以对话方式运行工作流，接口设计与 `chat.stream()` 高度一致，同样返回 `Stream[ChatEvent]`，SSE 事件处理方式完全相同。HTTP 端点为 `POST /v1/workflows/chat`。

```python
from cozepy import Coze, TokenAuth, Message, ChatEventType, COZE_CN_BASE_URL

coze = Coze(auth=TokenAuth(token="your_token"), base_url=COZE_CN_BASE_URL)

for event in coze.workflows.chat.stream(
    workflow_id="your_workflow_id",
    additional_messages=[
        Message.build_user_question_text("帮我分析这段数据"),
    ],
    parameters={"key": "value"},  # 工作流输入参数
    app_id="your_app_id",         # 可选：关联应用 ID
    bot_id="your_bot_id",         # 可选：关联 Bot ID
    conversation_id=None,         # 可选：会话 ID
):
    if event.event == ChatEventType.CONVERSATION_MESSAGE_DELTA:
        print(event.message.content, end="", flush=True)
    elif event.event == ChatEventType.CONVERSATION_CHAT_COMPLETED:
        print("\n工作流对话完成")
```

### 与 chat.stream() 的区别

| 特性 | chat.stream() | workflows.chat.stream() |
|------|---------------|------------------------|
| 入口 | `bot_id` | `workflow_id`（必选） |
| 参数 | 对话消息 | 消息 + parameters（工作流输入参数） |
| 事件类型 | ChatEvent | ChatEvent（完全复用） |
| 场景 | 与 Bot 自由对话 | 运行特定工作流 |
| 关联 | 不需要 app_id | 可关联 app_id/bot_id |

这意味着你在 Chat 模块学到的 SSE 事件处理模式可以直接复用到工作流对话中——相同的 `ChatEventType`、相同的消息增量处理逻辑。

## 工作流运行（Runs）

`workflows.runs` 子客户端提供工作流的流式运行能力，返回 `Stream[WorkflowEvent]`。与 chat 模式不同，workflow runs 使用独立的事件体系 `WorkflowEvent`。

### WorkflowEvent 事件类型

工作流运行时产生三种核心事件：

| 事件类型 | 对应类 | 说明 |
|----------|--------|------|
| `MESSAGE` | `WorkflowEventMessage` | 输出消息事件（工作流节点产生的输出） |
| `ERROR` | `WorkflowEventError` | 错误事件（code + message） |
| `INTERRUPT` | `WorkflowEventInterrupt` | 中断事件（需要人工介入） |

```python
from cozepy import Coze, TokenAuth, COZE_CN_BASE_URL

coze = Coze(auth=TokenAuth(token="your_token"), base_url=COZE_CN_BASE_URL)

for event in coze.workflows.runs.stream(
    workflow_id="your_workflow_id",
    parameters={"input": "data"},
):
    event_type = event.event

    if event_type == "MESSAGE":
        print(f"输出: {event.message.content}")
    elif event_type == "ERROR":
        print(f"错误: {event.error.code} - {event.error.message}")
    elif event_type == "INTERRUPT":
        print(f"工作流中断，需要补充信息")
        # event.interrupt.data 包含中断详情
```

## 异步运行与中断恢复

工作流的一个重要特性是支持**中断（Interrupt）和恢复（Resume）**。当工作流执行到需要人工确认、补充信息或审批的节点时，会发出 `WorkflowEventInterrupt` 事件，暂停执行等待外部输入。

### 中断场景

典型的中断场景包括：
- **需要人工审批**：工作流到达决策节点，需要用户确认后才能继续
- **信息不足**：工作流需要用户补充参数或选择
- **等待外部系统**：工作流等待外部回调或异步操作完成

### 中断数据

`WorkflowEventInterrupt.data`（`WorkflowEventInterruptData` 类型）包含：
- 中断节点的标识
- 需要用户提供的数据描述
- 中断的上下文信息

### 恢复执行

用户提供所需信息后，可以恢复工作流执行。恢复时将中断数据和用户输入一起提交，工作流从中断处继续执行。这种模式使得工作流可以处理"人在回路"（Human-in-the-Loop）的复杂场景。

## 工作流基础模型

### WorkflowBasic

工作流基础信息：

| 字段 | 说明 |
|------|------|
| `workflow_id` | 工作流唯一 ID |
| `name` | 工作流名称 |
| `description` | 工作流描述 |

### WorkflowInfo

工作流详细信息，继承 WorkflowBasic，包含创建时间、更新时间、版本等元数据。

### WorkflowMode（枚举）

工作流运行模式枚举。

### WorkflowVersionInfo

工作流版本信息，记录版本号、发布时间、发布者等。

### WorkflowRunResult

工作流运行的最终结果。

### WorkflowRunHistory

工作流运行历史记录，可通过 `workflows.run_histories` 查询历史执行记录。

## 版本管理

通过 `workflows.versions` 子客户端管理工作流版本。每次发布工作流时会生成新版本，支持版本回滚。

## 协作者管理

通过 `workflows.collaborators` 子客户端管理工作流的协作者，支持多人协作编辑工作流。

## 工作流使用场景

| 场景 | 推荐方式 | 理由 |
|------|---------|------|
| 数据处理管道 | `workflows.runs.stream()` | 精确的输入输出控制，结构化输出 |
| 内容生成流水线 | `workflows.runs.stream()` | 多步骤生成，可中断确认 |
| 对话式工作流 | `workflows.chat.stream()` | 自然语言交互，复用 ChatEvent |
| 人在回路审批 | interrupt + resume | 中断等待人工确认后恢复 |
| 批量任务 | 异步运行 + 查询历史 | 提交后查询结果，不必保持连接 |

## 工作流与 Bot 的关系

工作流和 Bot 是两种不同的抽象：
- **Bot** 是面向对话的实体，有"人格"，用户通过自然语言与之自由对话
- **工作流** 是面向任务的编排，有明确的输入/输出，按预定义流程执行

工作流可以绑定到 Bot（通过 `BotWorkflowInfo`），Bot 在对话中可以调用工作流。你也可以直接通过 `workflows.runs` 或 `workflows.chat` 独立运行工作流，无需通过 Bot。

## 相关概念

- [对话与流式处理](03-chat-streaming.md) — ChatEvent 事件体系，workflows.chat.stream 复用
- [Bot 管理](04-bot-management.md) — Bot 可以绑定工作流
- [工作流执行示例](../examples/workflow-execution.md) — 流式/异步/中断恢复的完整代码
- [对话与工作流参考](../references/chat-workflow.md) — WorkflowsClient 和 WorkflowEvent 的完整 API
