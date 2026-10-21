---
type: Reference
title: "VibeKnow CLI 退出码契约全表"
description: "0/1/2/3/4/5/6/7/8 八档退出码的语义边界、失败类型常量、error.detail 字段与阻塞式/单次读取式命令的分界规则"
tags: [vibeknow, cli, 退出码, 契约, agent]
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
    title: "VibeKnow CLI 仓库自带 AGENTS.md（退出码与授权门契约）"
---

# VibeKnow CLI 退出码契约全表

本文是 VibeKnow CLI 退出码的完整登记表。信源为 tag `v0.9.2` @ `93a26eca`。

## 八档退出码

| 退出码 | 命名常量 | 语义 | 处置动作 |
|---|---|---|---|
| 0 | `ExitOK` | 成功 | 读取 stdout 结果 |
| 1 | `ExitAPI` | 通用 API 失败（兜底类） | 看 `error.detail` |
| 2 | `ExitValidation` | 参数或旗标校验未过 | 改命令行；未知旗标会提示最接近的真实旗标名 |
| 3 | `ExitAuth` | 令牌缺失 / 无效 / 过期 | 重新登录后重试 |
| 4 | `ExitNetwork` | DNS / 连接 / 超时；亦覆盖后端可重试类码 | 等候后重试同一命令 |
| 5 | `ExitInternal` | 不应出现的缺陷；亦覆盖 `insufficient_credits` | `insufficient_credits` 时停止重试 |
| 6 | 无命名常量（`WithCode(6)`） | 未达终态 | 读 `error.detail.delivery` 与 `resend_safe` 后再决定 |
| 7 | 无命名常量（`WithCode(7)`） | 部分成功（预览就绪、导出未就绪） | 读 `next_actions` |
| 8 | `ExitBlocked` | 需用户决策的付费动作被阻断 | 展示条款并回传 `action_id` |

退出码 0~5 的常量集中在 `internal/clerr/clerr.go:25-30`；退出码 8 定义于 `internal/cmdutil/gate.go:28`；退出码 6 与 7 以 `WithCode(n)` 形式内联。

### 后端码到退出码的映射

| 后端码 | 退出码 | 依据 |
|---|---|---|
| `rate_limited` | 4 | `AGENTS.md:73-75` |
| `internal_error` | 4 | `AGENTS.md:73-75` |
| `concurrent_work_limit` | 4 | `AGENTS.md:73-75` |
| `work_edit_busy` | 4 | `AGENTS.md:73-75` |
| `insufficient_credits` | 5 | `AGENTS.md:76` |
| `session_expired` | 3 | `internal/httpclient/errors.go` 错误对象文案 |

## 失败类型常量

`internal/clerr` 定义 5 个失败类型字符串（`internal/clerr/clerr.go:15-19`）：

| 类型 | 构造函数 | 退出码 |
|---|---|---|
| `validation` | `clerr.Validation(msg)` | 2 |
| `auth` | `clerr.Auth(msg)` | 3 |
| `network` | `clerr.Network(msg)` | 4 |
| `api` | `clerr.New(msg)` | 1 |
| `internal` | `clerr.Internal(msg)` | 5 |

`clerr.ExitCodeFor(err)` 依据错误类型取退出码；`clerr.Classifier` 是可替换的分类函数变量，由 `cmd/exitcode.go` 注册。

## 命令行层面的收敛

任何命令行层面的问题——未知命令、未知或拼错的旗标、缺失必填旗标、多余的位置参数、非法枚举值——一律退出码 2。

`cmd/exitcode.go` 的 `rootCmd.SetFlagErrorFunc` 捕获旗标解析失败，转为 `clerr.Validation`，并按 Levenshtein 距离给出最接近的真实旗标名。另有 `usagePrefixes` 收录 9 条不走 `SetFlagErrorFunc` 的 cobra 命令行解析失败前缀（`cmd/exitcode.go:104-127`）：

1. `unknown command`
2. `unknown flag`
3. `unknown shorthand flag`
4. `flag needs an argument`
5. `invalid argument`
6. `required flag(s)`
7. `accepts `
8. `requires at least`
9. `requires at most`

命中即转退出码 2。

## 退出码 6 的三态投递判定

退出码 6 覆盖三种成因（`AGENTS.md:59-63`）：

| `error.detail.reason` | 成因 |
|---|---|
| `wait_budget_expired` | `--for` 预算耗尽，运行本身健康 |
| 缺省 | 流在无终止事件时结束 |
| 缺省 | 任务被暂停，可用 `vk video resume` 恢复 |

退出码 6 的详情载荷含 `delivery` 与 `resend_safe` 两个字段：

| `delivery` | `resend_safe` | 判据 |
|---|---|---|
| `submitted` | false | 后端已有该 session 的 work 行 |
| `not_submitted` | true | 后端返回 not_found（work 行在 init 时创建，缺席即无计费发生） |
| `indeterminate` | false | 探针本身失败 |

`resend_safe` 仅在 `delivery == not_submitted` 时为 true（`internal/cmdutil/unknown.go` 的 `ResendSafe()` 判定式）。`indeterminate` 保守地给出 `resend_safe: false`——等待一次已丢失的运行只损失时间，重发一次未丢失的运行损失用户的钱。

## 阻塞式命令与单次读取式命令的分界

| 类别 | 命令 | 退出码来源 |
|---|---|---|
| 阻塞至终态 | `vk create`、`vk video wait`、`vk video export`（无 `--async`） | 终态状态 |
| 单次读取 | `vk video status`、`vk video export-status` | 恒为 0，状态写在载荷里 |

同一次失败的导出，在 `vk video export` 上是退出码 7，在 `vk video export-status` 上是退出码 0 + `export.status="failed"`。两者都不会以退出码 0 且无可判定信息的方式结束。

## 退出码使用点分布

脚本统计（口径：以 `WithCode(n)` 调用点与 `const Exit*` 定义点为准）：

| 退出码 | 使用点数 | 位置 |
|---|---|---|
| 0 | 1 | `internal/clerr/clerr.go`（常量定义） |
| 1 | 2 | `cmd/video/edit.go`、`internal/clerr/clerr.go`（常量定义） |
| 2 | 1 | `internal/clerr/clerr.go`（常量定义） |
| 3 | 1 | `internal/clerr/clerr.go`（常量定义） |
| 4 | 3 | `cmd/create.go`、`cmd/video/pause.go`、`internal/clerr/clerr.go`（常量定义） |
| 5 | 5 | `cmd/video/pause.go`、`cmd/video/script.go`、`cmd/video/set.go`、`internal/clerr/clerr.go`（常量定义） |
| 6 | 9 | `cmd/create.go`、`cmd/video/edit.go`、`cmd/video/progress.go`、`cmd/video/script.go`、`cmd/video/set.go`、`cmd/video/wait.go`、`internal/cmdutil/unknown.go` |
| 7 | 1 | `cmd/video/export.go` |
| 8 | 常量单点 | `internal/cmdutil/gate.go:28` |

## 相关概念

- [/concepts/01-exit-code-contract.md](/concepts/01-exit-code-contract.md) —— 退出码契约的读者视角解读
- [/concepts/02-paid-action-gate.md](/concepts/02-paid-action-gate.md) —— 退出码 8 的授权门
- [/examples/01-agent-safe-automation.md](/examples/01-agent-safe-automation.md) —— 按退出码分流的自动化范式
