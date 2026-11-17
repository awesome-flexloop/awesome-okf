---
okf_version: "0.2"
type: Concept
title: "工作流与编排：图、检查点、人工干预与五种模式"
description: "图 API 与函数式 API 的取舍、执行器/边/事件/状态、检查点与恢复、HITL 请求响应、顺序/并发/移交/群聊/Magentic 五种编排"
tags: [工作流, 编排, 检查点, HITL, Handoff, Magentic, 群组聊天]
generated: { by: "blog-article-to-okf-bundle", at: "2026-11-10T15:05:00+08:00" }
verified: { by: "process:seven-concepts-v", at: "2026-11-10T15:05:00+08:00" }
status: stable
stale_after: 2027-05-31
sources:
  - id: learn-workflows
    resource: https://learn.microsoft.com/zh-cn/agent-framework/concepts/workflows/
  - id: learn-wf-features
    resource: https://learn.microsoft.com/zh-cn/agent-framework/workflows/
  - id: learn-checkpoints
    resource: https://learn.microsoft.com/zh-cn/agent-framework/workflows/checkpoints
  - id: learn-hitl
    resource: https://learn.microsoft.com/zh-cn/agent-framework/workflows/human-in-the-loop
  - id: learn-orchestrations
    resource: https://learn.microsoft.com/zh-cn/agent-framework/workflows/orchestrations/
---

# 工作流与编排：图、检查点、人工干预与五种模式

当任务从“一次对话”变成“多步骤、多角色、要能恢复”，代理的自主循环就不够了。你需要一条显式、可检查的执行路径。这就是 MAF 工作流要解决的问题（F-071）。

## 两种 API，一种结果

所有 SDK 都支持基于图的工作流；Python 额外提供实验性的函数式工作流 API（F-072）。两者产出相同的可观察工作流结果，但表达方式不同（F-074）：

| 维度 | 函数式（`@workflow` / `@step`） | 图（`WorkflowBuilder` / `workflow.NewBuilder`） |
|------|-------------------------------|-----------------------------------------------|
| 控制流 | 原生 Python：`if`、循环、`asyncio.gather` | 边与条件 |
| 最适合 | 顺序管道、自定义循环、临时并行 | 固定图、扇出/扇入、类型验证的消息路由 |
| 并行 | `asyncio.gather` | 并行边组与超步执行 |
| 可观测性 | 每步事件 | 每执行器事件 |
| HITL | `ctx.request_info()` | `RequestInfoExecutor` |
| 检查点 | 每步结果缓存 | 超步边界检查点 |
| 代理包装 | `FunctionalWorkflow.as_agent()` | `Workflow.as_agent()` |

选择建议：

1. 流程稳定、需要可视化与类型安全 → 图。
2. 流程含复杂循环、动态分支、Python 原生并发 → 函数式（接受实验性风险）。
3. 需要与 .NET/Go 对齐 → 图（三语言都支持）。

## 四个运行时原语

图模型的骨架只有四个概念（F-075）：

1. **执行器（Executor）**：接收输入、执行工作、发出输出。
2. **边（Edge）**：在执行器之间路由值。
3. **事件（Event）**：暴露工作流生命周期与执行活动。
4. **状态管理（State）**：持久化与运行级状态。

一个最小 .NET 工作流（F-073 的示例结构）：

```csharp
Func<string, string> uppercaseFunc = s => s.ToUpperInvariant();
var uppercase = uppercaseFunc.BindAsExecutor("UppercaseExecutor");

WorkflowBuilder builder = new(uppercase);
builder.AddEdge(uppercase, reverse).WithOutputFrom(reverse);
var workflow = builder.Build();
```

执行器可以是纯函数、类、代理，或子工作流（F-076）。代理执行器把代理接入图；子工作流把一张图封装成另一张图的执行器。

## 检查点：在超级步边界保存进度

检查点在超级步（superstep）边界创建（F-078）。这个设计选择决定了恢复语义：恢复时回到最近的超级步边界，而不是任意指令位置。

检查点能力包括：

1. 捕获检查点：配置检查点存储，构建启用检查点的工作流，运行后从存储访问检查点。
2. 从检查点恢复：指定第 N 个检查点恢复。
3. 解除冻结：不需要为恢复单独启用检查点。
4. 保存执行器状态：执行器可持久化自己的状态。
5. 安全：`Pickle` 序列化有代码执行风险；存储位置由你负责。

三条实践建议：

1. 不要把检查点存到不受信任的位置；`Pickle` 反序列化等于执行代码。
2. 检查点里可能含 PII 与工具输出；加密与保留策略要一起设计。
3. 恢复不是“重放”：外部副作用（发邮件、扣款）需要幂等键，否则会重复执行。

## 人工干预（HITL）：暂停，不是阻塞线程

HITL 通过请求/响应机制暂停并恢复执行（F-079）：

1. 工作流发出请求（函数式 `ctx.request_info()`，图 `RequestInfoExecutor`）。
2. 外部系统或人提供响应。
3. 工作流从暂停点继续。

关键语义：**多次 `run` 调用之间状态不隔离**，状态会保留（F-079）。这意味着 HITL 不是“重新开始”，而是“带着状态继续”。如果你的应用把每次请求当成独立运行，会丢失暂停点。

HITL 与检查点可以结合：在等待人工输入前创建检查点，恢复时从检查点继续（F-079）。

编排层也支持 HITL：代理可使用需审批的工具，在执行前暂停工作流供人工评审（F-081）。

## 五种编排模式

官方内置五种多代理编排（F-080）：

| 模式 | 机制 | 适合 |
|------|------|------|
| **顺序（Sequential）** | 代理按定义顺序逐个执行 | 流水线：研究 → 起草 → 审校 |
| **并发（Concurrent）** | 代理并行执行 | 多视角评估、并行检索 |
| **移交（Handoff）** | 代理根据上下文互相移交控制权 | 分诊 → 专家；需要追问时转交 |
| **群组聊天（Group Chat）** | 代理在共享对话中协作 | 头脑风暴、多角色讨论 |
| **Magentic** | 管理代理动态协调特定代理 | 复杂任务，需要动态选人 |

### 移交（Handoff）为什么重要

博文对 Handoff 的解释很到位（F-109）：多代理系统常从“路由器转发给专家”开始，但第一次遇到“专家需要追问”“需要同伴的上下文”“中途发现请求不属于自己”时就会断。Handoff 让代理在对话中移交控制权，而不是一次性路由。

实现上，开发者声明代理与有向边，框架为每个代理注入移交工具；拓扑与护栏由开发者掌握，路由决策由代理掌握（F-109）。.NET 用 `AgentWorkflowBuilder.CreateHandoffBuilderWith(...)`，Python 用 `HandoffBuilder(...)`（F-110）。

设计含义：**护栏在边上，判断在代理里**。你可以限制“计费只能转技术、技术不能转计费”，但不能硬编码“什么情况下转”——那由代理根据对话决定。

### Magentic 与群组聊天的区别

群组聊天是“多代理在一个共享对话里轮流发言”，适合开放式讨论；Magentic 是“管理代理动态选择下一个发言者/执行者”，适合任务分解与动态编排。前者偏协作，后者偏指挥。

## 工作流作为代理

工作流可以通过标准代理接口暴露（F-082）：

1. .NET：`AsAIAgent()`。
2. Python：`.as_agent()`。
3. Go：`agentworkflow.NewAgent(...)`。

这让“把一条确定性流程当成一个代理”成为可能：外层代理可以把工作流当工具调用，工作流内部又可以调用代理。组合的边界由你设计，但要避免无限递归。

## 声明性工作流

声明性工作流允许通过配置定义受支持的工作流（F-084）。适合标准化流程（审批、工单、内容审核），不适合需要复杂代码逻辑的场景。声明式的代价是表达力受限，收益是可视化、可审计、非开发者也能改。

## 可观测性与可视化

工作流可导出范围、指标、事件与传递状态；可视化可呈现与导出拓扑（F-083）。这两项在排障时比日志更有用：拓扑告诉你“应该走哪”，事件告诉你“实际走了哪”。

## 选型速查

| 需求 | 选择 |
|------|------|
| 固定流水线 | 顺序编排 / 图 |
| 多视角并行 | 并发编排 / 并行边 |
| 分诊 + 专家 + 追问 | Handoff |
| 开放式多角色讨论 | 群组聊天 |
| 动态任务分解 | Magentic |
| 需要暂停等人 | HITL + 检查点 |
| 需要跨进程恢复 | 检查点 + Durable Extension |

## 示例

可演练版本见 [工作流与检查点](../examples/03-workflow-checkpoint.md)。

## 已知边界

1. 函数式工作流 API 在 Python 中是实验性的，API 可能变化。
2. 检查点的序列化安全责任在应用侧；本文不提供加密实现。
3. 编排模式的内部调度细节（轮次、终止条件）需查各模式专页。
4. HITL 的“状态保留”意味着应用要设计好会话与运行的对应关系，否则会串状态。
