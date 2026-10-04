---
type: Example
title: "实时事件订阅自动化：NDJSON、jq 投影与 bus 自愈"
description: "用 event list/schema 发现事件，以批处理与常驻两种模式 consume 实时会议事件，解析 stderr ready 标记与退出码，处理 orphan/stale_owner 总线异常。"
tags: [tencent-meeting, tmeet, example, event, ndjson, jq, websocket, bus, automation, v1.0.18]
generated: { by: "reference_agent/trae-solo", at: "2026-10-03T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-10-03T00:00:00Z" }
status: stable
stale_after: 2027-04-03
sources:
  - id: command-reference
    resource: /references/command-reference.md
    title: 官方完整命令参考 docs/command.md
  - id: skill-manifest
    resource: /references/skill-manifest.md
    title: CLI-SKILL 清单与 CHANGELOG（v1.0.18）
---

# 实时事件订阅自动化（v1.0.18+）

> 场景：不再轮询「会开始了没」，改为订阅实时事件——会议开始时触发自动拉取参会名单/通知外部系统，会议结束时自动触发纪要归档。本示例演示安全的事件消费姿势。

## 0. 版本前提

event 组在 v1.0.18（2026-09-11）引入（F-009、F-079）。先确认版本：

```bash
tmeet --version    # 需要 ≥ v1.0.18
```

## 1. 发现可订阅事件（本地、免登录）

```bash
tmeet event list
# 输出内置注册表中全部 EventKey，按 domain, key 排序（F-083）
```

## 2. 查事件结构（订阅前必做）

```bash
tmeet event schema meeting.started
```

输出 `params_schema`、`resolved_output_schema` 与 `jq_root_path`（F-083）。**务必先看 schema**：`jq_root_path` 配错不会报错，而是静默丢弃事件（F-085）。例如 `meeting.started`/`meeting.end` 的根路径是 `.payload`，且 payload 恒为长度 1 的数组，jq 要先 `.[0]`。

## 3. 批处理模式（定时任务首选）

收满 20 条会议开始事件就退出，事件落盘到相对目录：

```bash
tmeet event consume meeting.started \
  --max-events 20 \
  --output-dir ./events/started \
  2>consume.err >events.ndjson
```

或运行 5 分钟后自动结束：

```bash
tmeet event consume meeting.started --timeout 5m
```

（F-080）stdout 只有 NDJSON 业务事件；stderr 是诊断流。退出码（F-081）：

- `0`：达到 limit/timeout 或正常收到信号；
- `1`：致命错误；
- `2`：仅 status/stop 的异常判定使用。

## 4. 常驻模式 + jq 投影

```bash
tmeet event consume meeting.started --jq '.[0].subject'
```

`--jq` 使用 gojq 语法在消费端投影，减少 Agent 上下文占用。因为 payload 是长度 1 的数组，取会议主题要写 `.[0].subject` 而非 `.subject`（F-085）。

也可按参数过滤：

```bash
tmeet event consume meeting.end --param meeting_code=412345678
```

常驻模式不读 stdin，下列后台化方式都不会导致它退出（F-084）：

```bash
nohup tmeet event consume meeting.started >events.ndjson 2>bus.err &
setsid tmeet event consume meeting.started < /dev/null
```

停止方式：SIGINT/SIGTERM，或另开终端执行 `tmeet event stop`。

## 5. 用 ready 标记做启动同步

编排脚本若在「订阅成功」后就要触发外部动作，应等待 stderr 的 ready 行（F-081）：

```bash
tmeet event consume meeting.started 2> >(grep --line-buffered '^\[event\]' >&2) \
  | while IFS= read -r line; do
      # 每行一个 bare JSON 事件（无 trace_id 信封，F-037）
      echo "$line" | jq -c '.'
      # 在这里触发你的自动化：拉参会名单 / 调 webhook / 写台账
    done
```

stderr 会出现：

```
[event] ready event_key=meeting.started
```

`--quiet` 也不屏蔽 ready 行；退出时 stderr 的 reason 为 limit/timeout/signal/shutdown 之一。

## 6. 多消费者共享一条连接

可同时开多个 consume（不同 EventKey 或不同过滤），它们由同一个 per-host bus 守护进程服务，底层只有一条 WSS 长连接，心跳/重连由 bus 统一处理（F-079）：

```bash
tmeet event consume meeting.started --jq '.[0].meeting_code' > started.log &
tmeet event consume meeting.end     --jq '.[0].meeting_code' > ended.log &
```

注意：事件**不回放历史**，只投递订阅建立后新产生的事件（F-084），所以先起消费者再等待会议发生。

## 7. bus 异常排查与自愈

```bash
tmeet event status
tmeet event status --fail-on-orphan ; echo "exit=$?"
```

| 状态 | 含义 | 处理 |
|------|------|------|
| running | 正常 | — |
| stale_owner | bus 绑定其他用户/当前未登录 | 重新登录对应账号（F-082） |
| orphan | 进程已死，pid/meta 残留 | `tmeet event stop --force` 清理 |

`--fail-on-orphan` 在异常态返回退出码 2，适合接监控告警（F-082）。`event stop --force` 是破坏性操作，Agent 中按二次确认流程执行。

相关错误码（F-098）：4000 EventInternal / 4001 EventBus / 4002 EventBusNotRunning；服务端 WSS token 过期码 200010203、10006（正常情况下 bus 会自动重连刷新）。

## 8. 一个完整自动化设想（命令级拼装）

会议开始 → 自动抓参会名单；会议结束 → 自动排队取纪要：

```bash
# 终端 1：开始事件 → 触发 report participants（该命令 --meeting-id 必填，不接受 --meeting-code）
tmeet event consume meeting.started --jq '.[0].meeting_id' | \
  while read -r mid; do
    tmeet report participants --meeting-id "$mid" --compact \
      >> "attendance_${mid}.jsonl"
  done

# 终端 2：结束事件 → 触发 minutes get（纪要路由逻辑见示例 02）
tmeet event consume meeting.end --jq '.[0] | [.meeting_code,.meeting_id] | @tsv' | \
  while IFS=$'\t' read -r code mid; do
    tmeet minutes get --meeting-id "$mid" >> "minutes_${code}.jsonl"
  done
```

> 实际 `meeting.started` / `meeting.end` payload 字段以 `tmeet event schema <EventKey>` 输出为准（已确认 jq_root_path 为 `.payload`，且长度 1 的数组契约目前仅覆盖这两个 key，见 F-173）；上例为演示管道组合方式。注意 `report participants`、`participants-export`、`waiting-room-log` 均以 `--meeting-id` 为必填标识，需要会议号时先用事件中的 meeting_id，或 `meeting get --meeting-code` 转换。
>
> ⚠️ **v0.3.0 源码复核更正**：结束事件的 EventKey 拼写是 **`meeting.end`**（command.md:1472 与 schemas.go:44-45 一致），不是 `meeting.ended`；写错会收到 UnknownEventKey（F-173/F-174）。

## 检查单

- [ ] 版本 ≥ v1.0.18
- [ ] consume 前先 `event list` + `event schema`，确认 jq_root_path
- [ ] stdout 走业务 NDJSON、stderr 走诊断与 ready
- [ ] 需要不漏事件时等 ready 再做依赖动作
- [ ] 定时任务用 `--max-events`/`--timeout`，长期驻留用信号或 `event stop`
- [ ] 监控接入 `event status --fail-on-orphan`（退出码 2）
- [ ] 不直接调用隐藏命令 `event _bus`（F-086）

## 相关概念

- [07 - 实时事件总线](../concepts/07-event-bus.md)
- [02 - 命令体系与全局约定](../concepts/02-command-map.md)
- [02 - 会后取纪要工作流](02-minutes-workflow.md)
