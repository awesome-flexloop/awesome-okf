---
type: Concept
title: "事件总线内核：per-host bus 的分层、协议与生命周期"
description: "源码视角拆解 v1.0.18 事件子系统：source/bus/transport/busctl/spawner/busdiscover/consume_runner 七个组件、再 exec 自举与 alive-lock 选举、NDJSON 八类消息、wsspb 心跳重连、8 个硬编码 EventKey、owner 哈希隔离、引用计数订阅、背压去重与登出清理闭环。"
tags: [tencent-meeting, tmeet, source-code, event-bus, websocket, ipc, ndjson, daemon, wsspb]
generated: { by: "reference_agent/trae-solo", at: "2026-10-04T00:00:00Z" }
verified: { by: "process:seven-concepts-v", at: "2026-10-04T00:00:00Z" }
status: stable
stale_after: 2027-04-04
sources:
  - id: source-code
    resource: /references/source-code.md
    title: tencentmeeting-cli 源码主体（tag v1.0.18 @ e631b35）
  - id: skill-manifest
    resource: /references/skill-manifest.md
    title: CLI-SKILL 清单与 CHANGELOG（v1.0.18）
---

# 事件总线内核

> 用户面（如何 consume、ready/exit 契约、status/stop）见 [07 - 实时事件总线](07-event-bus.md)。本文深入 `internal/event/`，说明一个 `event consume` 背后实际运行着一套完整的单机 IPC（Inter-Process Communication，进程间通信）微内核。

## 分层全景

```
┌─────────────────────────────── 本机 ───────────────────────────────┐
│                                                                     │
│  event consume (CLI 进程)            event consume (第二个消费者)   │
│        │ consume_runner                     │                       │
│        ▼ NDJSON (hello/event/…)             ▼                       │
│  ┌────────────────── IPC transport ──────────────────┐              │
│  │ unix: <configDir>/event/bus.sock                  │              │
│  │ win : \\.\pipe\tmeet-event-bus (缓冲 65536)       │              │
│  └────────────────────▲──────────────────────────────┘              │
│                       │ busctl: Ping / QueryStatus / SendShutdown   │
│              ┌────────┴─────────┐                                   │
│              │  bus 守护进程      │  ← spawner 再 exec `event _bus`  │
│              │  (event _bus)     │     busdiscover 负责发现/选举    │
│              │  Hub fan-out      │                                   │
│              │  subRegistry 引用计数                                 │
│              │  dedup ring 512   │                                   │
│              └────────┬─────────┘                                   │
└───────────────────────┼─────────────────────────────────────────────┘
                         │ 一条 WSS 长连（source 层独占）
                         ▼
              wss://meeting.tencent.com/wemeet-socket/mercury-wss-cli/connection
```

七个组件各司其职（F-163）：source（WSS 连接生命周期）→ bus（守护进程内 Hub fan-out，每消费者 Conn 的 sendCh 容量 100）→ transport（IPC 收发）→ busctl（Ping/QueryStatus/Shutdown 控制面）→ spawner（自举）→ busdiscover（发现与存活判定）→ consume_runner（CLI 侧消费端适配，输出/退出码语义在此）。前六个在 bus 守护进程侧，consume_runner 在 consume 客户端侧。

## 自举与选举：为什么 pid 文件不代表存活

- **自举**：没有系统服务。第一个 consume 发现 bus 不在时，spawner 直接 `exec` 当前二进制再调隐藏命令 `event _bus`（F-165）。unix 用 Setsid 脱离控制终端；Windows 用 CREATE_NEW_PROCESS_GROUP(0x200) + HideWindow——**刻意不用 DETACHED_PROCESS**，以保留与 Setsid 对等的进程组信号语义；子进程 stdio 全 nil；ready 等待 5s、探测 ping 间隔 20ms。
- **存活判据**：`bus.alive.lock` 上的非阻塞 TryLock（F-166）。内核保证持锁进程死亡后锁必然释放；而 PID 会被复用、pid 文件会残留。因此：
  - `bus.pid`（pid + RFC3339，原子写）与 `bus.meta`（meta_version=1/openid_hash/started_at/bus_version/pid）**只是诊断信息**；
  - pid/meta 存在但锁拿得到 → orphan（进程已死的残留文件，对应用户面 F-082）；
  - 锁持有者的 openid_hash 与当前登录用户不同 → stale_owner。
- 并发 fork 用 `bus.fork.lock` 串行化（防双开 bus）；source 状态持久化在 `ws.state`。

## IPC 协议：NDJSON 八类消息

行分隔 JSON，共 8 种消息类型（F-170）：

`hello` / `hello_ack` / `event` / `control` / `bye` / `status_query` / `status_response` / `shutdown`

consumer 的 hello 帧要过三道校验（F-172）：

1. **owner hash**：必须等于 `sha256(openId)` 前 12 字节的 hex（24 字符）——不匹配返回 WrongOwner，实现多用户同机隔离；
2. **恰好声明 1 个 EventKey**，且该 key 已在注册表（UnknownEventKey）；
3. 参数合法（InvalidParams）。

消费者 trace_id 形如 `consume-<pid>-<nanos>`。

## source 层：一条 WSS 与 wsspb 协议

- 入口是一条 WSS（WebSocket Secure，加密 WebSocket）长连 `wss://meeting.tencent.com/wemeet-socket/mercury-wss-cli/connection`；自研 wsspb（protobuf），Head 含 frame_type/cmd_type/cmd/seq_no/msg_id/module/status（F-167）。
- 鉴权帧 AuthBindReq/AuthRefreshReq：biz_id 固定 `web_hook_cli`、token_type=`access-token`，携带 token/open_id/cli_uniq_id；cmd 常量含 `/conn/ping`、`/conn/access-token-auth-bind`、WsCLISubscribeEvent、WsCLIPushEvent（F-168）。
- **心跳与重连参数**（F-169）：

| 参数 | 值 |
|------|----|
| 心跳 | 应用层 `/conn/ping`（非 websocket control ping），默认 25s，服务端 heart_interval 可覆盖 |
| 握手超时 / 读超时 | 10s / 5min |
| 重连退避 | 1-30s |
| 放弃阈值 | 连续失败 30 次；稳态持续 >60s 后计数清零 |
| 关闭码 1006 | 触发重连；鉴权错误不重连 |
| token 轮换 | AuthRefresh 优先于下一次 ping 发出 |

source 状态机 6 态：connecting / reconnecting / steady / auth_failed / auth_expired / disconnected（F-171）。

## 事件注册表：封闭的 8 个 key

`internal/event/schemas.go` 中**实测 8 次 RegisterKey**（行 106/196/294/378/462/563/675/768）（F-173）：

| domain | EventKey |
|--------|----------|
| meeting（5） | meeting.created、meeting.updated、meeting.canceled、meeting.started、meeting.end |
| recording（1） | recording.completed |
| smart（2） | smart.transcripts、smart.minutes |

共性：jq_root_path 全部为 `.payload`；params 均为可选 meeting_id；线上 payload 形态为 `array<object>`。**长度恒为 1 的保证仅适用于 meeting.started / meeting.end 两个 key**（源码注释明确：数组形态是为未来批量推送预留，当前未启用）；其余 6 个 key 不做此保证，jq 一律写 `.[0]` 在未来批量推送启用后会静默丢元素，当前版本与 F-085 的用户面示例对应。

⚠️ **头注释提到的 `recording.failed` 并未注册**（F-174）。注册表不是开放扩展点——`event list` 列的是「这个二进制版本硬编码支持什么」，新增事件类型必须改代码发版本。这也是它能保证 `event schema` 全部本地可查（F-083）的代价。

## 多消费者复用：引用计数、背压与去重

- **引用计数** subRegistry：同 key 第一个消费者 0→1 才向服务端发 SUBSCRIBE；**最后一个消费者 1→0 时不发 UNSUBSCRIBE**——`Remove()` 虽返回 1→0 布尔值但 bus 不据此动作，契约是「消费者消失后由腾讯会议服务端按 TTL 自动取消订阅」（subreg.go/source.go 注释明确 "There is intentionally NO Unsubscribe"）；重连后用 `Snapshot()` 全量 Replay 重订阅。多个 consume 因而复用同一条服务端推送（F-175）。
- **背压**：每消费者独立有界队列（sendCh=100），满时 PushDropOldest 丢最旧保最新；dropped 计数按订阅者每 1s 聚合上报（F-176）。
- **去重**：容量 512 的 ring，键为 RawEvent.TraceID，吸收重连窗口内的重复推送（F-178）。
- **空闲退出**：无消费者时 IdleTimeout=30s 自动收摊（F-177）。

## 生命周期收尾：consume / stop / logout

- consume 就绪行 `[event] ready event_key=%s` 写 stderr 且 `--quiet` 不屏蔽；frameCh 容量 8；事件输入全部来自 IPC netConn，**不读 stdin**（nohup/setsid/`</dev/null` 均安全）；退出行 reason 为字符串 limit/timeout/signal/shutdown；退出码 2 仅用于 `status --fail-on-orphan` 与 `stop` 被拒绝/出错（F-179、F-180）。
- `--output-dir`：仅相对路径、拒绝绝对路径与 `..` 段、traceID 经 sanitizeTraceID 清洗、文件 0o600；落盘的是原始事件，不受 `--jq` 影响（F-181）。
- `event stop`：优雅等待 10s；仍有消费者且无 `--force` → refused(2)；`--force` 清理 pid/meta/sock 三件但**不删 alive lock**（F-182）。
- 登出钩子 cleanup.OnUserCleared：owner 匹配 → Shutdown 等 3s → 仍活按 PID SIGKILL/TerminateProcess → 清 sock/meta/pid（F-183）。
- `--jq` 基于 gojq；投影零结果时 dropped=true 静默丢弃（F-184）。

## 按层排障地图

| 症状 | 先查哪一层 | 关键判据 |
|------|-----------|----------|
| consume 卡住不出 ready | IPC/spawner | sock/管道是否存在、bus 是否被 stale_owner 占用（`event status`） |
| status 报 orphan/stale_owner | discover | pid/meta 残留 vs alive lock；`event stop --force` 清三件 |
| ready 后无事件 | source | `ws.state` 状态：auth_failed/auth_expired（重新登录）还是 reconnecting（网络） |
| 有事件但 jq 无输出 | 消费侧投影 | 8 key 拼写；`.payload` 为数组先 `.[0]`（长度 1 保证仅 meeting.started/end）；投影零结果按 dropped 静默丢弃 |
| 换账号后旧 bus 捣乱 | owner 隔离 | 旧账号 logout（钩子强杀）或 `--force` |
| 事件偶发重复/缺失 | 去重/背压 | TraceID 去重环 512；慢消费者 dropped 聚合行 |

> ⚠️ Windows 命名管道无显式 SDDL（Security Descriptor Definition Language，安全描述符定义语言；未设置时落到系统默认 ACL 访问控制列表），同机多用户隔离主要靠应用层 owner hash 而非 OS 强制；高敏环境需评估此项。

## 相关概念

- [07 - 实时事件总线](07-event-bus.md)（用户面命令与契约）
- [04 - 事件自动化示例](../examples/04-event-automation.md)
- [11 - 凭证安全内部机制](11-credential-security-internals.md)（登出停 bus 的 hook）｜[13 - 传输、输出与跨平台工程](13-cross-platform-engineering.md)

## 延伸阅读

- 信源登记：[references/source-code.md](../references/source-code.md)
- 核心洞察：[洞察八 · 单机 IPC 微内核](../spec/insights.md)
