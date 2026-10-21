---
type: Concept
title: "运行账本、目标解析与异步语义"
description: "jobs.jsonl 账本的六个状态与 best-effort 写入、三级目标解析顺序、--async 的 60 秒脱离上限、导出幂等与 exit 6/7 的触发点"
tags: [vibeknow, cli, 账本, 异步, session, 目标解析]
generated:
  by: trae-seven-concepts
  at: "2026-10-21T00:00:00+08:00"
verified:
  by: process:seven-concepts-v
  at: "2026-10-21T00:00:00+08:00"
status: stable
stale_after: "2027-04-21"
sources:
  - id: vksrc
    resource: https://github.com/vibeknow/cli
    title: "VibeKnow CLI 源码仓库 v0.9.2 @ 93a26eca"
  - id: vkagents
    resource: https://github.com/vibeknow/cli/blob/v0.9.2/AGENTS.md
    title: "VibeKnow CLI 仓库自带 AGENTS.md（运行账本契约）"
---

# 运行账本、目标解析与异步语义

> **事实编号**：F-043~F-053（完整清单见 [/references/source-facts.md](/references/source-facts.md)）


一次视频生成会跑很久。上下文被裁剪、终端被关、进程重启之后，怎么找回那条还在跑、还在计费的运行？这套机制由本地账本 + 三级目标解析 + 异步脱离共同承担。

## 每次运行的身份是一对 ID

每个运行由 `(task_id, session_id)` 标识。`vk create` 会把这一对写进 `<config-dir>/jobs.jsonl`，让丢失上下文的调用方仍能触达那个活着的运行。

## 账本：jobs.jsonl

| 属性 | 取值 |
|---|---|
| 路径 | `<config-dir>/jobs.jsonl` |
| 写入方式 | append-only JSONL，单次 `O_APPEND` 追加 |
| 压缩阈值 | `compactThreshold = 2000` 行，超过时改写文件 |
| 写入失败 | 在 stderr 告警，**不使运行失败** |

单次 `O_APPEND` 写入不需要加锁，因此并发的多个 `vk create` 不会互相破坏行。

### 六个状态

| 状态 | 含义 |
|---|---|
| `submitted` | init 已返回、运行已派发，结果未观测 |
| `running` | 至少观测到一个进度事件 |
| `succeeded` | 终态成功 |
| `failed` | 终态失败 |
| `unknown` | 流在终态事件前断开 |
| `paused` | 后端报告运行被暂停，可恢复 |

### 账本是本地且建议性的

两条纪律值得单独记住：

1. **条目缺失只表示「此处未记录」，不表示「运行不存在」**。权威状态在后端。
2. **写入是尽力而为的**。写失败只告警。

因此每个 `vk video` 子命令都仍然接受显式的 `--session-id`——那是绕开本地账本的可靠路径。

### `vk jobs` 三个子命令

```bash
vk jobs list [--active] [--output json]   # 已记录的运行，最新在前
vk jobs get [task_id]                     # 单个运行（默认取最近一个）
vk jobs prune --terminal | --older-than 30d | --all
```

裸的 `vk jobs prune` 被拒绝——它会丢掉指向某个活着的运行的指针。

## 三级目标解析

`cmd/video/helpers.go` 的 `resolveTarget` 按固定顺序找目标：

| 顺序 | 来源 | 说明 |
|---|---|---|
| 1 | 显式 `--session-id` | 永远优先 |
| 2 | 本地账本 | `jobs.Get(taskID)` 或 `jobs.Latest()` |
| 3 | 后端最近 work | `ListWorks(ctx, 1, 1)` 取最新一条的 session |

**只给 task_id 而不给 session 时不做远程解析**——后端的 work 列表按 work_id / session_id 键控，拿不到 session 就无法反查，命令返回退出码 2 并提示 `vk video list`。

## 异步：脱离而非跳过

`--async` **不跳过启动流水线**。它仍然会走完整的启动路径（上传、建 run、派发），只是不再等待终态。

```bash
vibeknow create --text "..." --async --output json
```

成功输出：

```json
{
  "task_id": 42,
  "session_id": "...",
  "status": "running",
  "next_actions": [{ "command": "vibeknow video wait 42 --session-id ..." }]
}
```

ndjson 模式下额外带 `"event": "task.submitted"`。

### 60 秒脱离上限

`asyncDetachTimeout = 60 * time.Second` 是等待后端首个流事件的上限。触顶不致命——运行请求已经发出去了——但会被报告，因为这个运行从未被观测到启动。

这个常量的注释解释得很细：设得足够长，普通节点间隙不会触发；设得足够短，手绘风格那段以分钟计的静默中段能不止一次地给出「还在生成」的宽慰。

（`streamStallNotice = 60 * time.Second` 是另一条常量：进度流静默多久后人类路径打印一次安慰话。）

### `--async` 与 `--export` 互斥

`--export` 跑在预览快照之后，而 `--async` 在运行确认后就脱离了，到不了导出那一步。两者组合过去会静默丢掉 `--export` 却仍退出 0，调用方拿到预览却无从察觉——现在直接返回退出码 2。

`vk video export` 也有 `--async`，另有别名 `--no-wait` 指向它。

## 导出：幂等、部分成功与未知态

| 场景 | 结果 |
|---|---|
| 同一 (user, session) 重复导出 | 后端幂等，返回同一 task_id |
| 同步轮询被取消或超时 | 退出码 6 |
| 导出失败但预览已在 | 退出码 7（`WithCode(7)`），提示取 `next_actions[0].Command` |
| 运行状态无法确认 | 退出码 6 + `error.detail.delivery` 三态 |

退出码 7 的语义是「部分成功」：预览页和分享链接仍然可用，MP4 不在。重新 `vk video export` 一次不会重复计费，因为后端对 (user, session) 幂等。

## 实践建议

1. **长任务一律显式传 `--session-id`**，把身份握在自己手里，不依赖账本。
2. **异步之后用 `vk video wait` 收口**，或轮询 `vk video status`。
3. **账本缺条目不等于运行不存在**——先 `vk jobs list`，再 `vk video list`。
4. **退出码 6 先查状态再决定是否重跑**，见 [01-exit-code-contract.md](01-exit-code-contract.md)。

## 相关概念

- [/concepts/01-exit-code-contract.md](/concepts/01-exit-code-contract.md) —— 退出码 6 的三态判定
- [/concepts/02-paid-action-gate.md](/concepts/02-paid-action-gate.md) —— 导出时的授权门
- [/concepts/05-create-parameter-space.md](/concepts/05-create-parameter-space.md) —— `--async` 的互斥校验
- [/examples/01-agent-safe-automation.md](/examples/01-agent-safe-automation.md) —— 异步收口的脚本范式
