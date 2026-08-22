---
type: spec
title: "DeepSeek Reasonix 架构洞察"
description: "对 DeepSeek Reasonix 源码的 4 个核心架构洞察，覆盖插件化内核、推理内容回传、会话级并发调度与多前置端共享运行时。"
tags: [spec, insight, reasonix, architecture]
generated: { by: "okf-wiki-bot", at: "2026-08-23T12:00:00+08:00" }
verified: { by: "process:grep-verification", at: "2026-08-23T12:00:00+08:00" }
status: draft
stale_after: 2027-08-23
---

# DeepSeek Reasonix 架构洞察

## 洞察 1：核心是"接口 + 注册表"，模型与工具全部按名注入

**陈述**：Reasonix 的内核不含任何具体的模型实现或工具实现。模型通过 `provider.Register`（按 kind 字符串）在 `init()` 中自注册，工具通过 `tool.Registry` 按名解析；CLI 入口用空白导入把编译期内置提供方连接到注册表。

**证据**：F-004（cmd/reasonix/main.go 空白导入 anthropic/openai/responses/tool/builtin）、F-009（`Provider` 接口只有 `Name()` 与 `Stream()`）、F-011/F-012（`Register` 按 kind 注册、`New` 按 kind 实例化）、F-003（包注释"config- and plugin-driven"）。

**反常识**：一个"DeepSeek 编码 Agent"并不硬编码 DeepSeek 模型——`main.go` 空白导入的三个提供方是 anthropic、openai、responses，DeepSeek 只是 OpenAi-compatible 通道下的一个实例名（`provider.Message` 内还保留了 `ReasoningContent`/`ReasoningID`/`ReasoningSignature` 等为多厂商推理回传设计的字段，见 F-014/F-019）。

**行动**：阅读本项目时，先读 `internal/provider` 与 `internal/tool` 的接口与注册表，再按"一个 kind 一个实现包"去定位具体模型/工具，而不是在 agent 循环里找 `switch model`。

## 洞察 2：Agent 是"无状态装配 + 会话负载"的组合，并发边界在会话级调度器上

**陈述**：`Agent` 结构体本身不持有模型/工具引用，只持有会话（`sess sessionRuntime`）、任务（`task taskRuntime`）与回合（`turn turnRuntime`）三段运行时状态；真正的并发串行化发生在 `SubagentScheduler`——它用 `maxTotal`/`maxWriters` 两个上限，把 task、fleet、parallel_tasks、profile skills 与嵌套子代理统一收口到一个会话级信号量。

**证据**：F-023/F-029/F-030（Agent 的 sess/task/turn 三段状态）、F-047（`SubagentScheduler.maxTotal/maxWriters/parentClaims`）、F-046（`AcquireRequest.Writer/WritePaths/Nested`）、F-048（`NewSubagentScheduler(maxTotal, maxWriters)`）。

**反常识**：写权限并发控制不是靠仓库文件锁，而是靠会话内"写路径声明"（WritePathSet）——父代理持有的声明会阻塞子代理重叠声明却"不占用子代理槽位"（见 F-047 的 `parentClaims` 注释意图），嵌套请求在容量耗尽时"立即失败"而非排队，以避免父子槽位死锁。

**行动**：排查"子代理卡死/并发异常"时，先看 `internal/agent/scheduler.go` 的 `AcquireWithID` 与 `parentClaims` 路径，理解槽位与写声明是两套正交的约束。

## 洞察 3：推理内容（reasoning）作为一等公民在会话与线路上显式回传

**陈述**：DeepSeek 的"思考模式"要求 `reasoning_content` 在多轮请求间原样回传，Reasonix 不把推理文本当作普通展示内容，而是在 `provider.Message`/`provider.Chunk` 里显式建模，并配有两个能力探测接口（`ToolCallReasoningPolicy`/`ReasoningRoundTripPolicy`）来区分"工具调用回合是否重放推理"与"所有助手消息是否必须回传推理"。

**证据**：F-014（`Message.ReasoningContent`）、F-019（`Chunk.Signature/ReasoningID/ReasoningStatus`）、F-022（`ToolCallReasoningPolicy`）、F-020（按 reasoning 启停分档的输出预算常量）。

**反常识**：看似"拼接字符串发送给模型"的简单动作，实际上被拆成精细的回传契约——签名（`ReasoningSignature`）需要在下一次输入中随 `ReasoningContent` 一起回放，而带本地展示翻译的复制文本"不得回传到 API"（provider.go 对 `ToolCallReasoningPolicy` 的注释）。误把展示副本回传会破坏多厂商的思考模式。

**行动**：写 Provider 适配器或调会话历史时，遵循 `Message.ReasoningContent`（存储原文）与展示译文的分离规则，避免推理文本在回传队列里被二次翻译。

## 洞察 4：CLI / 桌面 / ACP / Bot 四个前置端共享同一条装配链

**陈述**：reasonix 不是"一个 CLI + 几个旁支"，而是 `internal/boot` 提供统一的 `build(ctx, Options) (*BuildResult, error)` 装配函数，CLI 入口（`cli.RunWithBuildInfo` → `runAgent`/`chatREPL`）、桌面 Wails 应用（`desktop.NewApp`）与 Bot 网关（`BotGateway.buildController`）都经由它派生 `*control.Controller`；ACP 层则作为覆盖在 `control.SessionAPI` 之上的 stdio JSON-RPC 适配器，把事件流映射为 `session/update` 通知。

**证据**：F-142（`boot.build`）、F-100（`BotGateway.buildController func(...) (*control.Controller, error)`）、F-112/F-113/F-114（`RunWithBuildInfo`/`runAgent`/`chatREPL`）、F-146（`desktop.NewApp`）、F-088/F-089（ACP `AgentInfo`/`Serve`）。

**反常识**：Bot 网关刻意只依赖 `control.Lifecycle`/`control.TurnControl`/`control.Approvals` 三个子端口（F-100 附近 `botController` 接口），而不是具体 `*control.Controller` 及其约 99 个方法——这使 bot 永远碰不到 goals、checkpoints、memory，从类型层面削减了权限面。

**行动**：新增前置端（如新聊天接入）时复用 `boot.build` 而非自己拼装 provider/tool；需要暴露给 ACP/Bot 的能力，先确认它在 `control` 包的哪个子端口接口里。

## 相关概念

- [/concepts/00-overview.md](/concepts/00-overview.md)
- [/concepts/01-agent-runtime.md](/concepts/01-agent-runtime.md)
- [/concepts/02-acp-protocol.md](/concepts/02-acp-protocol.md)
- [/concepts/03-bot-gateway.md](/concepts/03-bot-gateway.md)