---
type: Concept
title: "OpenCode 2.0.32 会话执行生命周期"
description: "沿 prompt handler、接纳、唤醒、协调器、runner 与事件投影追踪会话执行边界"
tags: [opencode, session, execution, llm, persistence, 2.0.32]
generated: { by: "reference_agent/trae-cn", at: 2026-10-20T12:01:30+08:00 }
verified: { by: "process:seven-concepts-e", at: 2026-10-20T12:01:30+08:00 }
status: draft
stale_after: 2027-04-20
sources:
  - id: opencode-source-map-2.0.32
    resource: /references/source-code-map-2.0.32.md
    title: OpenCode 2.0.32 固定源码地图
---

# OpenCode 2.0.32 会话执行生命周期

在 2.0.32 快照中，提交一条 prompt 与完成一次模型执行是不同阶段。读者可以沿着 `Server handler → Core Session service → admission → wake → session-key coordinator → runner → event projector` 追踪；每一段解决的问题不同，不应把一次 API 请求的结束直接等同于模型 turn 的结束。（F-093～F-100、F-114）

本篇聚焦源码可证实的执行路径，不覆盖所有会话 API、所有消息状态或旧版 V2 会话语义。此前的 [会话与工具章节](/concepts/03-session-tools.md)属于 `1.18.21` 历史快照；它不应被当作本篇版本的实现依据。

## 从 handler 到接纳

Protocol 的 session group 声明 `session.prompt` 等 endpoint；Server 的 `session.prompt` handler 将 session ID、消息 ID、文本、文件、agents、skills、metadata、delivery 和 resume 等字段交给 Core 的 `session.prompt`。Core Session service 再把调用转给对应 session 的 prompt 实现。（F-102、F-114）

prompt 实现准备输入并调用 `admission.admit`。默认情况下，当 `resume` 未设为 `false` 时，随后会调用 `execution.wake(sessionID)`；传入 `resume: false` 时则不会走这次唤醒分支。这里应区分“输入已交给 admission”和“执行已被唤醒”，不要把两者混为一个同步动作。（F-114）

## 按 session key 协调执行

`SessionRunCoordinator` 按 key 管理 drain 状态。协调器提供 join、wake、interrupt 与 `awaitIdle` 等操作；若某 key 正在执行，新的 wake 会登记待处理唤醒，当前 drain 结束前后由协调器继续处理待办。（F-093、F-094）

执行状态由 `SessionExecution` 配合 `SessionStore` 管理。源码把 `Execution.Started` 事件发布与 `SessionStore.claim(sessionID)` 放在同一个 commit 回调；成功或失败终态发布时调用 release。shutdown 中断的发布路径没有携带 release 回调，其他中断路径携带 release 回调。该差异是具体的资源状态处理，不应简化成“任何终态都以相同方式释放”。（F-095）

## Runner 与模型 step

LLM runner 的 drain 循环先准备 context、提升可处理的 inbox 项，再调用 `runStep` 并递增 step 序号。单个 step 将准备好的 request 和 options 传给 `llm.stream`。当流中出现非 provider 执行的 `tool-call` 事件时，runner 创建本地工具执行 fiber，并在流结束后等待这些工具 fiber。（F-096、F-097）

因此，模型输出中的工具调用意图不等于工具副作用已经发生。需要继续确认该调用是否由 provider 执行，还是由 OpenCode 本地 runtime 执行；本篇会话路径描述后者的调度边界，工具输入输出和权限细节见[模型、工具与扩展机制](/concepts/07-model-tool-extensibility.md)。

## 事件与持久化投影

固定快照的 Session SQL 声明了 `session_v2`、`session_message`、`session_pending`、`session_inbox`、`instruction_entry`、`instruction_blob` 与 `instruction_state` 等表。`projector.ts` 通过 `bus.project` 将 Session 事件交给数据库处理函数，其中包含执行成功、失败、中断、step 和 tool 等事件。（F-098、F-099）

这为排查提供了另一条定位轴：若问题发生在输入接纳，检查 handler 与 admission；若请求已唤醒但没有执行，检查 coordinator/execution；若模型 step 与工具状态不一致，检查 runner/tool event；若状态读取与事件不一致，再沿 projector 和 SQL 投影追踪。该定位建议是基于上述分层的排查路径，不表示本篇已检查所有故障处理分支。

## 学习边界

这里描述的是 commit `6ec56821d63100fe5bda45b759364f561c56b359` 中检查过的 prompt 主链。它没有枚举全部 endpoint，也没有证明所有存储状态、并发交错和 provider 适配器都已穷尽。若版本标签与源码不一致，以[固定源码地图](/references/source-code-map-2.0.32.md)记录的 commit 为准；关键事实编号汇总于[事实清单](/spec/facts-2.0.32.md)。

## 相关概念

- [OpenCode Monorepo 包地图](/concepts/05-monorepo-package-map.md)
- [模型、工具与扩展机制](/concepts/07-model-tool-extensibility.md)
- [Protocol、Server、Client 与 SDK 边界](/concepts/08-protocol-server-client-sdk.md)
- [会话 Prompt 源码追踪示例](/examples/02-session-prompt-trace.md)
