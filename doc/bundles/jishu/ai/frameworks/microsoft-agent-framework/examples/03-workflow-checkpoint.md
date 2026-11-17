---
okf_version: "0.2"
type: Example
title: "示例：工作流、检查点与人工干预"
description: "构建两个执行器的图工作流、启用检查点存储、从检查点恢复，并在暂停点接入人工输入"
tags: [示例, 工作流, 检查点, HITL, Python]
generated: { by: "blog-article-to-okf-bundle", at: "2026-11-10T15:21:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-11-10T15:21:00+08:00" }
status: stable
stale_after: 2027-05-31
sources:
  - id: learn-wf-start
    resource: https://learn.microsoft.com/zh-cn/agent-framework/get-started/workflows
  - id: learn-checkpoints
    resource: https://learn.microsoft.com/zh-cn/agent-framework/workflows/checkpoints
  - id: learn-hitl
    resource: https://learn.microsoft.com/zh-cn/agent-framework/workflows/human-in-the-loop
---

# 示例：工作流、检查点与人工干预

> 本示例基于官方 get-started 第 5 步、检查点页与 HITL 页的组合改写；API 名称以你安装的版本为准，不是官方原文。

## 目标

1. 定义两个执行器：大写转换与反转。
2. 用 `WorkflowBuilder` 连边并运行。
3. 启用检查点存储，运行后查看检查点。
4. 说明 HITL 的暂停/恢复位置。

## 最小图工作流（Python）

```python
import asyncio
from typing import Never

from agent_framework import WorkflowBuilder, WorkflowContext, executor


@executor(id="upper_case")
async def upper_case(text: str, ctx: WorkflowContext[str]) -> None:
    await ctx.send_message(text.upper())


@executor(id="reverse_text")
async def reverse_text(text: str, ctx: WorkflowContext[Never, str]) -> None:
    await ctx.yield_output(text[::-1])


async def main() -> None:
    workflow = (
        WorkflowBuilder(start_executor=upper_case)
        .add_edge(upper_case, reverse_text)
        .build()
    )
    result = await workflow.run("hello world")
    print(result.get_outputs()[0])


if __name__ == "__main__":
    asyncio.run(main())
```

预期：输出 `DLROW OLLEH`。

## 启用检查点

```python
from agent_framework import InMemoryCheckpointStorage, WorkflowBuilder

checkpoint_storage = InMemoryCheckpointStorage()

builder = WorkflowBuilder(
    start_executor=upper_case,
    checkpoint_storage=checkpoint_storage,
)
builder.add_edge(upper_case, reverse)
workflow = builder.build()

async for event in workflow.run("Hello, World!", stream=True):
    print(event)
```

要点：

1. `storage_path` 对 `FileCheckpointStorage` 是必填项，没有默认目录（文档明确）。
2. 检查点在每个超级步结束时创建，捕获所有执行器状态、待处理消息、请求/响应与共享状态（F-078）。
3. 生产分布式场景用 `CosmosCheckpointStorage`；三者实现同一 `CheckpointStorage` 协议，可替换。

## 从检查点恢复

Python 侧通过检查点存储与运行 API 恢复；.NET 侧通过 `CheckpointManager` 与运行 API：

```csharp
CheckpointManager checkpointManager = CheckpointManager.CreateInMemory();

StreamingRun run = await InProcessExecution
    .RunStreamingAsync(workflow, input, checkpointManager);

IReadOnlyList<CheckpointInfo> checkpoints = run.Checkpoints;
```

（F-078 的 .NET 形态）

恢复前要确认：

1. 工作流定义与检查点版本兼容。
2. 外部副作用有幂等键，避免重复执行。
3. 检查点存储的访问控制与加密到位（`Pickle` 反序列化有代码执行风险）。

## 人工干预的位置

HITL 不是“阻塞线程”，而是“发出请求、保存状态、等待响应、恢复执行”（F-079）：

1. 函数式工作流用 `ctx.request_info()` 发出请求。
2. 图工作流用 `RequestInfoExecutor`。
3. 响应到达后，工作流从暂停点继续；多次 `run` 之间状态保留。

一个安全的设计：

1. 在请求人工输入前创建检查点。
2. 记录请求 ID 与业务单据 ID 的映射。
3. 响应进入前校验操作者权限。
4. 恢复时用幂等键防止重复提交。

## 验证清单

- [ ] 两个执行器都被调用，输出顺序正确。
- [ ] 检查点数量等于超级步数量（或符合入口检查点规则）。
- [ ] 从检查点恢复后，不重复已完成的步骤。
- [ ] HITL 暂停期间没有持续消耗模型 token。

## 常见错误

| 现象 | 原因 | 处理 |
|------|------|------|
| `FileCheckpointStorage` 报缺少路径 | 未传 `storage_path` | 显式指定目录 |
| 恢复后重复发通知 | 外部副作用无幂等键 | 加业务幂等键 |
| HITL 恢复后状态丢失 | 每次请求新建运行上下文 | 复用同一工作流运行/会话 |
| 检查点文件泄露 | 存储位置权限过宽 | 限制目录权限并加密 |
