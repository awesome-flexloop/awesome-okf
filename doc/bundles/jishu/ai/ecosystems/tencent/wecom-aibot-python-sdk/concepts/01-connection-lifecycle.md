---
type: concept
title: 连接生命周期
description: 从 connect 到认证、心跳保活、异常断连与指数退避重连的完整时序与边界条件
tags: [wecom, aibot, python-sdk, lifecycle]
generated: { by: okf-wiki/0.2, at: 2026-11-09 }
status: stable
verified: { by: "process:seven-concepts-v", at: "2026-11-09" }
stale_after: 2027-11-09
sources:
  - resource: vendor/WecomTeam/wecom-aibot-python-sdk/
  - resource: /references/facts.md
---

# 连接生命周期

## 一次连接的五个阶段

SDK 没有显式的状态机类，状态由「底层连接是否打开 + 是否收到认证回执 + 心跳是否在跑」三者共同表达。理解这条链路的关键是：**重连不是恢复旧会话，而是完整重跑一遍建连、认证、启动心跳**（F-020、F-022、F-024）。

| 阶段 | 动作 | 成功信号 | 失败信号 | 依据 |
|---|---|---|---|---|
| 清理 | `_cleanup_ws()` 收尾旧连接 | — | — | F-020 |
| 建连 | `websockets.connect(url, ssl=..., ping_interval=None, ping_timeout=None, close_timeout=5)` | 触发 `connected` | 异常进入重连调度 | F-020 |
| 认证 | 发送 `aibot_subscribe`（携带 `bot_id`、`secret`） | `errcode == 0` 时启动心跳并触发 `authenticated` | `errcode != 0` 仅触发 `error` | F-022、F-024 |
| 保活 | 每 30 秒发送 `ping`，等待回执清零计数 | 回执到达 | 连续缺席触发判死 | F-025、F-026 |
| 断连 | 停止心跳、清空待回执消息、触发 `disconnected` | — | — | F-023 |

## 建连与认证

`connect()` 的顺序是固定的：先清理旧连接，再建立 WebSocket，随后把 `_reconnect_attempts` 与 `_missed_pong_count` 同时置 0，依次触发 `on_connected()`、发送认证帧、以 `asyncio.ensure_future` 启动接收循环（F-020）。这里有两个容易忽略的细节：

1. 连接参数显式关闭了协议层 ping：`ping_interval=None`、`ping_timeout=None`，保活完全由业务层 `ping` 帧负责（F-020）。
2. 认证帧的 `req_id` 由 `generate_req_id("aibot_subscribe")` 生成，形如 `aibot_subscribe_毫秒时间戳_8位随机串`；服务端回执靠这个前缀被识别为认证响应（F-022、F-024、F-032）。

认证结果只有两条路：`errcode == 0` 时启动心跳并触发 `authenticated`；`errcode != 0` 时只调用 `on_error`，**既不关闭连接，也不安排重连**（F-024）。因此「认证失败」不是可自愈故障，客户端会停在「TCP 已连、业务未认证、心跳未启动」的静默状态。

## 心跳：缺席计数而非超时计时

心跳循环每轮先 `sleep(heartbeat_interval / 1000)`，默认 30 秒，再调用 `_send_heartbeat()`（F-025）。发送前的判定顺序决定了判死窗口：

1. 若 `_missed_pong_count >= 2`：记 `warn`、停止心跳、关闭底层连接，然后返回（F-026）。
2. 否则先把 `_missed_pong_count` 加 1，再发送 `{"cmd": "ping", "headers": {"req_id": "ping_..."}}`（F-026）。
3. 收到心跳回执且 `errcode == 0` 时把计数清零；`errcode != 0` 只记 `warn`，不清零（F-024）。

把顺序展开即可得到实际窗口：最后一次成功回执后，第 1 个周期发送 `ping` 并把计数置 1，第 2 个周期置 2，第 3 个周期才命中 `2 >= 2` 判死。也就是说默认判死时间约为 **90 秒**，而不是 30 秒；把 `heartbeat_interval` 调小会等比缩小该窗口，而 `_max_missed_pong = 2` 是硬编码的（F-025）。

## 异常断连与重连

判死本身不直接调用重连函数，它只是 `close()` 底层连接；真正的重连由接收循环完成：`async for` 因 `ConnectionClosed` 退出后，依次停止心跳、以原因清空待回执消息、触发 `disconnected`，并在非手动关闭时调用 `_schedule_reconnect()`（F-023、F-026）。

重连采用指数退避，序列为 1 秒、2 秒、4 秒、8 秒……上限 30 秒，公式为 `min(base × 2^(n-1), 30000)` 毫秒；`max_reconnect_attempts` 默认 10，设为 `-1` 表示无限（F-027）。上限判定是 `attempts >= max`，命中后触发 `error(Exception("Max reconnect attempts exceeded"))` 并彻底放弃（F-027）。手动 `disconnect()` 会置手动关闭标记、停止心跳、以 `Connection manually closed` 清空待回执消息，并以 `code=1000, reason="Manual disconnect"` 关闭连接，此路径不触发重连（F-028）。

| 断连原因 | 是否重连 | 说明 |
|---|---|---|
| 网络中断 / 心跳判死 | 是 | 接收循环捕获 `ConnectionClosed` 后调度 |
| 服务端主动关闭 | 是 | 只要不是手动关闭即进入退避 |
| 认证失败 | 否 | 连接不关闭，无重连计划 |
| 达到重连上限 | 否 | 触发 `error` 后停止 |
| 调用 `disconnect()` | 否 | `_is_manual_close = True` |

## 语义边界

- **无会话恢复**：重连后重新认证，期间错过的消息不会补发；需要可靠性的业务应在服务端或本地另行对账。
- **计数会清零**：任何一次握手成功都会把重连计数归零，所以「能连上但立刻断开」可以无限循环，`max_reconnect_attempts` 不是熔断器（F-020、F-027）。
- **连接存活判定**：`is_connected` 同时兼容 `websockets <= 13.x` 的 `ws.open` 与 `>= 14.x` 的 `ws.state is State.OPEN`（F-028）。

## 延伸阅读

- [帧协议与事件分发](/concepts/02-frame-protocol.md)：认证回执与心跳回执如何被 `req_id` 前缀识别。
- [流式回复与模板卡片](/concepts/03-streaming-and-card.md)：断连时待回执消息如何被清空。
- [概览与快速开始](/concepts/00-overview.md)：最小骨架中的连接事件注册。