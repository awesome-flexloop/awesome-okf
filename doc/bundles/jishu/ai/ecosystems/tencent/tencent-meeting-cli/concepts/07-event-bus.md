---
type: Concept
title: "实时事件总线：event 命令组与 per-host bus 守护进程"
description: "v1.0.18 新增的实时会议事件订阅：5 个 event 子命令、per-host bus 共享 WSS 长连接、NDJSON 流、stdout/stderr 契约、ready 标记、退出码语义与孤儿总线自愈。"
tags: [tencent-meeting, tmeet, event, websocket, ndjson, daemon, bus, real-time, v1.0.18]
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

# 实时事件总线（event，v1.0.18+）

v1.0.18（2026-09-11）新增 `event` 命令组，让 Agent/脚本可以订阅腾讯会议的实时事件（如会议开始、结束等），而不是轮询 REST API。

## 五个子命令

| 命令 | 作用 | 需登录 |
|------|------|--------|
| `event list` | 列出内置注册表中全部 EventKey（按 `domain, key` 排序） | 否（本地查询） |
| `event schema <EventKey>` | 查看事件的 params_schema、resolved_output_schema、jq_root_path | 否（本地查询） |
| `event consume <EventKey>` | 订阅消费事件（拉起/复用 bus，流式输出 NDJSON） | 是 |
| `event status` | 查看本机 bus 状态（可加 `--fail-on-orphan`） | 否 |
| `event stop` | 停止 bus（`--force` 清理残留，属破坏性操作需确认） | — |

（F-079、F-083、F-082）

## 架构：per-host bus + 共享 WSS

```
event consume A ──┐
event consume B ──┼──► 本机 bus 守护进程（隐藏命令 event _bus，自动拉起）
event consume C ──┘            │
                               ▼
                    一条 WSS 长连接（握手/心跳/重连由 bus 统一管理）
                               │
                               ▼
                    fan-out 给各消费者（NDJSON → 各自 stdout）
```

- 所有消费者**复用同一条 WSS 长连接**，bus 负责握手、心跳、自动重连（F-079）；
- 事件以 **NDJSON**（每行一个 JSON）写 stdout；诊断信息写 stderr；
- bus 存活探测基于进程级独占文件锁；`event _bus` 是隐藏子命令，Agent **不得直接调用**（F-086）；
- 登出时通过 ResourceReleaseHook 先停 bus 再清凭证（F-032）。

## consume 的两种运行模式

```bash
# 批处理：收满 N 条退出
tmeet event consume meeting.started --max-events 10

# 批处理：运行时长上限（30s / 5m 等）
tmeet event consume meeting.started --timeout 5m

# 常驻：两者都不传，靠 SIGINT/SIGTERM 或 event stop 退出
tmeet event consume meeting.started
```

（F-080）

常用选项：

| 选项 | 作用 |
|------|------|
| `--param key=value` | 按事件参数过滤（可重复） |
| `--jq <表达式>` | 用 gojq 在服务端/本地投影字段 |
| `--output-dir <相对目录>` | 事件落盘；仅接受相对路径，拒绝 `..` |
| `--quiet` | 静默（但不屏蔽 ready 标记） |

消费端不回放历史事件，**仅投递订阅之后新产生的事件**（F-084）。consume 不读取 stdin，因此 `< /dev/null`、nohup、setsid、后台 `&` 都不会让它退出（F-084）——这对定时任务与守护编排很友好。

## stdout/stderr 契约与退出码

脚本/Agent 编排的关键约定（F-081）：

- **ready 标记**（写 stderr）：`[event] ready event_key=<key>`，表示订阅已建立、此后不会漏事件。即使加了 `--quiet` 也会输出。编排脚本应以这一行为启动同步点（看到 ready 再开始依赖事件触发的动作）。
- **退出标记**：stderr 输出 reason，取值 `limit` / `timeout` / `signal` / `shutdown`。
- **退出码**：

| 码 | 含义 |
|----|------|
| 0 | 正常退出（收满/超时/收到信号/bus 关闭） |
| 1 | 致命错误 |
| 2 | 仅 `event status --fail-on-orphan` 与 `event stop` 在 refused/errored 时返回，适合健康检查判定 |

- **输出无信封**：event 族是 bare JSON，没有 `{trace_id,message,data}` 包装；`--compact` 对 event 无效（F-037）。

## bus 状态机与自愈

`event status` 可能报告（F-082）：

| 状态 | 含义 | 处置 |
|------|------|------|
| `running` | bus 正常 | — |
| `stale_owner` | bus 绑定的是其他用户或当前未登录 | 切换/登录后重启 |
| `orphan` | bus 进程已死，但 pid/meta 文件残留 | `event stop --force` 清理（需用户确认） |

健康检查模式：

```bash
tmeet event status --fail-on-orphan || echo "bus 需要人工处理，退出码=$?"
```

## jq 投影的陷阱

- `jq_root_path` 配置错误时**不会报错**，而是静默丢弃事件——订阅前先 `event schema <EventKey>` 确认根路径（F-085）；
- `meeting.started` / `meeting.end` 的 `jq_root_path` 为 `.payload`，且 payload 是长度恒为 1 的数组，jq 表达式要先 `.[0]` 再下钻（F-085）。

```bash
# 先查 schema 再写 jq
tmeet event schema meeting.started
tmeet event consume meeting.started --jq '.[0].subject'
```

## 相关错误码（F-098）

| 码 | 含义 |
|----|------|
| 4000 | EventInternal（事件客户端内部错误） |
| 4001 | EventBus（总线错误） |
| 4002 | EventBusNotRunning（总线未运行） |
| 200010203 / 10006 | 服务端 WSS token 过期（bus 应自动重连刷新） |

## Agent 使用要点

1. 先 `event list` 发现可用事件、`event schema` 确认字段与 jq 根路径，再 consume；
2. 用批处理模式（`--max-events`/`--timeout`）做定时采集，比自写 REST 轮询简单且不漏；
3. 需要「订阅成功后再动作」时，解析 stderr 的 ready 行做同步；
4. 流水线中只消费 stdout 的 NDJSON，诊断信息从 stderr 单独走；
5. 账号切换/异常后用 `event status --fail-on-orphan` 探测，按退出码 2 告警；
6. `event stop --force` 属破坏性操作，按二次确认流程执行（F-082）。

## 延伸阅读

- [02 - 命令体系与全局约定](02-command-map.md)（信封/分页契约与 event 例外）
- [08 - 应用配置与运维反馈](08-app-tshoot.md)
- 示例：[04 - 事件订阅自动化](../examples/04-event-automation.md)
