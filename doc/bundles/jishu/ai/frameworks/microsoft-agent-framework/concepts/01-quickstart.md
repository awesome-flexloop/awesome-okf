---
okf_version: "0.2"
type: Concept
title: "快速开始：安装、最小代理与会话"
description: "Python 与 .NET 的安装命令、最小代理代码、run/stream 两种执行方式、AgentSession 多轮对话、凭据与 .env 的常见坑"
tags: [快速开始, 安装, AgentSession, Foundry, Python, .NET]
generated: { by: "blog-article-to-okf-bundle", at: "2026-11-10T14:47:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-11-10T14:47:00+08:00" }
status: stable
stale_after: 2027-05-31
sources:
  - id: learn-quickstart
    resource: https://learn.microsoft.com/zh-cn/agent-framework/get-started/your-first-agent
  - id: learn-multiturn
    resource: https://learn.microsoft.com/zh-cn/agent-framework/get-started/multi-turn
  - id: learn-overview
    resource: https://learn.microsoft.com/zh-cn/agent-framework/overview/
---

# 快速开始：安装、最小代理与会话

MAF 的上手门槛不高：一个模型客户端加一句指令，就能得到一个可运行的代理。但“能跑”和“跑对”之间有几处容易踩的坑——凭据、`.env`、会话复用。这篇文档把最小路径和坑一起讲清楚。

## 安装

**Python**

```bash
pip install agent-framework
```

`agent-framework` 是元包，会安装 core 与许多可选集成；如果只需要 Foundry 集成，用 `agent-framework-foundry`，它会安装 `agent-framework-core` 加 Foundry 部分（F-006）。

**.NET**

```bash
dotnet add package Microsoft.Agents.AI
dotnet add package Microsoft.Agents.AI.Foundry
dotnet add package Azure.AI.Projects
dotnet add package Azure.Identity
```

`Microsoft.Agents.AI` 是核心包，Foundry 集成与 Azure 身份/项目客户端需要额外包（F-007）。

## 第一个代理（Python）

```python
import asyncio

from agent_framework import Agent
from agent_framework.foundry import FoundryChatClient
from azure.identity import AzureCliCredential


async def main() -> None:
    agent = Agent(
        client=FoundryChatClient(
            project_endpoint="https://your-account.services.ai.azure.com/api/projects/your-project",
            model="your-deployment-name",
            credential=AzureCliCredential(),
        ),
        instructions="You are a friendly assistant. Keep your answers brief.",
    )
    print(await agent.run("What is the largest city of France?"))


if __name__ == "__main__":
    asyncio.run(main())
```

这段结构对应文档的最小示例（F-013）：`Agent` 负责代理抽象，`FoundryChatClient` 负责模型连接，`instructions` 是系统指令，`run` 返回响应。

## 第一个代理（.NET）

```csharp
using Azure.AI.Projects;
using Azure.Identity;
using Microsoft.Agents.AI;

var endpoint = Environment.GetEnvironmentVariable("AZURE_OPENAI_ENDPOINT")
    ?? throw new InvalidOperationException("Set AZURE_OPENAI_ENDPOINT");
var deploymentName = Environment.GetEnvironmentVariable("AZURE_OPENAI_DEPLOYMENT_NAME") ?? "gpt-4o-mini";

AIAgent agent = new AIProjectClient(new Uri(endpoint), new DefaultAzureCredential())
    .AsAIAgent(
        model: deploymentName,
        instructions: "You are a friendly assistant. Keep your answers brief.",
        name: "HelloAgent");

Console.WriteLine(await agent.RunAsync("What is the largest city in France?"));
```

`AsAIAgent` 是 .NET 的常用入口；所有代理实现共享 `AIAgent` 抽象，因此后续的工具、中间件、工作流代码可以面向同一接口编写（F-014、F-018）。

## 流式与非流式

非流式一次拿到完整响应；流式逐步输出，适合终端或聊天 UI。.NET 用 `RunStreamingAsync`（F-015）：

```csharp
await foreach (var update in agent.RunStreamingAsync("Tell me a one-sentence fun fact."))
{
    Console.Write(update);
}
```

Python 的流式响应对象可以先迭代展示增量，再取聚合后的完整响应，且不会重复迭代（F-015）。这一点在实现“边显示边记录”的 UI 时很有用。

## 多轮对话：会话是显式对象

MAF 不会把对话历史藏在全局变量里。要跨轮次保留上下文，必须创建并复用 `AgentSession`（F-027、F-028）：

```python
session = agent.create_session()

first = await agent.run("My name is Alice.", session=session)
second = await agent.run("What is my name?", session=session)

serialized = session.to_dict()
resumed = AgentSession.from_dict(serialized)
```

.NET 对应 `CreateSessionAsync()`、`SerializeSession` / `DeserializeSessionAsync`。会话是代理/提供程序专用的；用另一个代理配置复用同一会话，可能导致上下文失效（F-028）。

如果历史由服务托管，会话里会带 `service_session_id`。这类 ID 默认只限定到 API key 或项目，**不能当作最终用户授权边界**（F-029）。多用户应用应把服务端 ID 存在可信存储里，客户端只拿到你自己的会话标识，恢复前校验归属。

## 四个常见坑

1. **`.env` 不会自动加载**。Python 必须在启动时 `load_dotenv()`，否则环境变量读不到（F-009）。
2. **`DefaultAzureCredential` 只适合开发**。文档明确警告：生产环境应使用 `ManagedIdentityCredential` 等特定凭据，避免延迟、意外凭据探测与回退风险（F-014 的配套警告）。
3. **模型部署名不是模型名**。`model` 参数填的是部署名；填错会在服务端报找不到部署。
4. **会话不是线程安全的共享状态**。并发请求应各自持有会话，或由应用层做串行化；文档没有承诺并发复用同一会话的安全性。

## 从最小代理到生产

最小代理只证明了“模型能回话”。要变成生产代理，按官方七步路径逐步加能力（F-004 的文档结构）：

1. 第一个代理与工具（本文 + [工具、技能与 MCP](04-tools-skills-mcp.md)）
2. 多轮对话（本文）
3. 内存与持久性（[记忆、RAG 与多用户边界](05-memory-rag.md)）
4. 工作流（[工作流与编排](07-workflows.md)）
5. Harness（[Agent Harness](03-harness.md)）
6. 托管（[托管、协议与运维](08-hosting-operations.md)）

## 示例

可演练版本见 [Hello Agent：Python 与 .NET 最小闭环](../examples/00-hello-agent.md)，其中包含环境变量、运行命令与预期输出。

## 已知边界

1. 文档示例中的模型名随版本变化（概述页与入门页使用的示例模型并不一致），本文用 `your-deployment-name` 占位。
2. Foundry 项目终结点格式以你所在租户的实际资源为准；本文不复制具体资源 ID。
3. 会话序列化格式属于实现细节，跨版本恢复前应做兼容性测试。
