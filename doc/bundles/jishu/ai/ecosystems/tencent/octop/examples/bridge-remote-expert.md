---
type: Example
title: "联邦桥接：把远程 Octop 专家接入本地"
description: "通过 Bridge WebSocket 把另一台 Octop 上的专家以 bridge: 代理身份接入本地实例：探测、注册连接、握手重连、资源白名单与 SSRF 排错。"
tags: [octop, bridge, federation, websocket, tunnel, ssrf]
generated: { by: "reference_agent/trae-cn", at: 2026-10-04T10:00:00+08:00 }
verified: { by: "process:grep-v", at: 2026-10-04T10:00:00+08:00 }
status: stable
stale_after: 2027-10-04
sources:
  - id: bridge
    resource: /concepts/14-bridge-federation.md
    title: 联邦桥接
  - id: channels
    resource: /concepts/03-gateway-channels.md
    title: 网关与通道
---

# 联邦桥接：把远程 Octop 专家接入本地

本示例演示用 Bridge（联邦桥接）把远程 Octop 实例上的专家接入本地聊天：本地实例作为发起方（initiator）主动拨出，远程专家以 `bridge:<连接>:<专家id>` 的影子代理出现在本地。

## 场景与两侧准备

- **本地（发起方）**：能访问远程 HTTP 端口；用自己的用户登录本地 Dashboard/API
- **远程（被接入方）**：运行 `octop run`，有一个可登录账号（用户名+密码），该账号能看到要分享的专家；Bridge 端点随服务内置（`/api/bridge/ws`）

远程实例的对外地址（advertise URL）由启动配置推导：`public_base_url_from_config(bind_host, port)` 返回 `http://<host>:<port>`，当 host 为 `0.0.0.0` 或 `::` 时改写为 `127.0.0.1`（F-393）。因此远程若在反代/NAT 后，必须以反代域名或可达 IP 启动（如 `octop run --host 0.0.0.0` 前确保对方经域名访问），否则握手后回传的地址不可达。

凭证密钥无需手工配置：远程密码与访问令牌用 Fernet 加密落库，密钥在 secrets 表中按键名 `bridge_fernet` 自动生成（`get_or_create`，F-401）。

## 1. 先探测远程凭据

```bash
curl -X POST http://127.0.0.1:8088/api/bridge/probe \
  -H "Authorization: Bearer <jwt-token>" -H "Content-Type: application/json" \
  -d '{
    "peer_base_url": "https://octop.example.com",
    "peer_username": "bridge_user",
    "password": "<remote-password>"
  }'
```

探测只做登录 + 拉取专家列表，不建连接、不开 WS。底层 `POST /api/auth/login`，超时 20 秒；401 映射为「peer rejected credentials」。

## 2. 注册出站连接

```bash
curl -X POST http://127.0.0.1:8088/api/bridge/connections \
  -H "Authorization: Bearer <jwt-token>" -H "Content-Type: application/json" \
  -d '{
    "peer_base_url": "https://octop.example.com",
    "peer_username": "bridge_user",
    "password": "<remote-password>",
    "display_name": "云上专家",
    "notes": "生产环境 Octop",
    "icon_name": "cloud",
    "connect": true
  }'
```

`display_name` 必填且 1–64 字符（会话切换用的唯一名）；`connect` 默认 true，保存后立即拨号。之后可用 `POST /api/bridge/connections/{id}/connect|disconnect` 手动控制，`GET /api/bridge/connections/{id}/agents` 列出远程专家。

## 3. 握手与自动重连

拨号流程（F-385–F-391）：

1. 先用远程账号换 JWT，再升级 WS：`wss://<peer>/api/bridge/ws?token=<token>`（https 站点对应 wss）
2. WS 建连参数：`open_timeout=20`、`max_size=32 MiB`
3. 出站首帧为 `hello`，字段含 `type/protocol_version/connection_id/role/advertise_base_url/advertise_username/display_name`，`role` 逐字为 `"initiator"`，协议版本为 1（F-386、F-394）
4. 等待远程 `hello_ack` 20 秒；远程侧入站 hello 等待 30 秒。失败关闭码：4000 `hello required`、4002 `protocol mismatch`、4000 `connection_id required`、4003（其他校验失败）
5. 异常断线自动重连：**5 次**失败上限，退避间隔逐字为 2.0/4.0/8.0/16.0/30.0 秒（F-384）；服务重启后会恢复标记了自动重连的连接

## 4. 使用 bridge: 代理专家

连接成功后，远程专家以影子 id 注册到本地，形态逐字为 `bridge:{connection_id}:{remote_agent_id}`（F-394）。之后与本地专家无异：在 Dashboard 选择它聊天，或走聊天 WS；其所有 API 调用经入站 HTTP 隧道转发到远程 ASGI 应用（隧道客户端 base_url 为 `http://bridge.local`）。

远程并非全盘暴露，只允许 Agent 作用面（F-397、F-398）：

- `GET /api/agents`（列表只读）
- `/api/agents/<id>/` 下 **28 个**白名单子路径：threads、history、uploads、avatar、icon、chat、messages、files、workspace、attachments、media、turns、memory、skills、tools、tool-settings、mbti、persona、channels、cron、config、state、status、welcome、members、subagents、reload、acp
- 只读组合面：`providers/resolved`、`providers/active-model`、`knowledge-bases`、`knowledge-bases/capability`
- 浏览器仅 GET `browser/env-status`、`browser/harness-sessions` 与 POST 浏览器 handoff
- 管理面（用户、权限、设置、bridge 自身、auth）一律不可达；隧道还会剥离 host/content-length/authorization/cookie 等 6 个请求头（F-399）

## 5. 超时对照

| 环节 | 超时 | 出处行为 |
|------|------|----------|
| WS 建连 open_timeout | 20s | `websockets.connect(..., open_timeout=20, max_size=32MiB)`（F-385） |
| 远程登录 / 等 hello_ack | 20s | 出站侧（F-387） |
| 入站 hello 等待 / 探测 httpx | 30s | 服务端握手与 probe（F-387、F-389） |
| 单条隧道请求 | 120s | tunnel 默认 timeout=120（F-401） |
| 一轮对话等待 | 600s | turn 等待 600s（F-389） |
| 浏览器流 | 首帧 15s / 整体 600s | browser 等待（F-389） |

## 排错

| 现象 | 原因与处理 |
|------|-----------|
| `peer URL host is not allowed (link-local / metadata addresses blocked)` | 目标解析到链路本地/元数据地址，`169.254.0.0/16`、`fe80::/10`、`::ffff:169.254.0.0/112` 三网段恒拒（F-400）；改用普通内网/LAN 或公网域名 |
| `peer URL must be http or https` | scheme 只接受 http/https，且主机名必填（F-400） |
| 4000 `hello required` / 4002 `protocol mismatch` | 对端未在 30s 内发 hello，或协议版本不一致；确认双方均为带 Bridge 的 Octop 版本 |
| 提示 `peer may not support Bridge yet (needs Octop with /api/bridge/ws)` | 探测到 403/404；对端版本过旧或反代未放行 `/api/bridge/ws` |
| 能连上但远程资源 404/403 | 路径不在 28 子路径白名单或方法不允许（如 collection 只许 GET）；管理面永不开放（F-397、F-398） |
| 远程专家卡片/头像裂图 | 隧道只重写 icon_url 等 6 个 URL 键与 `/api/agents/` 路径段（F-396）；外链 http(s) 原样保留，本地需能直接访问该外链 |
| 重连不成功 | 5 次退避（2/4/8/16/30s）用尽后停止；改密/改地址用 `PATCH /api/bridge/connections/{id}`（会触发重新登录），再手动 connect |

## 相关概念

- [/concepts/14-bridge-federation.md](../concepts/14-bridge-federation.md)
- [/concepts/03-gateway-channels.md](../concepts/03-gateway-channels.md)
