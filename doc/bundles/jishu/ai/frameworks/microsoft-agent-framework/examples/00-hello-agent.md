---
okf_version: "0.2"
type: Example
title: "示例：Hello Agent（Python 与 .NET 最小闭环）"
description: "从安装、配置凭据到运行第一个代理并验证多轮会话的最小步骤，含预期输出与排错点"
tags: [示例, 快速开始, Python, .NET, Foundry]
generated: { by: "blog-article-to-okf-bundle", at: "2026-11-10T15:15:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-11-10T15:15:00+08:00" }
status: stable
stale_after: 2027-05-31
sources:
  - id: learn-first-agent
    resource: https://learn.microsoft.com/zh-cn/agent-framework/get-started/your-first-agent
  - id: learn-multiturn
    resource: https://learn.microsoft.com/zh-cn/agent-framework/get-started/multi-turn
---

# 示例：Hello Agent（Python 与 .NET 最小闭环）

> 本示例是对官方入门页的最小化改写，用于验证环境与凭据；不是官方原文。模型名与终结点需替换为你自己的部署。

## 目标

1. 安装 SDK。
2. 用 Azure CLI 登录并创建代理。
3. 运行一次非流式调用。
4. 用一个会话完成两轮对话，验证上下文保留。

## 前置条件

1. 一个 Microsoft Foundry 项目与模型部署。
2. Python 3.11+ 或 .NET 8+。
3. 已安装 Azure CLI，并执行 `az login`。
4. 环境变量：`FOUNDRY_PROJECT_ENDPOINT`、`FOUNDRY_MODEL`（.NET 示例可用 `AZURE_OPENAI_ENDPOINT` / `AZURE_OPENAI_DEPLOYMENT_NAME`）。

## Python 步骤

安装：

```bash
pip install agent-framework azure-identity
```

`hello_agent.py`：

```python
import asyncio
import os

from agent_framework import Agent
from agent_framework.foundry import FoundryChatClient
from azure.identity import AzureCliCredential


async def main() -> None:
    agent = Agent(
        client=FoundryChatClient(
            project_endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
            model=os.environ["FOUNDRY_MODEL"],
            credential=AzureCliCredential(),
        ),
        name="HelloAgent",
        instructions="You are a friendly assistant. Keep your answers brief.",
    )

    print(await agent.run("What is the largest city in France?"))

    session = agent.create_session()
    print(await agent.run("My name is Alice.", session=session))
    print(await agent.run("What is my name?", session=session))


if __name__ == "__main__":
    asyncio.run(main())
```

运行：

```bash
python hello_agent.py
```

预期：

1. 第一次调用返回巴黎相关回答。
2. 第二次调用确认名字是 Alice。
3. 第三次调用能回答“Alice”，证明会话生效。

## .NET 步骤

```bash
dotnet add package Microsoft.Agents.AI
dotnet add package Microsoft.Agents.AI.Foundry
dotnet add package Azure.AI.Projects
dotnet add package Azure.Identity
```

```csharp
using Azure.AI.Projects;
using Azure.Identity;
using Microsoft.Agents.AI;

var endpoint = Environment.GetEnvironmentVariable("AZURE_OPENAI_ENDPOINT")
    ?? throw new InvalidOperationException("Set AZURE_OPENAI_ENDPOINT");
var deployment = Environment.GetEnvironmentVariable("AZURE_OPENAI_DEPLOYMENT_NAME") ?? "gpt-4o-mini";

AIAgent agent = new AIProjectClient(new Uri(endpoint), new DefaultAzureCredential())
    .AsAIAgent(
        model: deployment,
        instructions: "You are a friendly assistant. Keep your answers brief.",
        name: "HelloAgent");

AgentSession session = await agent.CreateSessionAsync();
Console.WriteLine(await agent.RunAsync("My name is Alice.", session));
Console.WriteLine(await agent.RunAsync("What is my name?", session));
```

## 验证清单

- [ ] `az login` 成功，且当前账号能访问 Foundry 项目。
- [ ] `FOUNDRY_MODEL` 是**部署名**，不是模型家族名。
- [ ] 第二次调用能记住 Alice。
- [ ] 若使用 `.env`，Python 已调用 `load_dotenv()`。

## 常见错误

| 现象 | 原因 | 处理 |
|------|------|------|
| `DefaultAzureCredential` 超时 | 本地未登录或多凭据探测 | 先 `az login`；生产改用托管身份 |
| 404 / deployment not found | 模型参数填了模型名 | 改为部署名 |
| 环境变量为空 | `.env` 未加载 | `load_dotenv()` 或直接导出变量 |
| 第二轮忘记名字 | 未复用同一个 session | 把 `session` 传给每次 `run` |
