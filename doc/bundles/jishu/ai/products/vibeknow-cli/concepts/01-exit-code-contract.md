---
type: Concept
title: "退出码契约：把结果编码进 8 档状态"
description: "VibeKnow CLI 用 0/1/2/3/4/5/6/7/8 八档退出码表达可判定的失败语义，退出码 6 的三态投递判定与阻塞式/单次读取式命令的分界规则"
tags: [vibeknow, cli, 退出码, agent, 契约]
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
  - id: exitcodes
    resource: /references/exit-code-contract.md
    title: "VibeKnow CLI 退出码契约全表"
---

# 退出码契约：把结果编码进 8 档状态

> **事实编号**：F-014~F-023、F-037~F-039（完整清单见 [/references/source-facts.md](/references/source-facts.md)）


VibeKnow CLI 的退出码不是「成功 / 失败」两分，而是八档各自对应一种可判定的语义。设计目标很直接：让一个小模型或一段 shell 脚本不必解析任何散文就能分流。

## 八档速查

| 退出码 | 含义 | 你该做什么 |
|---|---|---|
| 0 | 成功 | 读 stdout 的结果 |
| 1 | 通用 API 失败 | 读 `error.detail` |
| 2 | 命令行有问题 | 改命令行；拼错的旗标会提示最接近的真实旗标名 |
| 3 | 令牌缺失 / 无效 / 过期 | 重新登录后重试同一命令 |
| 4 | 网络问题或后端可重试状态 | 等候后重试同一命令 |
| 5 | 内部缺陷，或积分不足 | 积分不足时停止重试 |
| 6 | 未达终态 | 读 `error.detail.delivery` 与 `resend_safe` 再决定 |
| 7 | 部分成功 | 预览就绪但 MP4 未就绪，读 `next_actions` |
| 8 | 付费动作需要用户决策 | 展示条款，把 `action_id` 原样带回 |

退出码 0~5 的常量集中在 `internal/clerr/clerr.go:25-30`；退出码 8 定义在 `internal/cmdutil/gate.go:28`，名为 `ExitBlocked`；退出码 6 与 7 没有命名常量，以 `WithCode(6)` / `WithCode(7)` 的形式内联在调用点。

## 命令行层面的收敛

任何命令行层面的问题都归到退出码 2：未知命令、未知或拼错的旗标、缺失必填旗标、多余的位置参数、非法枚举值。

拼错的旗标不会只给一句「未知旗标」——`cmd/exitcode.go` 的 `SetFlagErrorFunc` 会按 Levenshtein 距离找出当前命令上最接近的真实旗标名，放进提示里。另有 9 条不走 `SetFlagErrorFunc` 的 cobra 解析失败前缀被单独登记，同样转退出码 2。

对写自动化的人来说，退出码 2 是「我写错了」，与其它各档区分得很干净：它永远不需要重试，只需要改。

## 退出码 4 与 5：等一等还是别等了

退出码 4 同时覆盖两类情形：传输层问题（DNS / 连接 / 超时），以及后端明确表示「值得重试」的状态码——`rate_limited`、`internal_error`、`concurrent_work_limit`、`work_edit_busy`。这四类的共同点是同一条命令稍后重跑有意义。

退出码 5 覆盖 `insufficient_credits`——重试帮不上忙，钱不够就是钱不够。剩余情形归到 `internal` 类型（不应出现的缺陷）。

## 退出码 6：把「状态未知」拆成可操作的三态

这是全套退出码里信息量最大的一档。当一次运行的最终状态无法确认时，CLI 不报成功也不报失败，而是报 6，并在 `error.detail` 里给出两个字段：

| `delivery` | `resend_safe` | 判据 |
|---|---|---|
| `submitted` | false | 后端已有该 session 的 work 行 |
| `not_submitted` | true | 后端返回 not_found——work 行在 init 时创建，缺席即无计费发生 |
| `indeterminate` | false | 探针本身失败 |

`resend_safe` 只在 `not_submitted` 时为 true（判定式是 `u.Delivery == DeliveryNotSubmitted`）。

**为什么「不确定」对应「不要重发」**：源码注释写得很直白——等一次已经丢失的运行只损失时间，重发一次没丢失的运行损失用户的钱。于是 `indeterminate` 保守地给出 `resend_safe: false`。

退出码 6 还覆盖三种成因，可在 `error.detail.reason` 中区分：

| `reason` | 成因 | 处置 |
|---|---|---|
| `wait_budget_expired` | `--for` 预算耗尽，运行本身健康 | 加预算再等 |
| 缺省 | 流在无终止事件时结束 | 查 `delivery` 决定是否重发 |
| 缺省 | 任务被暂停 | `vk video resume` |

## 阻塞式与单次读取式的分界

同一件事，两种读法，退出码不同：

| 类别 | 命令 | 退出码来源 |
|---|---|---|
| 阻塞至终态 | `vk create`、`vk video wait`、`vk video export`（无 `--async`） | 终态状态 |
| 单次读取 | `vk video status`、`vk video export-status` | 恒为 0，状态写在载荷里 |

一次失败的导出，在 `vk video export` 上是退出码 7（部分成功：预览在、MP4 不在）；在 `vk video export-status` 上是退出码 0 加 `export.status="failed"`。

两者都不会以「退出码 0 但没有任何可判定信息」的方式结束——这是这套契约的底线。

## 失败类型与结构化详情

`internal/clerr` 定义 5 个失败类型字符串，与退出码一一对应：

| 类型 | 构造函数 | 退出码 |
|---|---|---|
| `validation` | `clerr.Validation(msg)` | 2 |
| `auth` | `clerr.Auth(msg)` | 3 |
| `network` | `clerr.Network(msg)` | 4 |
| `api` | `clerr.New(msg)` | 1 |
| `internal` | `clerr.Internal(msg)` | 5 |

`clerr.ExitCodeFor(err)` 按类型取码；`clerr.Classifier` 是可替换的分类函数变量，由 `cmd/exitcode.go` 注册。

要拿细粒度原因，开 `--output json`，读 `error.detail`（`delivery`、`resend_safe`、`reason`）与 `next_actions`（可执行的后续命令）。

## 实践建议

1. **分支只按退出码写**，不 grep stdout 文本。文本是人读的，码是机器读的。
2. **退出码 6 不要直接重跑**。先 `vk video status` 查一次，确认 `resend_safe` 再动。
3. **退出码 7 读 `next_actions`**，那里已经写好了该执行哪条命令。
4. **退出码 8 不是错误**，是「需要人来拍板」。处置见 [02-paid-action-gate.md](02-paid-action-gate.md)。

## 相关概念

- [/concepts/02-paid-action-gate.md](/concepts/02-paid-action-gate.md) —— 退出码 8 的授权门
- [/concepts/03-output-and-events.md](/concepts/03-output-and-events.md) —— 怎么把 `error.detail` 读出来
- [/examples/01-agent-safe-automation.md](/examples/01-agent-safe-automation.md) —— 按退出码分流的完整脚本范式
- [/references/exit-code-contract.md](/references/exit-code-contract.md) —— 退出码全表与使用点分布
