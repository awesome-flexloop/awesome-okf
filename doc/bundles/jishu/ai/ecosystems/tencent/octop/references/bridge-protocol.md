---
type: Reference
title: "Octop↔Octop 桥接协议信源登记"
description: "Bridge 子系统源码信源登记：bridge: 影子 ID、WS 握手帧与关闭码、HTTP 隧道 28 条 agent 子路径白名单、SSRF 防护、凭证 Fernet 加密与 /api/bridge 管理面端点。"
tags: [octop, bridge, websocket, tunnel, shadow-agent, ssrf, fernet]
generated: { by: "reference_agent/trae-cn", at: 2026-10-04T10:00:00+08:00 }
verified: { by: "process:grep-v", at: 2026-10-04T10:00:00+08:00 }
status: stable
stale_after: 2027-10-04
sources:
  - id: src
    resource: /spec/facts.md
    title: Octop 源码事实清单 F-384~F-401
---

# Octop↔Octop 桥接协议

本信源登记 `src/octop/infra/bridge/`（manager.py、ids.py、tunnel_policy.py、http_tunnel.py、peer_auth.py、crypto.py、transport.py、icons.py）与 `src/octop/api/routers/bridge.py`、`src/octop/infra/server.py` 中桥接装配点的全部可验证事实。源码版本 v1.0.2b5（commit e473dd3c，MIT）。

## 1. 协议常量与影子代理标识（ids.py）

```python
BRIDGE_AGENT_PREFIX = "bridge:"                 # ids.py:10（F-394）
_BRIDGE_PROTOCOL_VERSION = 1                    # ids.py:11（F-394）
PROTOCOL_VERSION = _BRIDGE_PROTOCOL_VERSION     # ids.py:13，对外导出名（F-394）
# 代理 id 形态：f"bridge:{cid}:{aid}"（ids.py:33，F-394）
```

`BridgeAgentRef` 为 frozen dataclass（connection_id、remote_agent_id），`agent_id` 属性返回 `format_bridge_agent_id` 结果；格式化时 connection_id 与 remote_agent_id 均 `strip()` 且不得为空，connection_id 含 `:` 抛 ValueError（ids.py:16-33）。

隧道载荷中需要重写的身份键（ids.py:90-110，F-395、F-396）：

| 集合 | 键（逐字清点） | 数量 |
|------|----------------|------|
| `_TUNNEL_AGENT_ID_KEYS`（:90-99） | agent_id、speaker_agent_id、from_agent_id、to_agent_id、host_agent_id、remote_agent_id | 6 |
| `_TUNNEL_AGENT_ID_LIST_KEYS`（:100） | member_ids、target_agent_ids | 2 |
| `_TUNNEL_URL_KEYS`（:101-110） | icon_url、icon、url、preview_url、access_url、image_url | 6 |

路径段重写正则（ids.py:111，F-396）：

```python
_AGENT_API_PATH_RE = re.compile(r"(/api/(?:plugins/)?agents/)(?!bridge:)([^/?#]+)")
```

来源：F-394、F-395、F-396。

## 2. 连接生命周期、装配点与自动重连

### 2.1 进程装配（infra/server.py `_boot_runtime` 尾部）

BridgeManager 装配于 `_boot_runtime` **尾部**、`AppRuntime` 组装之前（server.py:486-524）：局部导入 `sign_token` 与 `BridgeManager, public_base_url_from_config`；`_sign_user_token` 用 `secret_repo.get("jwt")` 密钥按用户 id/username/role 与 `access_token_ttl_seconds` 签发 owner token；`advertise = public_base_url_from_config(config.bind_host, config.port)`；随后以 bridge_connection_repo、secret_repo、user_repo、advertise_base_url、token_signer 构造 `BridgeManager`（F-393）。

当前 `AppRuntime` 组装含 8 个字段：agent_registry、gateway、cron_manager、user_manager、proactive_scheduler、trajectory_service、history_archive、bridge_manager（server.py:515-524；bridge_manager 为本次新增字段）。装配末尾创建自动恢复任务：`asyncio.create_task(_resume_bridges(), name="bridge-auto-resume")`，内层 `_resume_bridges` 以 `with suppress(Exception)` 包裹 `bridge_mgr.resume_auto_connections()`（server.py:530-534，best-effort）。

### 2.2 重连策略（manager.py 模块级常量）

```python
_AUTO_RECONNECT_MAX_FAILURES = 5                       # manager.py:35（F-384）
_AUTO_RECONNECT_BACKOFF_SEC = (2.0, 4.0.0, 8.0, 16.0, 30.0)  # manager.py:36，5 个浮点元素（F-384）
```

失败计数达到 5 停止重连（manager.py:664）；退避按 `failures - 1` 索引并钳到末位（:678-679），首连失败取首段 2.0（:701）。`resume_auto_connections` 遍历 `repo.list_auto_reconnect()`，跳过 inbound 方向的连接（manager.py:610-627）。

### 2.3 出站握手与登录

- 探测对端：`httpx.AsyncClient(timeout=30.0, follow_redirects=True)`（manager.py:236）（F-389）。
- 登录由 peer_auth.py 完成：POST 对端 `api/auth/login`，JSON 体键为 username、password，默认超时 20.0（peer_auth.py:76-91）；401 抛 BRIDGE_AUTH_FAILED "peer rejected credentials"，其余 ≥400 同样归认证失败；响应必须含非空 `access_token`（F-400）。
- WebSocket 连接调用字面为 `websockets.connect(url, open_timeout=20, max_size=32 * 1024 * 1024)`（manager.py:746）（F-385）。URL 由 `peer_ws_url` 生成：https→wss、http→ws，形态 `/api/bridge/ws?token={token}`（peer_auth.py:68-73）（F-400）。
- 出站 hello 帧（manager.py:749-757）键依次为 type、protocol_version、connection_id、role、advertise_base_url、advertise_username、display_name；role 字面值 `"initiator"`；advertise_base_url 缺省 `"http://127.0.0.1"`（F-386）。
- hello_ack 等待超时 20 秒（manager.py:762）；收到后比对 `protocol_version`，不等则抛 OctopError(BRIDGE_PEER_UNREACHABLE, "bridge protocol mismatch: peer={peer_version} local={PROTOCOL_VERSION}")（manager.py:774-782）（F-387、F-391）。
- 入站 hello 等待超时 30 秒（manager.py:824）；入站侧对 advertise_base_url 做 `normalize_peer_base_url`，异常时回落 `http://127.0.0.1`，advertise_username 缺省 "peer"（manager.py:840-846）（F-387）。

### 2.4 凭证加密与删除语义

- `_FERNET_KEY = "bridge_fernet"`（bridge/crypto.py:12）；`encrypt_payload`/`decrypt_payload` 与 connectors 同模式：Fernet 配合 `json.dumps(ensure_ascii=False)` 的 utf-8 字节，密钥经 `SecretRepo.get_or_create(_FERNET_KEY, Fernet.generate_key)` 取得（crypto.py:15-27）（F-401）。
- 创建/更新连接时 password 与 access_token 分别传入加密函数落库（manager.py:358-359）（F-390）。
- 删除连接时向活动会话发送 `{"type": "close", "reason": "deleted"}`（manager.py:397）；出站循环识别 `close_reason == "deleted"`（:914）（F-390）。
- `last_error` 截断长度 500（manager.py:441、:657、:670）（F-390）。
- `advertise_base_url` 可经 `set_advertise_base_url` 更新，写入时 `rstrip("/")`（manager.py:144、:163-164）。

来源：F-384、F-385、F-386、F-387、F-389、F-390、F-391、F-393、F-400、F-401。

## 3. 帧模型与超时表

`BridgeSession`（bridge/transport.py）是单连接 WS 的多路复用会话，承载 HTTP tunnel、turn、browser 三类帧；JSON 序列化使用 `ensure_ascii=False` 与 `bridge_json_default`（兼容 Pydantic/LangChain 对象，transport.py:21-38、:79-82）。

| 帧类型 | 处理位置 | 语义 |
|--------|----------|------|
| `close` | transport.py:93 | 记录 close_reason 后关闭会话；挂起的 Future 以 ConnectionError("bridge session closed") 失败（:75-77） |
| `tunnel.request` | transport.py:97 | 回调 on_tunnel_request，成功回 `tunnel.response`（:101） |
| `tunnel.error`（OctopError） | transport.py:108 | code 取 `exc.code.value`，message 截断 500（:111） |
| `tunnel.error`（非 OctopError） | transport.py:118 | code 字面 `"TUNNEL_ERROR"`（:120），message 截断 500（:121） |
| `tunnel.response` / `tunnel.error` | transport.py:125 | 按 id 唤醒 `_pending` Future |
| `tunnel.request`（发起侧构造） | transport.py:158 | 帧含 id（uuid4().hex）、method、path、query、headers，可选 body_b64（:157-166） |
| `turn.*` / `browser.*` | transport.py:131-136 | 分别委托 on_turn_frame / on_browser_frame |

超时常量清单：

| 场景 | 超时 | 位置 |
|------|------|------|
| tunnel 请求默认 timeout | 120.0 秒 | transport.py:148（F-401） |
| 入站 HTTP 隧道 ASGI 客户端 | 120.0 秒 | http_tunnel.py:91（F-399） |
| 出站 WS open_timeout / hello_ack 等待 | 20 秒 | manager.py:746、:762（F-385、F-387） |
| 对端登录 / 对端探测 | 20.0 / 30.0 秒 | peer_auth.py:81、manager.py:236（F-389、F-400） |
| 入站 hello 等待 | 30 秒 | manager.py:824（F-387） |
| turn 队列等待 | 600.0 秒 | manager.py:1391（F-389） |
| browser 队列等待 | 600.0 秒 | manager.py:1596（F-389） |
| browser 首帧等待 | 15 秒 | manager.py:1576（F-389） |

出站侧判定回帧为 tunnel.error 时转交错误处理（manager.py:956）（F-391）。来源：F-389、F-391、F-399、F-400、F-401。

## 4. WebSocket 关闭码

### 4.1 桥接协议层（manager.py 入站握手）

| 关闭码 | reason 字面 | 触发条件 | 行号 |
|--------|-------------|----------|------|
| 4000 | `"hello required"` | 30 秒内未收到合法文本帧 / 帧非 JSON | manager.py:827 |
| 4000 | `"hello required"` | 帧非 dict 或 type 非 "hello" | manager.py:830 |
| 4002 | `"protocol mismatch"` | 入站 `protocol_version` 不等于本地 PROTOCOL_VERSION（=1） | manager.py:834 |
| 4000 | `"connection_id required"` | hello 帧 connection_id 为空 | manager.py:838 |
| 4003 | `"connection owned by another user"` | 该 connection_id 已存在且 owner_user_id 与当前登录用户不同 | manager.py:849-850 |

来源：F-388。

### 4.2 API 层（api/routers/bridge.py，WS 握手阶段）

| 关闭码 | reason | 位置 |
|--------|--------|------|
| 4001 | `"missing token"` | browser-stream WS :426；/bridge/ws :512 |
| 4001 | `f"auth: {exc.code.value}"` | browser-stream WS :431；/bridge/ws :517 |
| 1011 | `"bridge not ready"` | browser-stream WS :436；/bridge/ws :521 |
| 1011 | `str(exc.code.value)` | browser-stream WS :442 |

## 5. HTTP 隧道路径白名单与 SSRF 防护

### 5.1 agent 资源 28 个子路径（逐字登记）

`_AGENT_RESOURCE`（tunnel_policy.py:10-17）正则内联子路径实测 28 个，源码三行分组为 9 + 9 + 10，以下逐字列出（F-397）：

```python
r"(?:/(?:threads|history|uploads|avatar|icon|chat|messages|files|workspace"      # tunnel_policy.py:13 —— 9 个
r"|attachments|media|turns|memory|skills|tools|tool-settings|mbti|persona"       # tunnel_policy.py:14 —— 9 个
r"|channels|cron|config|state|status|welcome|members|subagents|reload|acp"       # tunnel_policy.py:15 —— 10 个
```

第一组（9 个，tunnel_policy.py:13）：

| # | 子路径 |
|---|--------|
| 1 | threads |
| 2 | history |
| 3 | uploads |
| 4 | avatar |
| 5 | icon |
| 6 | chat |
| 7 | messages |
| 8 | files |
| 9 | workspace |

第二组（9 个，tunnel_policy.py:14）：

| # | 子路径 |
|---|--------|
| 1 | attachments |
| 2 | media |
| 3 | turns |
| 4 | memory |
| 5 | skills |
| 6 | tools |
| 7 | tool-settings |
| 8 | mbti |
| 9 | persona |

第三组（10 个，tunnel_policy.py:15）：

| # | 子路径 |
|---|--------|
| 1 | channels |
| 2 | cron |
| 3 | config |
| 4 | state |
| 5 | status |
| 6 | welcome |
| 7 | members |
| 8 | subagents |
| 9 | reload |
| 10 | acp |

正则主体允许影子 id 与普通 id 两种形态：`r"^/api/agents/" r"(?:bridge:[^/]+|[^/]+)"`（tunnel_policy.py:11-12），28 子路径均可再带子路径（`(?:/.*)?`）或精确匹配。

### 5.2 全部策略规则与方法矩阵（is_tunnel_path_allowed）

`verb` 缺省归一为 GET；path 去 query、补前导 `/`、去尾斜杠（根除外）（tunnel_policy.py:44-52）。

| 规则 | 路径形态 | 允许方法 | 行号 |
|------|----------|----------|------|
| `_AGENT_COLLECTION` | `^/api/agents/?$` | 仅 GET | :9、:54-55 |
| `_AGENT_RESOURCE` | `/api/agents/{id}` + 28 子路径 | GET、POST、PUT、PATCH、DELETE、HEAD | :66-67 |
| `_COMPOSER_READONLY` | providers/resolved、providers/active-model、knowledge-bases、knowledge-bases/capability（4 条，:21-28 逐行清点） | 仅 GET | :57-58 |
| `_BROWSER_VIEWER_GET` | `^/api/browser/(?:env-status|harness-sessions)$` | 仅 GET | :31、:60-61 |
| `_BROWSER_HANDOFF` | `^/api/browser/sessions/[^/]+/handoff$` | 仅 POST | :32、:63-64 |
| `_PLUGIN_AGENT` | `^/api/plugins/agents/{id}(?:/tools)?$` | GET、PATCH | :36、:69-70 |
| `_MBTI` | `^/api/mbti(?:/.*)?$` | GET、POST | :37、:72-73 |
| `_SUBAGENT_CATALOG` | `^/api/subagent-catalog(?:/.*)?$` | 仅 GET | :38、:75-76 |
| `_ACP_GLOBAL` | `^/api/acp(?:/[^/]+)?$` | GET、PUT、DELETE | :39、:78-79 |
| `_CRON_SETTINGS` | `^/api/cron/settings$` | 仅 GET | :40、:81-82 |
| `_CONNECTOR_INSTANCES_LIST` | `^/api/connector-instances$` | 仅 GET | :41、:84-85 |
| 兜底 | 其他一切路径（含全部 `/api/bridge/*` 管理面） | 拒绝（return False） | :87 |

来源：F-397、F-398。

### 5.3 SSRF：链路本地/元数据地址阻断（peer_auth.py）

```python
_BLOCKED_NETWORKS = (
    ipaddress.ip_network("169.254.0.0/16"),          # peer_auth.py:16（F-400）
    ipaddress.ip_network("fe80::/10"),               # peer_auth.py:17（F-400）
    ipaddress.ip_network("::ffff:169.254.0.0/112"),  # peer_auth.py:18（F-400）
)
```

`_host_resolves_blocked`：字面 IP 直接查网段；主机名经 `socket.getaddrinfo` 逐结果地址查网段，解析失败抛 BRIDGE_PEER_UNREACHABLE "peer host could not be resolved"（peer_auth.py:22-47）。`normalize_peer_base_url` 要求 scheme 仅 http/https（否则 "peer URL must be http or https"）、netloc 非空，命中阻断网段报 "peer URL host is not allowed (link-local / metadata addresses blocked)"，返回值去尾斜杠（peer_auth.py:50-65）（F-400）。

### 5.4 请求/响应头处理（http_tunnel.py）

入站隧道请求丢弃 6 个请求头（逐字清点，:19-28）：host、content-length、connection、transfer-encoding、authorization、cookie（F-399）。清洗后注入属主身份：`clean_headers["authorization"] = f"Bearer {access_token}"`（http_tunnel.py:83）。响应头白名单丢弃 4 个（:29-36）：content-length、transfer-encoding、connection、content-encoding（F-399）。

客户端构造字面（http_tunnel.py:88-92）：

```python
httpx.ASGITransport(app=app)
base_url="http://bridge.local"
timeout=120.0
```

路径不在白名单时抛 OctopError(BRIDGE_REMOTE_UNSUPPORTED, "This action is not available through the remote bridge. Manage it on the peer Octop.")（http_tunnel.py:73-77）。响应编码 `encode_tunnel_response` 含 status、headers、done=True，body 以 body_b64 传递（:46-59）。

来源：F-399、F-400。

## 6. 影子 ID 重写、图标 URL 与模块分工

### 6.1 重写方向

- **入站（peer-local id → 本地影子）**：`rewrite_peer_agent_id(cid, aid)` 把对端本地代理 id 映射为 `bridge:{cid}:{aid}`；已是 bridge: 形态的直接透传（ids.py:54-61）。`rewrite_tunneled_json` 递归遍历 dict/list，6 个标量身份键与 2 个列表键逐值映射，6 个 URL 键及含 `/api/agents/`、`/api/plugins/agents/` 的字符串走 `rewrite_agent_url_segment`；注释明确禁止子串裸替换（团队房间 id 为 `{room}~{member}`，会话键以 `{agent_id}:` 起始）（ids.py:148-191）。
- **反向（影子 → peer）**：`restore_peer_path_ids(rest, bridge_agent_id=..., remote_agent_id=...)` 把 hub 路径中嵌入的影子 id 替换回对端 id，使陈旧标签页仍可加载 `…/threads/{room}~bridge:cid:member/history`（ids.py:209-219）。
- 实时流帧由 `rewrite_peer_stream_frame` 统一改写说话者 id 与媒体 URL（ids.py:194-206）。

### 6.2 图标 URL 改写（icons.py）

`rewrite_remote_icon_url` 规则（F-401，:34-62）：

1. 空值 → None（UI 回落 icon_name）；
2. `/experts/` 前缀路径原样保留（:49，本地内置同款资源，query 保留）；
3. http(s) 外链解析 path 后，凡不以 `/api/agents/` 或 `/experts/` 开头者（CDN/SkillHub 头像）原样保留（:45）；
4. 以 `/avatar` 或 `/icon` 结尾的对端上传头像，改走本地 `bridge_avatar_api_path(bridge_agent_id)`（:53-56）；未设 bridge_agent_id 时返回 None（浏览器无法对对端鉴权）；
5. shadow experts 同步分支保留 `/experts/avatars` 与 CDN 前缀（manager.py:1043-1045）（F-392）。

### 6.3 模块分工

| 模块 | 职责 |
|------|------|
| ids.py | bridge: 影子 id 构造/解析、载荷与路径身份重写（F-394~F-396） |
| transport.py | 进程内 WS 会话、帧分发、tunnel Future 多路复用（F-401） |
| tunnel_policy.py | HTTP 隧道路径与方法白名单（F-397、F-398） |
| http_tunnel.py | ASGI 本地调用、请求/响应头清洗、owner Bearer 注入（F-399） |
| peer_auth.py | 对端登录、WS URL 拼装、链路本地网段 SSRF 阻断（F-400） |
| crypto.py | bridge_fernet 凭证/令牌加密（F-401） |
| icons.py | 对端头像与图标 URL 的本地化改写（F-401） |
| manager.py | 连接编排、握手、自动重连、影子 experts、turn/browser 隧道（F-384~F-393） |

## 7. 管理面 HTTP/WS 端点（api/routers/bridge.py）

以下端点均属本机管理面，**不在** HTTP 隧道白名单内（隧道仅允许第 5 节登记的 agent/composer/browser 等产品面路径）；其中代理类端点在对端落地后映射到对应隧道白名单规则。

| # | 方法 | 路径（装饰器行号） | 状态码 | 隧道白名单归属（对端落地路径） |
|---|------|--------------------|--------|--------------------------------|
| 1 | POST | `/bridge/probe`（:64） | — | 管理面，不入隧道 |
| 2 | POST | `/bridge/connections/{id}/probe`（:86-89） | — | 管理面，不入隧道 |
| 3 | GET | `/bridge/connections`（:110） | — | 管理面，不入隧道 |
| 4 | POST | `/bridge/connections`（:120） | 201 | 管理面，不入隧道 |
| 5 | GET | `/bridge/connections/{id}`（:140） | — | 管理面，不入隧道 |
| 6 | POST | `/bridge/connections/{id}/connect`（:151-154） | — | 管理面，不入隧道 |
| 7 | POST | `/bridge/connections/{id}/disconnect`（:165-168） | — | 管理面，不入隧道 |
| 8 | PATCH | `/bridge/connections/{id}`（:218-221） | — | 管理面，不入隧道 |
| 9 | DELETE | `/bridge/connections/{id}`（:262-266） | 204 | 管理面，不入隧道 |
| 10 | GET | `/bridge/connections/{id}/agents`（:276-279） | — | 对端 GET `/api/agents` → `_AGENT_COLLECTION` |
| 11 | GET | `/bridge/connections/{id}/providers/resolved`（:290-293） | — | `_COMPOSER_READONLY`（GET） |
| 12 | GET | `/bridge/connections/{id}/providers/active-model`（:305-308） | — | `_COMPOSER_READONLY`（GET） |
| 13 | GET | `/bridge/connections/{id}/knowledge-bases`（:322-325） | — | `_COMPOSER_READONLY`（GET） |
| 14 | GET | `/bridge/connections/{id}/knowledge-bases/capability`（:337-340） | — | `_COMPOSER_READONLY`（GET） |
| 15 | GET | `/bridge/connections/{id}/browser/env-status`（:354-357） | — | `_BROWSER_VIEWER_GET`（GET） |
| 16 | GET | `/bridge/connections/{id}/browser/harness-sessions`（:371-374） | — | `_BROWSER_VIEWER_GET`（GET） |
| 17 | POST | `/bridge/connections/{id}/browser/sessions/{session_id}/handoff`（:393-396） | — | `_BROWSER_HANDOFF`（POST） |
| 18 | WS | `/bridge/connections/{id}/browser-stream/ws`（:417） | — | 本机浏览器流 WS，不入 HTTP 白名单 |
| 19 | WS | `/bridge/ws`（:504） | — | 桥接主 WS（对端拨入），不入 HTTP 白名单 |

PATCH 体 `BridgePatchBody` 字段：auto_reconnect、display_name（max 64）、notes（max 500）、icon_name（max 64）、peer_base_url、peer_username、password（缺省保留旧密）（bridge.py:181-215）。

## 相关概念

- [/concepts/00-architecture.md](../concepts/00-architecture.md)
- [/concepts/05-acp-protocol.md](../concepts/05-acp-protocol.md)
- [/references/connectors-catalog.md](./connectors-catalog.md)
- [/references/server-launch.md](./server-launch.md)
