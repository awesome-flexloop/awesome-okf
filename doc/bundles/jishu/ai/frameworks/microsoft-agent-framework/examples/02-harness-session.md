---
okf_version: "0.2"
type: Example
title: "示例：Harness 代理与会话复用"
description: "用 create_harness_agent 创建带规划/待办/压缩的代理，跨轮次复用会话，并关闭不需要的文件记忆与 Web 搜索"
tags: [示例, Harness, 会话, 压缩, Python]
generated: { by: "blog-article-to-okf-bundle", at: "2026-11-10T15:19:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-11-10T15:19:00+08:00" }
status: stable
stale_after: 2027-05-31
sources:
  - id: learn-harness-start
    resource: https://learn.microsoft.com/zh-cn/agent-framework/get-started/harness
  - id: learn-harness
    resource: https://learn.microsoft.com/zh-cn/agent-framework/concepts/harness
---

# 示例：Harness 代理与会话复用

> 本示例基于官方 get-started 第 6 步与 Harness 概念页改写，用于演示“长任务代理 + 会话状态”的最小结构；不是官方原文。

## 目标

1. 用 `create_harness_agent` 创建 Harness 代理。
2. 关闭本示例不需要的文件记忆与 Web 搜索，避免副作用。
3. 跨两轮复用同一个会话，验证计划/待办状态保留。

## 代码

```python
import asyncio

from agent_framework import create_harness_agent
from agent_framework.foundry import FoundryChatClient
from azure.identity import AzureCliCredential


async def main() -> None:
    agent = create_harness_agent(
        client=FoundryChatClient(
            project_endpoint="https://your-account.services.ai.azure.com/api/projects/your-project",
            model="your-deployment-name",
            credential=AzureCliCredential(),
        ),
        agent_instructions="Help users plan and complete multi-step tasks.",
        disable_file_memory=True,
        disable_web_search=True,
    )

    session = agent.create_session()

    print(await agent.run("Plan a weekend trip to Seattle.", session=session))
    print(await agent.run("Turn that plan into a checklist.", session=session))


if __name__ == "__main__":
    asyncio.run(main())
```

## 为什么这样配置

1. **`disable_file_memory=True`**：示例不需要写盘；生产环境若要跨进程保留笔记，应保留文件记忆并配置 `AgentFileStore`。
2. **`disable_web_search=True`**：避免示例在无网络/无配额环境失败；需要实时信息时再打开。
3. **`session` 复用**：Harness 的计划、待办与历史都在会话里；不传 session，第二轮就看不到第一轮的计划（F-044）。

## 压缩的配置提醒

Harness 提供压缩机制，但在 .NET/Python 中需要提供令牌限制或自定义策略才启用（F-037）。如果你不设置预算，不要假设上下文会自动压缩。一个实践起点：

1. 设置最大上下文窗口与最大输出。
2. 观察长任务第 10+ 轮的 token 曲线。
3. 再决定用摘要、截断还是技能卸载。

## 验证清单

- [ ] 第二轮能引用第一轮的计划。
- [ ] 没有生成 `agent-file-memory/` 目录（因为关闭了文件记忆）。
- [ ] 长任务下上下文没有无限增长（配置压缩后）。
- [ ] 工具审批提示可被交互式处理（Harness 默认启用审批）。

## .NET 对照

```csharp
AIAgent agent = chatClient.AsHarnessAgent();
AgentSession session = await agent.CreateSessionAsync();

await foreach (var update in agent.RunStreamingAsync("Plan a weekend trip to Seattle.", session))
{
    Console.Write(update);
}
```

（F-035、F-100）

## 常见错误

| 现象 | 原因 | 处理 |
|------|------|------|
| 第二轮丢失计划 | 每轮新建 session | 复用同一 session |
| 上下文溢出 | 未配置压缩预算 | 设置上下文/输出上限或自定义策略 |
| 代理反复请求审批 | 未配置“不再询问”规则 | 使用 `ToolApprovalAgent` 的审批规则 |
| 生产环境写盘越权 | 文件访问默认关闭但被手动打开 | 明确文件根目录与权限 |
