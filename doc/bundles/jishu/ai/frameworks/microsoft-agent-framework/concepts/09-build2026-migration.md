---
okf_version: "0.2"
type: Concept
title: "Build 2026 新特性与迁移：Harness、Hosted、CodeAct、Copilot SDK、Handoff"
description: "Build 2026 四项公告的机制与边界、CodeAct 基准的厂商自述属性、Semantic Kernel 与 AutoGen 迁移路径、版本时间线与采用建议"
tags: [Build 2026, CodeAct, Hyperlight, GitHub Copilot SDK, Handoff, 迁移]
generated: { by: "blog-article-to-okf-bundle", at: "2026-11-10T15:11:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-11-10T15:11:00+08:00" }
status: stable
stale_after: 2027-05-31
sources:
  - id: build2026
    resource: https://devblogs.microsoft.com/agent-framework/microsoft-agent-framework-at-build-2026-announce/
  - id: learn-migration-sk
    resource: https://learn.microsoft.com/zh-cn/agent-framework/migration-guide/from-semantic-kernel/
  - id: learn-migration-autogen
    resource: https://learn.microsoft.com/zh-cn/agent-framework/migration-guide/from-autogen/
  - id: github-hyperlight
    resource: https://github.com/microsoft/agent-framework/tree/main/python/packages/hyperlight
---

# Build 2026 新特性与迁移：Harness、Hosted、CodeAct、Copilot SDK、Handoff

Build 2026（2026-06-03）的 MAF 公告不是一次普通的版本更新，而是把“代理如何长期干活”这件事产品化：Harness 提供运行时基架，Foundry Hosted 提供生产归宿，CodeAct 降低编排开销，Copilot SDK 与 Handoff 补齐生态与协作模式（F-099）。

这篇文档按“机制—边界—采用建议”拆解四项公告，再讲迁移路径与版本节奏。

## 一、Agent Harness：把生产模式内置

公告把 Harness 描述为“模型推理与真实执行之间的层”：shell 与文件系统访问、人机审批、长会话上下文管理（F-033）。详细机制见 [Agent Harness](03-harness.md)，这里只列公告新增点：

1. 一个方法把聊天客户端变成 Harness（`AsHarnessAgent` / `create_harness_agent`）（F-100）。
2. 自动上下文压缩（需配置预算，见 F-037 的口径差异）。
3. 内置默认指令与指令合并：Harness 指令在前，自定义指令在后（F-042）。
4. 提供程序：FileMemory、FileAccess、Todo、AgentMode、AgentSkills、BackgroundAgents、Web 搜索、Shell（仅 .NET）（F-040）。
5. 中间件：`ToolApprovalAgent`、`OpenTelemetryAgent`、可插拔 `AgentFileStore`（F-041）。

采用建议：如果你在做 Coding/研究/数据分析代理，先评估 Harness 的默认能力是否覆盖 80% 需求；剩下 20% 用自定义提供程序与中间件补，而不是从零拼装。

## 二、Foundry Hosted Agents：从本地到生产

公告的定位是：代理在本地跑通后，下一步是部署、监控、评估、版本化；Foundry Hosted Agents 用容器把你的代码部署到 Foundry 管理的基础设施（F-087）。

核心卖点（F-087）：

1. 缩容到零，空闲不计费。
2. 缩容后文件系统与会话身份保留。
3. 每会话 VM 隔离沙箱。
4. OpenTelemetry 追踪零接线流入 Application Insights。
5. 版本化。

代码入口（F-088）：

```csharp
builder.Services.AddFoundryResponses(agent);
app.MapFoundryResponses();
```

```python
ResponsesHostServer(agent).run()
```

采用建议：先确认区域、配额、冷启动延迟与数据驻留；托管能力细节多为博文单源，落地前查 Foundry 官方文档。

## 三、CodeAct：把多回合压成一回合

### 问题

许多代理的瓶颈不是模型质量，而是编排开销：每次小工具调用都是一次独立模型回合，延迟与 token 用量随步骤数线性增长（F-102）。

### 机制

CodeAct 让模型写一段短 Python 程序，通过 `call_tool(...)` 调用你的工具，在沙箱中运行一次，返回汇总结果（F-103）。它随 `agent-framework-hyperlight`（alpha）发布，每次调用在全新的 Hyperlight micro-VM 中运行模型生成代码（F-104）。

```python
from agent_framework import Agent, tool
from agent_framework_hyperlight import HyperlightCodeActProvider

@tool
def get_weather(city: str) -> dict:
    """Return the current weather for a city."""
    return {"city": city, "temperature_c": 21.5, "conditions": "partly cloudy"}

codeact = HyperlightCodeActProvider(
    tools=[get_weather],
    approval_mode="never_require",
)

agent = Agent(
    client=client,
    name="CodeActAgent",
    instructions="You are a helpful assistant.",
    context_providers=[codeact],
)
```

（F-107 的代码形态）

### 基准与边界

博文给出的代表性多步工作负载对比（F-105）：

| 方式 | 时间 | Tokens |
|------|------|--------|
| 传统 | 27.81s | 6,890 |
| CodeAct | 13.23s | 2,489 |
| 提升 | 52.4% | 63.9% |

**这组数字是厂商自述、单源**：没有测例代码版本、硬件、模型与统计方法；仓库有 benchmark 示例，但文档未给出同一组数字。把它当作“方向性证据”，不要当作 SLA 承诺。

工程边界（F-065、F-106、F-107）：

1. 包为 alpha；安装 `pip install agent-framework-hyperlight --pre`。
2. 后端当前支持 Linux x86_64 与 Windows AMD64 上的 Python 3.11–3.15。
3. `HyperlightCodeActProvider` 注册的工具在沙箱内 `call_tool(...)` 可用，但不作为直接代理工具暴露。
4. **FIDES 不覆盖 CodeAct**：生成代码内的宿主工具调用绕过函数中间件，策略与标签跟踪不生效；宿主工具必须自行授权与限制目标。
5. 需要 FIDES 的工具应保留为直接代理工具，或在相关流程禁用 CodeAct。

采用建议：

1. 工具调用密集、单步逻辑简单、可容忍沙箱冷启动 → 试 CodeAct。
2. 工具涉及敏感数据流 → 先解决 FIDES 边界，再考虑 CodeAct。
3. 不要为了“看起来先进”把单步任务改成 CodeAct；单步调用本来就只需一个回合。

## 四、GitHub Copilot SDK：把编码能力接进 MAF

公告称 GitHub Copilot SDK 集成达到 1.0，把 Copilot 的编码能力（shell 执行、文件操作、URL 获取、MCP 服务器集成）带入 MAF 编程模型（F-108）。

```python
from agent_framework.github import GitHubCopilotAgent

agent = GitHubCopilotAgent(
    default_options={"instructions": "You are a helpful assistant."},
)
```

.NET 用 `CopilotClient.AsAIAgent()`（F-108）。Copilot 代理是标准 MAF 代理，支持工具、指令、流式、会话、MCP 与 OpenTelemetry。

时间线注意：博文 2026-06-03 宣布“reaching 1.0”，独立包 `python-github-copilot-1.0.0` 的 Release 是 2026-07-23（F-108、核验报告）。按“公告先行、包后续发布”理解即可。

## 五、Handoff：让代理在对话中移交

公告把 Handoff 编排带到 1.0（F-109）。它解决的问题是“路由器的第一次追问就崩”：代理需要追问、需要同伴上下文、或中途发现请求不属于自己时，能把控制权移交出去。

```csharp
Workflow workflow = AgentWorkflowBuilder
    .CreateHandoffBuilderWith(triage)
    .WithHandoff(triage, billing)
    .WithHandoff(triage, tech)
    .Build();
```

```python
workflow = (
    HandoffBuilder(participants=[triage, billing, tech])
    .with_start_agent(triage)
    .add_handoff(triage, [billing, tech])
    .build()
)
```

（F-110）

设计原则：**拓扑与护栏由开发者掌握，路由决策由代理掌握**（F-109）。你可以限制谁能转给谁，但不能硬编码“何时转”。

## 六、迁移：从 Semantic Kernel 与 AutoGen

官方提供两份迁移指南（F-113）。

### Semantic Kernel → MAF

主要变化（F-114、F-115）：

1. 命名空间：`Microsoft.SemanticKernel` / `Microsoft.SemanticKernel.Agents` → `Microsoft.Extensions.AI` + `Microsoft.Agents.AI`。
2. 代理创建简化：不再依赖 `Kernel` 实例，直接用聊天客户端构造代理。
3. 线程/会话：`AgentThread` → `AgentSession`，创建、清理、序列化方式变化。
4. 工具注册、流式/非流式调用、选项配置均有对应映射。

官方自述收益：简化 API、更好性能（对象创建与内存优化）、跨提供程序统一接口、更直观的开发者体验（F-114）。这些是厂商表述，迁移前应自己做基准。

### AutoGen → MAF

迁移指南覆盖（F-116）：

1. 模型客户端创建与配置。
2. `AgentSession` 管理聊天状态。
3. 流式、消息类型、工具、托管工具、MCP、代理即工具。
4. 中间件、自定义代理。
5. 工作流 vs GraphFlow。
6. 群组聊天、RoundRobin、MagenticOne 模式映射。

迁移策略建议：

1. 先迁“单代理 + 工具”路径，验证行为等价。
2. 再迁多代理编排；GraphFlow 到工作流的映射不是一对一，需要重画拓扑。
3. 最后迁自定义扩展（中间件、选择器、记忆）。
4. 用同一组评测用例对比迁移前后，不要只看“能跑”。

## 七、版本时间线与采用节奏

| 时间 | 事件 |
|------|------|
| 2025-12 | Python/.NET 1.0 beta 与 preview 密集发布 |
| 2026-04-02 | 1.0 GA（F-002） |
| 2026-06-03 | Build 2026 公告：Harness、Hosted、CodeAct、Copilot SDK、Handoff（F-099） |
| 2026-07-23 | `python-github-copilot-1.0.0` 发布（F-108 口径） |
| 2026-09-11 | `dotnet-1.21.0`（F-008） |
| 2026-10-08 | `python-1.21.0`（F-008） |
| 2026-10~11 | Learn 文档更新，新增 Go 预览说明（F-120） |

采用节奏建议：

1. **新项目**：直接用 1.x 稳定线，Harness 作为长任务默认起点。
2. **SK/AutoGen 存量**：按“单代理 → 多代理 → 扩展”分批迁移，保留回滚。
3. **尝鲜**：CodeAct 与后台代理都标实验/alpha，放独立服务或 feature flag 后。
4. **生产托管**：Foundry 托管已 GA；自托管包仍预发布，需锁定版本并准备升级预算。

## 八、Build 2026 相关 session

博文列出六个 session（F-111）：BRK243（Claw 与 agent harness）、BRK241（原型到生产）、DEM361（可观测性与评估）、DEM333（Foundry 与开源框架集成）、DEM312（三代理三框架）、BRK250（跨框架观测与控制）。这些标题只来自博文，未逐一核对 build.microsoft.com 页面。

## 已知边界

1. CodeAct 基准为厂商自述单源（F-105）。
2. Copilot SDK 的“1.0”时间线存在公告与包发布的时差（F-108）。
3. 迁移指南的“更好性能”是官方自述，未给基准方法（F-114）。
4. Build session 编号与标题为博文单源（F-111）。
