---
type: Concept
title: "Octop↔Octop 联邦桥接：经隧道使用远程专家"
description: "Bridge 子系统：bridge: 影子代理、WS 握手与关闭码、120 秒 HTTP 隧道、28 条 agent 子路径白名单、链路本地 SSRF 阻断、Fernet 凭证加密与自动重连退避。"
tags: [octop, bridge, federation, websocket, tunnel, shadow-agent, ssrf, fernet]
generated: { by: "reference_agent/trae-cn", at: 2026-10-04T10:00:00+08:00 }
verified: { by: "process:grep-v", at: 2026-10-04T10:00:00+08:00 }
status: stable
stale_after: 2027-10-04
sources:
  - id: facts
    resource: /spec/facts.md
    title: Octop 源码事实清单 F-384~F-401（v1.0.2b5）
  - id: proto
    resource: /references/bridge-protocol.md
    title: Octop↔Octop 桥接协议信源登记
---

# Octop↔Octop 联邦桥接：经隧道使用远程专家

桥接是 1.0.2b5 引入的联邦能力（CHANGELOG 原文「Octop↔Octop 云端桥接，经隧道使用远程专家」，F-150）。两台自托管 Octop 之间建立一条出站 WebSocket，发起方把对端的专家以 `bridge:` 前缀的**影子代理**挂进自己的列表，用户像使用本地 Agent 一样聊天，而 HTTP 请求、实时流、浏览器画面经隧道转发到对端执行。

## 1. 架构总览

```
   发起方 Octop（hub）                         对端 Octop（peer，专家持有者）
 ┌──────────────────────┐      WSS 出站       ┌──────────────────────┐
 │ BridgeManager        │ ───────────────────► │ /api/bridge/ws       │
 │  └ BridgeSession     │   hello / hello_ack  │  （token=对端登录态） │
 │ 影子专家 bridge:cid:aid│                     │                      │
 │         │            │ ◄══════════════════► │ 真实 Agent 运行时     │
 │         ▼            │  tunnel.request/response│                    │
 │ Dashboard / IM / 团队 │  turn.*  browser.*     │  ASGI 本地回环       │
 └──────────────────────┘   帧多路复用           └──────────────────────┘
```

对端落地 HTTP 时**不走网络**：隧道请求在对端进程内经 `httpx.ASGITransport(app=app)` 直接打回本进程 ASGI 应用，base_url 固定 `http://bridge.local`，超时 120.0 秒（F-399）。凭证用 Fernet 加密落库（密钥 settings 键 `bridge_fernet`，F-401）。

## 2. 协议版本与影子代理标识

`bridge/ids.py` 定义协议的两个锚点常量（F-394）：

```python
BRIDGE_AGENT_PREFIX = "bridge:"
_BRIDGE_PROTOCOL_VERSION = 1
PROTOCOL_VERSION = _BRIDGE_PROTOCOL_VERSION
# 影子 id 形态：f"bridge:{cid}:{aid}"
```

`format_bridge_agent_id(connection_id, remote_agent_id)` 对两端 strip 后拼接：空值抛 ValueError，connection_id 含 `:` 也抛错（F-394）。影子 id 让发起方的 Agent 列表、团队成员、URL 路径都能无冲突地承载远程专家。

## 3. 连接生命周期

### 3.1 装配位置：_boot_runtime 尾部

BridgeManager 在服务器启动序列的**尾部**、AppRuntime 组装之前构造（F-168、F-170）：

```python
advertise = public_base_url_from_config(config.bind_host, config.port)
BridgeManager(
    bridge_repo=services.bridge_connection_repo,
    secret_repo=services.secret_repo,
    user_repo=services.user_repo,
    advertise_base_url=advertise,
    token_signer=_sign_user_token,   # 用 secret_repo.get("jwt") 按 access_token_ttl 签 owner token
)
# 装配末尾：
asyncio.create_task(_resume_bridges(), name="bridge-auto-resume")
```

`public_base_url_from_config` 会把通配主机名 `0.0.0.0` 与 `::` 改写为 `127.0.0.1` 再对外通告（F-393）。自动恢复任务以 `with suppress(Exception)` 包裹，best-effort 不阻塞启动（F-170）。`AppRuntime` 因此新增第 8 个字段 `bridge_manager`（F-163）。

### 3.2 探测、登录与自动重连

```python
_AUTO_RECONNECT_MAX_FAILURES = 5
_AUTO_RECONNECT_BACKOFF_SEC = (2.0, 4.0, 8.0, 16.0, 30.0)
```

失败计数达 5 即停止重连；退避按 `failures - 1` 索引并钳到末位 30 秒（F-384）。`resume_auto_connections` 只恢复 `auto_reconnect` 开启的出站连接，跳过 inbound 方向记录（F-384）。建连前先以 30 秒超时 httpx 探测对端，再由 peer_auth 以 20 秒超时 POST 对端 `api/auth/login`（JSON 体键 username/password）换取 access_token（F-389、F-400）。

### 3.3 关闭语义

删除连接时向活动会话发送 `{"type": "close", "reason": "deleted"}`，出站循环识别该 reason 后退出；`last_error` 一律截断到 500 字符（F-390）。

## 4. 握手帧与超时表

WebSocket 调用字面为 `websockets.connect(url, open_timeout=20, max_size=32 * 1024 * 1024)`（F-385）。出站 hello 帧按固定顺序携带 7 个键（F-386）：

```python
{"type": ..., "protocol_version": ..., "connection_id": ...,
 "role": "initiator",
 "advertise_base_url": ..., "advertise_username": ..., "display_name": ...}
```

| 场景 | 超时 | 信源 |
|------|-----:|------|
| 隧道请求默认 / ASGI 客户端 | 120.0 秒 | F-401、F-399 |
| WS open_timeout / 等待 hello_ack | 20 秒 | F-385、F-387 |
| 对端登录 / 对端探测 | 20.0 / 30.0 秒 | F-400、F-389 |
| 入站 hello 等待 | 30 秒 | F-387 |
| turn 队列等待 | 600.0 秒 | F-389 |
| browser 队列等待 / 首帧 | 600.0 / 15 秒 | F-389 |

入站帧分发在 manager.py:883 有独立的 hello_ack 处理分支（F-391）。版本不符时抛 `BRIDGE_PEER_UNREACHABLE "bridge protocol mismatch: peer=... local=1"`（F-387）。出站侧在对端回错误帧时由 manager.py:956 发送 `tunnel.error` 帧转交错误处理（F-391）；非 OctopError 异常统一回 code `"TUNNEL_ERROR"`，message 截断 500（F-401）。

### 关闭码（入站握手）

| 关闭码 | reason 字面 | 触发条件 |
|-------:|-------------|----------|
| 4000 | `"hello required"` | 30 秒内无合法文本帧 / 帧非 JSON / type 非 hello |
| 4002 | `"protocol mismatch"` | 入站 protocol_version ≠ 1 |
| 4000 | `"connection_id required"` | hello 帧 connection_id 为空 |
| 4003 | `"connection owned by another user"` | connection_id 已被其他用户占用 |

来源：F-388。

## 5. 影子 ID 与 URL 重写

隧道载荷是递归 JSON，ids.py 按键名精确重写身份（注释明确禁止子串裸替换，因为团队房间 id 形如 `{room}~{member}`）（F-395、F-396）：

| 集合 | 键 | 数量 |
|------|----|---:|
| `_TUNNEL_AGENT_ID_KEYS` | agent_id、speaker_agent_id、from_agent_id、to_agent_id、host_agent_id、remote_agent_id | 6 |
| 列表键 | member_ids、target_agent_ids | 2 |
| `_TUNNEL_URL_KEYS` | icon_url、icon、url、preview_url、access_url、image_url | 6 |

入站方向把对端本地 id 映射为 `bridge:{cid}:{aid}`，反向 `restore_peer_path_ids` 把影子 id 还原，使陈旧标签页仍能加载 `…/threads/{room}~bridge:cid:member/history`；路径段重写正则锚定 `/api/(?:plugins/)?agents/`（F-396）。图标 URL 另有规则：`/experts/` 内置资源原样保留，对端上传头像（以 `/avatar`/`/icon` 结尾）改走本地 `bridge_avatar_api_path`，http(s) 外链保留（F-392、F-401）。

## 6. 28 条子路径白名单与 SSRF 黑名单

### 6.1 agent 资源白名单（9+9+10）

`_AGENT_RESOURCE` 正则内联 28 个子路径，源码按三行分组（F-397）：

| 组 | 子路径 |
|----|--------|
| 第一组 9 | threads、history、uploads、avatar、icon、chat、messages、files、workspace |
| 第二组 9 | attachments、media、turns、memory、skills、tools、tool-settings、mbti、persona |
| 第三组 10 | channels、cron、config、state、status、welcome、members、subagents、reload、acp |

白名单主体同时接受影子 id 与普通 id：`^/api/agents/(?:bridge:[^/]+|[^/]+)`（F-397）。此外集合列表 `^/api/agents/?$` 仅允许 GET；composer 只读面（providers/resolved、providers/active-model、knowledge-bases、knowledge-bases/capability）仅 GET；browser handoff 仅 POST；其余一切路径（含全部 `/api/bridge/*` 管理面）兜底拒绝（F-398）。越权路径在对端抛 `BRIDGE_REMOTE_UNSUPPORTED "This action is not available through the remote bridge. Manage it on the peer Octop."`（F-399）。

### 6.2 SSRF：链路本地/元数据地址阻断

```python
_BLOCKED_NETWORKS = (
    ipaddress.ip_network("169.254.0.0/16"),          # IPv4 链路本地/云元数据
    ipaddress.ip_network("fe80::/10"),               # IPv6 链路本地
    ipaddress.ip_network("::ffff:169.254.0.0/112"),  # IPv4-mapped IPv6
)
```

主机名经 `socket.getaddrinfo` 逐结果查网段，解析失败报 "peer host could not be resolved"；scheme 只接受 http/https，命中阻断网段报 "peer URL host is not allowed (link-local / metadata addresses blocked)"（F-400）。入站请求还会丢弃 6 个请求头（host、content-length、connection、transfer-encoding、authorization、cookie），清洗后注入属主 Bearer token；响应头白名单丢弃 4 个（F-399）。

## 7. 安全模型：单资源授权，而非主机互信

桥接的信任边界设计值得显式记录：

1. **凭证是对端的一个普通用户账号**——发起方持 username/password 登录换 token（F-400），对端用既有用户/权限体系裁决每个请求，没有额外的「主机互信」超级通道。
2. **能力面被白名单收窄**——即使凭证有效，隧道也只能触达 28 条 agent 子路径与少量只读 composer/browser 路径，管理面（连接管理、用户、系统设置）全部不可达（F-397、F-398）。
3. **身份按属主重写**——入站请求丢弃原始 authorization/cookie，改注入该连接 owner 的 token，防止发起方伪造身份（F-399）。
4. **凭证静态加密**——password 与 access_token 分别经 Fernet 加密后存入 `bridge_connections` 表（F-390、F-401）。
5. **网络出口收敛**——SSRF 黑名单阻止把对端当成打云元数据服务（169.254.0.0/16）的跳板（F-400）。

完整的端点登记、帧模型与模块分工见信源 [bridge-protocol.md](../references/bridge-protocol.md)。

## 相关概念

- [/concepts/01-server-lifecycle.md](01-server-lifecycle.md)——BridgeManager 在 _boot_runtime 尾部的装配顺序
- [/concepts/05-acp-protocol.md](05-acp-protocol.md)——另一种跨进程 Agent 互操作通道（ACP stdio）
- [/references/bridge-protocol.md](../references/bridge-protocol.md)——协议细节信源（关闭码、端点、帧表）
