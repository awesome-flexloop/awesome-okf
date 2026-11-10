---
okf_version: "0.2"
type: Example
title: "示例：把代理托管到 Foundry，并用 Handoff 编排分诊"
description: "Foundry Hosted Agents 的最小托管入口、自托管对照、Handoff 的 .NET/Python 声明式拓扑与上线检查点"
tags: [示例, Foundry, 托管, Handoff, 编排]
generated: { by: "blog-article-to-okf-bundle", at: "2026-11-10T15:24:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-11-10T15:24:00+08:00" }
status: stable
stale_after: 2027-05-31
sources:
  - id: build2026
    resource: https://devblogs.microsoft.com/agent-framework/microsoft-agent-framework-at-build-2026-announce/
  - id: learn-hosting
    resource: https://learn.microsoft.com/zh-cn/agent-framework/hosting/
  - id: learn-orchestrations
    resource: https://learn.microsoft.com/zh-cn/agent-framework/workflows/orchestrations/
---

# 示例：把代理托管到 Foundry，并用 Handoff 编排分诊

> 本示例组合官方 Build 2026 公告与托管/编排文档的代码片段，用于演示上线路径；托管资源创建、配额与计费需按 Foundry 文档操作。不是官方原文。

## 目标

1. 用最少代码把本地代理暴露为 Foundry Responses 端点。
2. 理解自托管的等价入口。
3. 用 Handoff 建一个“分诊 → 计费/技术”的拓扑。

## Foundry 托管入口

.NET：

```csharp
using Microsoft.Agents.AI.Foundry.Hosting;

var builder = WebApplication.CreateBuilder(args);
builder.Services.AddFoundryResponses(agent);

var app = builder.Build();
app.MapFoundryResponses();

app.Run();
```

Python：

```python
server = ResponsesHostServer(agent)
server.run()
```

（F-088）

部署前确认：

1. 代理代码已打成容器可运行形态。
2. Foundry 项目、身份与权限已配置。
3. 会话状态与文件系统保留符合预期（托管服务的卖点之一是缩容后保留）。
4. OpenTelemetry 已接 Application Insights。

## 自托管对照

如果不想用 Foundry 托管，用 ASP.NET Core 暴露 OpenAI 兼容端点：

```csharp
using Microsoft.Agents.AI.Hosting;

WebApplicationBuilder builder = WebApplication.CreateBuilder(args);
var hostedAgent = builder.AddAIAgent("weather-agent", (_, _) => agent);

WebApplication app = builder.Build();
app.MapOpenAIResponses(hostedAgent);
app.Run();
```

（F-090）

差别不在代理代码，而在谁负责扩缩容、身份、存储与升级。自托管要自己实现 `AgentSessionStore`（或等价存储）来按延续 ID 加载会话。

## Handoff 拓扑

.NET：

```csharp
using Microsoft.Agents.AI;
using Microsoft.Agents.AI.Workflows;

AIAgent triage = chatClient.AsAIAgent(
    instructions: "You receive a user request and route it to the right specialist.",
    name: "Triage");

AIAgent billing = chatClient.AsAIAgent(
    instructions: "You handle billing questions.", name: "Billing");

AIAgent tech = chatClient.AsAIAgent(
    instructions: "You handle technical support questions.", name: "Tech");

Workflow workflow = AgentWorkflowBuilder
    .CreateHandoffBuilderWith(triage)
    .WithHandoff(triage, billing)
    .WithHandoff(triage, tech)
    .Build();
```

Python：

```python
from agent_framework_orchestrations import HandoffBuilder

workflow = (
    HandoffBuilder(participants=[triage, billing, tech])
    .with_start_agent(triage)
    .add_handoff(triage, [billing, tech])
    .build()
)
```

（F-110）

设计要点：

1. 边是护栏：只声明允许的移交方向。
2. 指令是路由依据：每个专家的 `instructions` 要写清职责边界。
3. 移交不是一次性路由：专家可以追问、再转交（F-109）。

## 上线检查点

- [ ] 托管模型与协议分别选定（两者独立）。
- [ ] 会话存储与多用户归属校验完成。
- [ ] 审批与 FIDES 策略处于生产模式。
- [ ] 可观测性接入，PII 脱敏。
- [ ] 缩容/冷启动延迟可接受。
- [ ] Handoff 拓扑无环或环有终止条件。
- [ ] 成本上限与告警设置。

## 常见错误

| 现象 | 原因 | 处理 |
|------|------|------|
| 托管后会话丢失 | 未使用托管会话或未接 `AgentSessionStore` | 检查会话持久化配置 |
| 端点 404 | 协议包未安装或路由未映射 | 安装协议包并 `Map...` |
| Handoff 来回踢皮球 | 拓扑有环且无终止条件 | 限制边或加兜底代理 |
| 冷启动慢 | 缩容到零 | 评估最小实例数或预热 |
