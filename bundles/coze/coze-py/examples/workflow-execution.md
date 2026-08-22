---
type: example
title: "工作流执行示例"
description: "演示工作流的流式对话、runs 流式执行、事件类型处理和中断恢复模式，覆盖同步流式和异步运行场景。"
tags: [workflow, stream, run, event, interrupt, resume, async]
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

# 工作流执行示例

本示例演示使用 cozepy 执行工作流的多种模式：工作流式对话（复用 ChatEvent）、runs 流式执行、事件处理，以及中断恢复的基本模式。

## 前置准备

1. 在 Coze 平台创建一个工作流并发布
2. 获取工作流 ID
3. 配置 PAT Token（参见[基础对话示例](/examples/basic-chat.md)）

## 完整代码

```python
import os
import time
from cozepy import (
    Coze,
    TokenAuth,
    Message,
    ChatEventType,
    COZE_CN_BASE_URL,
    CozeAPIError,
)


def workflow_chat(workflow_id: str, user_id: str, question: str) -> str:
    """
    工作流式对话：以对话方式运行工作流，复用 ChatEvent 事件体系。
    适用于有自然语言输入输出的工作流场景。

    Args:
        workflow_id: 工作流 ID
        user_id: 用户标识
        question: 输入问题/文本

    Returns:
        工作流输出文本
    """
    coze = Coze(
        auth=TokenAuth(token=os.environ["COZE_API_TOKEN"]),
        base_url=COZE_CN_BASE_URL,
    )

    full_output = ""
    print(f"[工作流聊天] 输入: {question}")
    print("输出: ", end="", flush=True)

    # workflows.chat.stream() 返回 Stream[ChatEvent]，
    # 事件处理方式与 chat.stream() 完全一致
    for event in coze.workflows.chat.stream(
        workflow_id=workflow_id,
        additional_messages=[
            Message.build_user_question_text(question),
        ],
        parameters={"key": "value"},  # 工作流输入参数（按需传入）
        # app_id="your_app_id",     # 可选：关联应用 ID
        # bot_id="your_bot_id",     # 可选：关联 Bot ID
    ):
        if event.event == ChatEventType.CONVERSATION_MESSAGE_DELTA:
            content = event.message.content
            full_output += content
            print(content, end="", flush=True)

        elif event.event == ChatEventType.CONVERSATION_CHAT_COMPLETED:
            chat = event.chat
            print()  # 换行
            if chat.last_error:
                print(f"[错误] {chat.last_error.code}: {chat.last_error.msg}")
            else:
                print(f"[完成] Token 消耗: {chat.usage.token_count}")

    return full_output


def workflow_run_stream(workflow_id: str, parameters: dict) -> None:
    """
    工作流 runs 流式执行：使用 WorkflowEvent 事件体系。
    适用于结构化输入输出的数据处理、内容生成场景。

    Args:
        workflow_id: 工作流 ID
        parameters: 工作流输入参数字典
    """
    coze = Coze(
        auth=TokenAuth(token=os.environ["COZE_API_TOKEN"]),
        base_url=COZE_CN_BASE_URL,
    )

    print(f"\n[工作流运行] 参数: {parameters}")
    print("-" * 40)

    for event in coze.workflows.runs.stream(
        workflow_id=workflow_id,
        parameters=parameters,
    ):
        event_type = event.event

        # WorkflowEvent 有三种类型：MESSAGE / ERROR / INTERRUPT
        if event_type == "MESSAGE":
            # 消息事件：工作流节点产生的输出
            msg_content = event.message.content if hasattr(event, 'message') else str(event.data)
            print(f"[输出] {msg_content}")

        elif event_type == "ERROR":
            # 错误事件
            print(f"[错误] {event.error.code}: {event.error.message}")
            break

        elif event_type == "INTERRUPT":
            # 中断事件：需要人工介入
            interrupt_data = event.interrupt.data
            print(f"[中断] 需要补充信息")
            print(f"  中断详情: {interrupt_data}")
            # 在实际应用中，这里会暂停执行，
            # 等待用户提供信息后恢复（见下方 interrupt_resume_demo）


def workflow_run_with_history(workflow_id: str) -> None:
    """
    查询工作流运行历史。

    Args:
        workflow_id: 工作流 ID
    """
    coze = Coze(
        auth=TokenAuth(token=os.environ["COZE_API_TOKEN"]),
        base_url=COZE_CN_BASE_URL,
    )

    print(f"\n[运行历史] 工作流: {workflow_id}")
    print("-" * 40)

    # 查询运行历史（分页）
    history_paged = coze.workflows.run_histories.list(workflow_id=workflow_id)
    for history in history_paged:
        print(f"  运行 ID: {history.id if hasattr(history, 'id') else 'N/A'}, "
              f"状态: {history.status if hasattr(history, 'status') else 'N/A'}")


def interrupt_resume_demo(workflow_id: str) -> None:
    """
    中断与恢复模式演示（伪代码框架）。
    当工作流遇到 INTERRUPT 事件时暂停，用户输入后恢复执行。

    实际使用时，需要根据工作流的中断节点设计具体的交互逻辑。
    """
    coze = Coze(
        auth=TokenAuth(token=os.environ["COZE_API_TOKEN"]),
        base_url=COZE_CN_BASE_URL,
    )

    print(f"\n[中断恢复演示]")
    print("-" * 40)

    # 第一轮：启动工作流，可能遇到中断
    interrupt_info = None
    for event in coze.workflows.runs.stream(
        workflow_id=workflow_id,
        parameters={"input": "需要审批的数据"},
    ):
        if event.event == "MESSAGE":
            print(f"[输出] {event.data if hasattr(event, 'data') else event}")

        elif event.event == "INTERRUPT":
            # 收到中断事件，保存中断信息
            interrupt_info = event.interrupt.data
            print(f"[中断] 工作流暂停，等待确认")
            print(f"  提示: {interrupt_info}")

        elif event.event == "ERROR":
            print(f"[错误] {event.error}")
            return

    # 如果遇到中断，等待用户输入后恢复
    if interrupt_info:
        print("\n>>> 请在控制台输入确认信息（输入 'approve' 继续）: ")
        user_input = input().strip()

        if user_input.lower() == "approve":
            print("[恢复] 提交用户输入，继续执行工作流...")

            # 恢复执行（具体 API 取决于工作流中断节点的设计）
            # 恢复时传入中断信息和用户输入
            for event in coze.workflows.runs.stream(
                workflow_id=workflow_id,
                parameters={
                    # 传入中断恢复所需的参数
                    "interrupt_data": interrupt_info,
                    "user_input": user_input,
                },
            ):
                if event.event == "MESSAGE":
                    print(f"[输出] {event.data if hasattr(event, 'data') else event}")
                elif event.event == "ERROR":
                    print(f"[错误] {event.error}")
        else:
            print("[终止] 用户未确认，工作流终止")


if __name__ == "__main__":
    WORKFLOW_ID = "your_workflow_id_here"
    USER_ID = "user_001"

    # 1. 工作流式对话（ChatEvent 体系）
    workflow_chat(WORKFLOW_ID, USER_ID, "帮我分析以下数据并生成摘要")

    # 2. 工作流 runs 流式执行（WorkflowEvent 体系）
    workflow_run_stream(WORKFLOW_ID, {"input": "测试数据", "format": "summary"})

    # 3. 查询运行历史
    # workflow_run_with_history(WORKFLOW_ID)

    # 4. 中断恢复（需要配置支持中断的工作流节点）
    # interrupt_resume_demo(WORKFLOW_ID)
```

## 代码解析

### 两种调用方式对比

SDK 提供两种执行工作流的方式：

| 方式 | 入口 | 事件类型 | 适用场景 |
|------|------|---------|---------|
| 工作流式对话 | `workflows.chat.stream()` | ChatEvent（同 chat.stream） | 自然语言对话，消息增量输出 |
| 工作流运行 | `workflows.runs.stream()` | WorkflowEvent（MESSAGE/ERROR/INTERRUPT） | 结构化数据处理，支持中断 |

### ChatEvent 复用

`workflows.chat.stream()` 返回的事件类型与 `chat.stream()` 完全相同（都是 `ChatEvent`），这意味着你可以复用同一个事件处理函数来处理 Bot 对话和工作流对话。这是 SDK 设计中的一个重要复用模式——内部的 `_chat_stream_handler` SSE 解析器被两个模块共享。

### WorkflowEvent 三种类型

`workflows.runs.stream()` 返回独立的 `WorkflowEvent` 体系：
- **MESSAGE**：工作流节点产生的输出数据
- **ERROR**：执行错误（code + message）
- **INTERRUPT**：工作流暂停，等待外部输入

### 中断恢复模式

中断恢复是工作流区别于普通对话的重要特性。典型流程：
1. 启动工作流执行
2. 遇到 `INTERRUPT` 事件，保存中断数据
3. 暂停执行，获取用户输入或执行人工操作
4. 使用中断数据和用户输入恢复执行
5. 继续处理后续事件直到 MESSAGE 或 ERROR

这种模式支持"人在回路"（Human-in-the-Loop）场景，如审批流程、信息确认等。

### 运行历史

通过 `workflows.run_histories` 子客户端可以查询历史运行记录，方便审计和追溯。

## 相关概念

- [工作流](/concepts/05-workflows.md) — 工作流架构和事件体系详解
- [对话与流式处理](/concepts/03-chat-streaming.md) — ChatEvent 事件处理
- [基础对话示例](/examples/basic-chat.md) — 基础 SSE 流式对话
- [对话与工作流参考](/references/chat-workflow.md) — WorkflowsClient 完整 API
