---
type: Example
title: "OpenCode 2.0.32 Session Prompt 源码追踪"
description: "按固定源码顺序追踪一条 session prompt 从 handler 到执行协调和事件投影的路径"
tags: [opencode, session, prompt, source-trace, example, 2.0.32]
generated: { by: "reference_agent/trae-cn", at: 2026-10-20T12:01:30+08:00 }
verified: { by: "process:seven-concepts-e", at: 2026-10-20T12:01:30+08:00 }
status: draft
stale_after: 2027-04-20
sources:
  - id: opencode-source-map-2.0.32
    resource: /references/source-code-map-2.0.32.md
    title: OpenCode 2.0.32 固定源码地图
---

# OpenCode 2.0.32 Session Prompt 源码追踪

本示例带读者沿固定快照中的一条 `session.prompt` 路径，从 Server handler 一直追到 Core 的执行协调、模型 step 与事件投影。它是源码阅读路线，不是可运行程序；其中的模块名和行为需按 commit `6ec56821d63100fe5bda45b759364f561c56b359` 核对。（F-090、F-093～F-103、F-114）

## 追踪前准备

先阅读[会话执行生命周期](/concepts/06-session-execution-lifecycle.md)，再打开[固定源码地图](/references/source-code-map-2.0.32.md)。源码地图列出了本示例所需的 Protocol、Server handler、Core Session、coordinator、runner、SQL 和 projector 文件；同一文件名应始终对应登记的固定 commit，避免无意间读到本地其他版本。

## 追踪步骤

| 顺序 | 查看位置 | 源码中可确认的动作 | 事实 |
|---|---|---|---|
| 1. 契约入口 | Protocol session group | 可定位 `session.prompt` endpoint 的声明；本示例不尝试枚举整个 group 的 endpoint 数量。 | F-102、F-111 |
| 2. Server 转交 | `packages/server/src/handlers/session.ts` | handler 将 session ID、消息 ID、文本、文件、agents、skills、metadata、delivery 与 resume 等字段交给 `session.prompt`。 | F-114 |
| 3. Core 接纳 | `packages/core/src/session.ts` 与对应 session 实现 | service 转发到目标 session；prompt 实现准备输入并调用 `admission.admit`。 | F-114 |
| 4. 条件唤醒 | 同一 prompt 实现 | 当 `resume !== false` 时调用 `execution.wake(sessionID)`；`resume: false` 不触发此唤醒分支。 | F-114 |
| 5. 执行协调 | `run-coordinator.ts`、`execution.ts` | coordinator 按 session key 管理 drain；活动执行期间到来的 wake 会记录为待处理唤醒。Execution 与 SessionStore 协同管理开始和终态状态。 | F-093～F-095 |
| 6. 模型 step | `runner/llm.ts`、`runner/step.ts` | runner 准备 context、处理 inbox，再调用 `runStep`；step 调用 `llm.stream`。 | F-096、F-097 |
| 7. 本地工具分支 | `runner/step.ts`、工具 runtime/MCP 路径 | 对非 provider 执行的 `tool-call`，runner 创建本地工具 fiber；MCP 工具执行路径调用 Permission 断言。 | F-090、F-091、F-097 |
| 8. 状态投影 | `sql.ts`、`projector.ts` | Session SQL 声明相关表；projector 将 Session 事件交给数据库处理函数。 | F-098、F-099 |

## 两种 resume 路径

比较调用时 `resume` 的取值，可以得到两个不同的源码分支：

- **省略或不为 `false`**：prompt 进入输入准备和 admission 后，代码调用 `execution.wake(sessionID)`。后续是否立即运行、是否 join 现有 drain 或登记待处理唤醒，由 coordinator 所处状态决定。（F-093、F-094、F-114）
- **`resume: false`**：仍走 prompt 的输入准备和 admission，但跳过这次 `execution.wake(sessionID)` 调用。不要把“这次调用未唤醒执行”改写为“该输入永不执行”；后续处理不在本分支事实中作推断。（F-114）

这一区分解释了为什么 API 请求完成、输入已接纳、执行开始和模型 step 完成不能互相代替。要确认某个阶段是否发生，应沿表中的对应边界检查，而不是仅从调用方观察一次 HTTP 返回。

## 读到工具调用时

当 `llm.stream` 产生 `tool-call` 事件，继续确认执行类型。事实清单记录的是：非 provider 执行的工具调用进入本地工具 fiber，runner 在流结束后等待这些 fiber；MCP 执行路径还会调用 Permission 断言。（F-091、F-097）

因此，追踪时应把三个问题分开记录：模型流是否产生工具调用事件、OpenCode 是否在本地启动工具执行、执行结果及事件是否进入状态投影。本示例不提供可运行的 API 调用代码，也不从事件名称推导未检查的错误恢复语义。

## 复核清单

完成一次源码追踪后，可用以下问题检查自己的路径是否越界：

1. 是否从 Protocol/handler 事实区分了契约声明与实际转交？
2. 是否明确指出 `admission.admit` 与条件 `execution.wake` 是两个步骤？
3. 是否检查了 coordinator 的活动 key 与待处理 wake，而非假设每次 wake 都启动新 runner？
4. 是否区分 provider 执行与本地 tool fiber？
5. 是否把持久化描述限定在已检查的 SQL 表与 projector 事件上？
6. 是否始终使用固定 commit，并对未覆盖分支保留“不作推断”的边界？

完整的事实路径和固定文件链接见[OpenCode 2.0.32 事实清单](/spec/facts-2.0.32.md)与[源码地图](/references/source-code-map-2.0.32.md)。

## 相关概念

- [会话执行生命周期](/concepts/06-session-execution-lifecycle.md)
- [模型、工具与扩展机制](/concepts/07-model-tool-extensibility.md)
- [Protocol、Server、Client 与 SDK 边界](/concepts/08-protocol-server-client-sdk.md)
