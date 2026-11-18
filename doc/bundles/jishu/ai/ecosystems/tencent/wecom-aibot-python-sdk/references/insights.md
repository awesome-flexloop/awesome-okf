---
type: reference
title: wecom-aibot-python-sdk 四元组洞察（I 阶段）
description: 基于 59 条源码事实提炼的 6 条四元组洞察，覆盖协议复用、流式队列、心跳判死、重连计数、私有解密约定与版本双口径
tags: [wecom, aibot, python-sdk, websocket, insights]
generated: { by: okf-wiki/0.2, at: 2026-11-09 }
phase: I（洞察提炼）
baseline: 6bcb59a9a636c566f4c6ea5268b228e3def1611a（pyproject 1.0.1 / __version__ 1.0.0）
status: stable
verified: { by: "process:seven-concepts-v", at: "2026-11-09" }
stale_after: 2027-11-09
sources:
  - resource: vendor/WecomTeam/wecom-aibot-python-sdk/
  - resource: /references/facts.md
---

# wecom-aibot-python-sdk 四元组洞察

本页把 [facts.md](/references/facts.md) 中 59 条零推测事实压缩为 6 条可行动的判断。每条按「陈述—证据—反常识—行动」四元组书写，证据只引用 F 编号，不重复抄录原文；若与源码冲突，以源码为准。

## 洞察一：一条连接承载全部语义，`req_id` 前缀被当作协议判别键

**陈述**：认证、心跳、回复、回执共用同一条 WebSocket。下行帧并不靠独立字段区分响应类型，而是看 `headers.req_id` 的字符串前缀：以 `aibot_subscribe` 开头判为认证响应，以 `ping` 开头判为心跳响应，命中 `_pending_acks` 则判为回复回执（F-022、F-024、F-039、F-042）。

**证据**：F-022（认证帧结构与 `SUBSCRIBE` 取值）、F-024（两处 `startswith` 分支）、F-032（`req_id = 前缀_毫秒时间戳_8位随机串`）、F-039（回复沿用入站帧的 `req_id`）。

**反常识**：常规协议用 `cmd` 或 `type` 字段路由，此处 `req_id` 既是关联键又是类型判别键。这意味着任何自定义 `req_id` 只要以 `ping_` 或 `aibot_subscribe_` 开头，就可能被误判为心跳或认证响应；反之，服务端若改变回执的 `req_id` 回填方式，整条回复链路会静默失效。

**行动**：自定义 `req_id` 前缀避开 `aibot_subscribe` 与 `ping`；抓包排障时先按前缀分类再按 `cmd` 分类；扩展协议时新增 `cmd` 常量，不要继续给 `req_id` 前缀叠加语义。

---

## 洞察二：「流式」在同 `req_id` 串行队列上实现为停等协议

**陈述**：`send_reply` 为每个 `req_id` 维护一条队列，队列上限 100；处理协程逐条 `send` 后 `await` 回执，回执超时 5.0 秒；`reply_stream` 的每次调用都走这条路径，`finish` 只是 `stream` 字段中的布尔值（F-037、F-038、F-040、F-041、F-042）。

**证据**：F-040（队列满时对新请求 `set_exception`，不丢旧帧）、F-041（`call_later(5.0, ...)` 与 `TimeoutError`）、F-042（`queue[0]` → `send` → `await ack` → `pop(0)` 的严格顺序）。

**反常识**：流式常被理解为「边生成边推送、不等待确认」，但此实现每帧必须等到回执才发下一帧。若一次回复拆成 N 帧，端到端耗时近似 `N × RTT`，模型推理时间与网络往返被串行叠加；队列满时抛错而非丢弃最旧消息，因此突发流量会把错误直接暴露给调用方。

**行动**：控制流式分片数量，把「逐 token 推送」改为「逐句/逐段推送」；不要在多协程中对同一 `frame` 并发调用 `reply_stream`；对 5 秒超时设计重试或降级话术。

---

## 洞察三：心跳判死是「缺席计数」而非「超时计时」，默认窗口约 90 秒

**陈述**：心跳循环每 30 秒执行一次；发送前先检查 `_missed_pong_count >= 2`，未命中才自增并发送 `ping`；收到心跳回执则清零。判死时停心跳并关闭底层连接，由接收循环的 `ConnectionClosed` 分支间接触发重连（F-025、F-026、F-023）。

**证据**：F-025（`_max_missed_pong = 2`、间隔 30000 毫秒）、F-026（先判后发、命中即 `close()`）、F-023（`ConnectionClosed` → `_stop_heartbeat` → `on_disconnected` → `_schedule_reconnect`）。

**反常识**：从最后一次成功回执算起，第 1、2 个周期各补发一次 `ping` 并把计数推到 2，第 3 个周期开始才命中判死条件，因此默认窗口约 90 秒，而不是 30 秒；判死动作本身不调用重连函数，而是「关连接 → 等接收循环抛异常 → 再重连」，若关闭未能让 `async for` 退出，重连就不会发生。

**行动**：用 `disconnected` 事件时间戳监控真实断连；需要更快发现半开连接时缩短 `heartbeat_interval`（会等比缩小判死窗口），不要指望修改 `_max_missed_pong`（硬编码）。

---

## 洞察四：重连上限统计的是「连续建连失败」，握手成功即清零

**陈述**：`connect()` 在 `websockets.connect` 成功后立即把 `_reconnect_attempts` 与 `_missed_pong_count` 置 0；`_schedule_reconnect` 以 `attempts >= max_reconnect_attempts` 判定放弃，退避为 `min(1000 × 2^(n-1), 30000)` 毫秒（F-020、F-027）。

**证据**：F-020（握手成功后清零）、F-027（10 次上限、`-1` 无限、指数退避上限 30 秒）、F-024（认证失败只调 `on_error`，既不关闭连接也不安排重连）。

**反常识**：`max_reconnect_attempts = 10` 容易被理解为「整个进程最多重连 10 次」，实际上任何一次 TCP/TLS 握手成功都会清零，所以「能连上但随即断开」的场景可以无限循环，该参数不构成熔断。更隐蔽的是认证失败路径：连接保持打开、心跳未启动、无重连计划，客户端会停在「已连接但未认证」的静默状态。

**行动**：不要用该参数做熔断器，应在 `authenticated` 事件上做健康断言、在 `disconnected` 上累计告警；认证失败需显式重启或告警，不要等待自动恢复。

---

## 洞察五：文件解密是「带私有约定的 AES-CBC」，不是标准 PKCS#7 栈

**陈述**：`decrypt_file` 先给 `aes_key` 补 Base64 填充并解码得到密钥，取 `iv = key[:16]`，把密文零补齐到 16 字节整数倍后解密，再手写去填充：`pad_len` 允许 1 至 32，并要求尾部每个字节都等于 `pad_len`（F-053、F-054）。

**证据**：F-050（无 `aes_key` 时原样返回）、F-051（`aiohttp` 下载，默认总超时 10 秒）、F-052（优先解析 RFC 5987 的 `filename*`）、F-053、F-054（补零、`pad_len` 上限 32、异常包装）。

**反常识**：标准 PKCS#7 的填充长度不可能超过块长 16，这里却允许到 32，说明实现复用了 32 字节块的约定；同时「先零补齐再解密」看似会破坏填充，但因 CBC 只对最后一组做异或，尾部填充仍然有效。文件名解析则依赖 `Content-Disposition`，两套正则都不命中时返回 `None`。

**行动**：跨语言复刻时照抄「补零 + `pad_len ≤ 32`」两处；不要直接套用通用 unpad；文件名缺失时用 URL 末段兜底，避免写盘时 `None` 参与拼接。

---

## 洞察六：版本双口径并存，且测试基础设施「有痕迹、无本体」

**陈述**：打包元数据版本为 `1.0.1`，运行期 `aibot.__version__` 为 `1.0.0`，示例启动日志同样打印 `1.0.0`；仓库 19 个受控文件中没有 `tests/` 目录，但 `.gitignore` 预留了 `.pytest_cache/`、`.coverage`、`htmlcov/`（F-002、F-008、F-009、F-059）。

**证据**：F-002、F-008、F-009（三处字符串并置）、F-059（19 文件清单与忽略项）。

**反常识**：`pip show` 看到 1.0.1，`aibot.__version__` 看到 1.0.0，用后者做兼容判断会误判；而「忽略文件里写了测试产物」并不代表存在测试，基线里一行测试代码都没有，任何行为结论只能来自源码阅读与示例脚本。

**行动**：问题单注明「打包 1.0.1 / 运行期 1.0.0」；兼容性断言以 `pyproject.toml` 为准；升级前用 `git diff` 核对 `aibot/` 九个模块，而不是只看版本号。

## 概念文档知识地图

5 篇概念文档构成「先建立全局，再逐层下钻」的依赖链，建议按 00 → 01 → 02 → 03 → 04 顺序阅读：

| 文档 | 回答的问题 | 依赖 | 被依赖 |
|---|---|---|---|
| [00-overview](/concepts/00-overview.md) | 它是什么、怎么装、最小骨架长什么样 | 无 | 全部 |
| [01-connection-lifecycle](/concepts/01-connection-lifecycle.md) | 连接如何建立、认证、保活与重建 | 00 | 02、03、04 |
| [02-frame-protocol](/concepts/02-frame-protocol.md) | 帧长什么样、`req_id` 如何路由、事件如何分发 | 01 | 03、04 |
| [03-streaming-and-card](/concepts/03-streaming-and-card.md) | 流式回复与模板卡片的时序与队列约束 | 01、02 | 04 |
| [04-file-download-decrypt](/concepts/04-file-download-decrypt.md) | 媒体如何下载、解密、命名 | 01、02 | 无 |

学习路径：先读 00 建立「机器人通道 SDK」的定位并跑通骨架；再用 01 理解「连接是一次性的、重连是新建连接」；随后用 02 掌握帧与事件分发，这是读 03、04 的前置；03 的串行队列是理解流式延迟的关键；04 可作为独立工具链单独查阅。示例文档 [examples/](/examples/index.md) 与 00、03、04 一一对应，可在读完概念后对照。