---
type: Reference
title: "HTTP API 挂载总表与端点计数 v1.0.2b5"
description: "Octop 1.0.2b5 FastAPI 装配事实、60 条 router 挂载完整总表、472 HTTP/9 WS 端点计数对账、关键路由接口面、chat/browser 子包与 JWT 豁免清单的信源登记。"
tags: [octop, http-api, fastapi, routers, endpoints, openapi, jwt]
generated: { by: "reference_agent/trae-cn", at: 2026-10-04T10:00:00+08:00 }
verified: { by: "process:grep-v", at: 2026-10-04T10:00:00+08:00 }
status: stable
stale_after: 2027-10-04
sources:
  - id: facts
    resource: /spec/facts.md
    title: Octop 源码事实清单 F-503~F-555（v1.0.2b5，commit e473dd3c）
---

# HTTP API 挂载总表与端点计数 v1.0.2b5

本信源登记 `src/octop/api/` 的装配机制、全部 60 条 router 挂载、装饰器计数与鉴权豁免面。计数除标注 F 事实外，均为 2026-10-04 对源码工作树的 Grep/Glob 实测（下文简称「源码实测」），与 F-503~F-555 锚点一致。

## 1. 装配事实（`api/app.py` / `deps.py` / `openapi_meta.py` / `middleware/`）

### 1.1 build_app 装配序列

`build_app(server: OctopServer) -> FastAPI`（`app.py:101`）按序执行（F-503~F-510；源码实测）：

1. 读配置开关：`enable_dashboard`（默认 True）、`enable_api_docs`（默认 False）、`enable_mobile = cfg.capabilities.mobile.enabled ... else False`（F-506/F-507）。
2. `FastAPI(title="Octop API", version="0.1.0", description=API_DESCRIPTION, openapi_url="/api/openapi.json" if enable_api_docs else None, openapi_tags=OPENAPI_TAGS)`（F-507；注意 HTTP API 自报版本为 `0.1.0`，与发行版 `1.0.2b5` 不同）。
3. `configure_openapi(app)` 注入 `BearerAuth`（type=http、scheme=bearer、bearerFormat=JWT），并对所有以 `/api/` 起始且非 `is_jwt_exempt_path` 的 operation 补 `security=[{"BearerAuth": []}]`（F-512）。
4. `app.state.octop_server = server`；安装异常处理器（F-510）：`OctopError` → `exc.to_envelope(locale=resolve_request_locale(request))`（5xx 额外 log.error 原文）；未捕获 `Exception` → `INTERNAL_ERROR` envelope。
5. CORS 仅在 `cfg.cors_origins` 非空时加装：`allow_credentials=True`、methods/headers `["*"]`、`expose_headers=[ACCESS_TOKEN_RESPONSE_HEADER]`（F-510）。
6. 中间件安装顺序逐行：`install_bridge_proxy` → `install_jwt_auth` → `install_setup_lockdown`；注释逐字「Bridge proxy must sit inside JWT auth so ``request.state.octop_user`` is set (Starlette runs the last-added middleware first).」（F-508）。
7. `server.app_runtime.bridge_manager` 非空时调 `bridge_manager.bind_asgi_app(app)`（`app.py:140-141`，源码实测）。
8. `@app.get("/.well-known/acme-challenge/{token}", include_in_schema=False)`：读 TLS `challenge_store`，缺失抛 404 "challenge not found"（F-508）。
9. `_mount_routers` 挂载 59 条常挂 router；`enable_mobile` 真值时再挂 mobile 1 条（F-503/F-506）。
10. `enable_api_docs` 真值时挂 `GET /api/docs`（include_in_schema=False）返回 `get_scalar_api_reference(openapi_url=app.openapi_url, title="Octop API")`（F-507）。
11. `enable_dashboard` 且 `dashboard/index.html` 存在时挂 SPA 兜底（见 §1.3）。

### 1.2 挂载机制

- `_RouterMount` 为 `@dataclass(frozen=True)`，字段 `router: Any`、`prefix: str`、`tags: Sequence[str]`（`app.py:26-30`，F-503）。
- `_mount_routers` 循环体唯一 `include_router`：`app.include_router(spec.router, prefix=spec.prefix, tags=list(spec.tags))`；Grep `_RouterMount\(` 实测 **60 命中**，`include_router` 字面值仅 1 命中（F-503，源码实测复核）。
- mobile 条件块：`_RouterMount(mobile.router, "/api", ["mobile"])`（F-506）。

### 1.3 SPA fallback 与缓存策略

`@app.get("/{full_path:path}", include_in_schema=False)`（`app.py:306-324`，F-509）：

- `api/`、`ws/` 前缀直接 404；绝对路径或含 `..` 路径段回退 shell 但不 join；候选文件经 `relative_to(dashboard_dir.resolve())` 越界校验（F-509，源码实测）。
- dashboard 目录字面 `Path(__file__).parent.parent / "dashboard"`（F-509）。
- `_NO_CACHE_DASHBOARD_NAMES = frozenset({"sw.js", "manifest.json", "index.html"})` → `no-cache`；`assets/` 前缀 → `public, max-age=31536000, immutable`；缺失的 hash asset 必须 404 而非回退 index.html（docstring 说明旧 shell 升级场景，F-509，源码实测）。

### 1.4 三道中间件

| 中间件 | 文件 | 行为要点 | 信源 |
|---|---|---|---|
| bridge proxy | `middleware/bridge_proxy.py` | 拦截 `/api/agents/bridge:{cid}:{aid}` 与 `/api/plugins/agents/bridge:…`（正则兼容 `%3A` 编码），把影子请求经隧道代理到对端；幂等属性 `_octop_bridge_proxy_installed`（源码实测） | F-508、源码实测 |
| JWT auth | `middleware/jwt_auth.py` | 仅拦 `/api/` 起始且非豁免路径；认证结果缓存到 `request.state.octop_user`；失败直接回 JSONResponse（注释「Middleware returns directly (skips FastAPI exception handlers).」）；响应阶段 `maybe_sliding_renew_token`，换新写 `X-Octop-Access-Token`；幂等属性 `_octop_jwt_auth_installed` | F-516 |
| setup lockdown | `middleware/setup_lockdown.py` | 无用户期间非 setup/health 端点一律 `503 {"setup_required": true}`；开放前缀 `/api/setup/`、`/api/health/`，精确 `/api/health`，开启文档时另放 `/api/docs`、`/api/openapi.json` | 源码实测 |

### 1.5 JWT 与权限依赖

- `sign_token(secret, *, sub, uname, role, ttl_seconds=86400)`：`jwt.encode(payload, secret, algorithm="HS256")`，payload 键 `sub`（str 化 int）、`uname`、`role`、`iat`、`exp`；解码 `algorithms=["HS256"]` 后 sub 转回 int；异常类 `InvalidToken`、`TokenExpired(InvalidToken)`（F-513）。
- `ACCESS_TOKEN_RESPONSE_HEADER = "X-Octop-Access-Token"`、`_SLIDING_RENEW_REMAINING_FRACTION = 1 / 3`；`extract_raw_token` 接受 `Authorization: Bearer ` 头或 `access_token` query（WS 用，F-512/F-515）。
- `require_permission(key)` 对未知 key 抛 `RuntimeError(f"unknown permission key: {key}")`；`require_admin()` 校验 `user.is_admin`（F-515）。
- 全树 require_permission 键集合（Grep 实测）：channels、backup、knowledge_settings、admin_console、sso、envs、users、connectors、desktop、browser、terminal、captcha、onnx_models、security、tls、update（F-548）。

## 2. 60 挂载总表（逐行转录 `app.py:216-290`）

挂载前缀逐字取自 `_RouterMount(prefix=...)`；「装饰器」列为该 router 对象上的 HTTP 装饰器数（源码实测，多 router 共享文件时标注合计口径）。

| # | 挂载前缀 | router 符号 @ 文件 | tag | HTTP/WS | 鉴权与备注 |
|---:|---|---|---|---|---|
| 1 | `/api` | setup.router @ `routers/setup.py` | setup | 11 | `/api/setup/` 前缀在 JWT 豁免表且为 lockdown 白名单；11 端点见 §4（F-542） |
| 2 | `/api/auth` | auth.router @auth.py | auth | 8 | `/api/auth/login`、`/api/auth/captcha` 精确豁免，余 current_user（F-533） |
| 3 | `/api/auth` | auth_oidc.router @auth_oidc.py | auth | 7 | oidc status/start/callback/exchange 精确豁免；config 3 端点 require_permission("sso")（F-534） |
| 4 | `/api/auth` | auth_oauth.router @auth_oauth.py | auth | 9 | oauth status/start/callback/exchange 精确豁免；bind/unbind 需登录；providers 配置 3 个 require_sso（F-534） |
| 5 | `/api/auth/invite` | invites.public_router @invites.py | auth | 2 | POST `/validate`、`/redeem` 精确豁免（F-531） |
| 6 | `/api` | preferences.router @preferences.py | auth | 2 | GET/PATCH `/preferences`，current_user（实测路径） |
| 7 | `/api` | i18n.router @i18n.py | i18n | 2 | `/api/i18n/` 前缀豁免（F-514） |
| 8 | `/api/health` | health.router @health.py | health | 1 | GET ``（summary "Health check"），精确+前缀双豁免（F-544） |
| 9 | `/api/users/invites` | invites.admin_router @invites.py | users | 3 | 列表/创建(201)/revoke，均 require_permission("users")（F-531） |
| 10 | `/api/users/roles` | user_roles.router @user_roles.py | users | 7 | 全部 require_permission("users")，含 3 个 avatar 端点（F-530） |
| 11 | `/api/users` | users.router @users.py | users | 12 | 用户 CRUD/头像/凭据 |
| 12 | `/api/agents` | agents.router @agents.py | agents | 13 | CRUD/avatar/start/stop/reload/read/status（F-548） |
| 13 | `/api` | agent_tools.router @agent_tools.py | agents | 3 | router 自带 `prefix="/agents"`（F-524） |
| 14 | `/api` | acp.router @acp.py | agents | 11 | 全局 5 个 require_admin；agent 面 6 个（F-547） |
| 15 | `/api` | chat.router @routers/chat/（聚合 5 子 router） | chat | 20 + 2 WS | 见 §5；WS 经 `?token=` 传 JWT（F-512/F-549） |
| 16 | `/api` | slash.router @slash.py | slash | 1 | GET `/slash/commands` |
| 17 | `/api` | connectors.router @connectors.py | connectors | 27 | `/api/connectors/oauth/callback` 前缀豁免（F-535） |
| 18 | `/api` | bridge.router @bridge.py | bridge | 17 + 2 WS | 全部 current_user，按 owner_user_id 取连接（F-525/F-526） |
| 19 | `/api` | knowledge_bases.router @knowledge_bases.py | knowledge | 26 | router 自带 `prefix="/knowledge-bases"`（F-524） |
| 20 | `/api` | internal_mcp.router @internal_mcp.py | internal-mcp | 3 | `/api/internal/mcp/` 前缀豁免；tag 描述「used by harness agents (no dashboard auth)」（实测） |
| 21 | `/api` | channels.router @channels.py | channels | 21 | 路径面 `/agents/{agent_id}/channels*`（实测） |
| 22 | `/api` | cron.router @cron.py | cron | 8 | 全部 current_user（F-539） |
| 23 | `/api` | settings.router @settings.py | settings | 5 | captcha GET/PUT 需 require_permission("captcha")（F-541） |
| 24 | `/api` | envs.router @envs.py | envs | 3 | router 自带 `prefix="/envs"`（F-524） |
| 25 | `/api` | search.router @search.py | search | 1 | router 自带 `prefix="/search"`（F-524） |
| 26 | `/api/providers` | providers.router @providers.py | providers | 15 合计 | 文件含用户 router + admin_router，15 装饰器为两者合计（F-524） |
| 27 | `/api/voice` | voice.router（用户）@voice.py | voice | 6 | presets/providers/active/stt/tts（F-532） |
| 28 | `/api/admin` | admin.router @admin.py | admin | 3 | GET `/overview`、`/audit-log`、`/metrics`（实测） |
| 29 | `/api/admin` | backup.router @backup.py | admin | 11 | 全部 require_permission("backup")（F-537） |
| 30 | `/api/admin/providers` | providers.admin_router @providers.py | admin | （含#26） | 模型供应商管理面 |
| 31 | `/api/admin/voice/providers` | voice.admin_router @voice.py | admin | 6 | CRUD(201/204)/test/test-configuration（F-532） |
| 32 | `/api/admin/observability` | observability.router @observability.py | observability | 3 | GET/PUT `/langfuse`、POST `/langfuse/test`（实测） |
| 33 | `/api/admin/media-generation` | media_generation.router @media_generation.py | providers | 4 | `/presets`、GET/PUT ``、POST `/test`；全 require_permission("providers")（实测） |
| 34 | `/api/admin/tls` | tls.router @tls.py | tls | 3 | 全 require_permission("tls")：status/preflight/issue（F-538） |
| 35 | `/api/admin/security` | security.router @security.py | security | 7 | 全 require_permission("security")（F-540） |
| 36 | `/api/admin/storage-backends` | storage_backends.admin_router @storage_backends.py | admin | 8 合计 | 文件含 admin/user 双 router，8 装饰器合计 |
| 37 | `/api/storage-backends` | storage_backends.user_router @storage_backends.py | storage-backends | （含#36） | 用户可见存储后端 |
| 38 | `/api/filesystem` | filesystem.router @filesystem.py | filesystem | 8 | 主机目录浏览 |
| 39 | `/api` | mbti.router @mbti.py | mbti | 7 | router 自带 `prefix="/mbti"`（F-544） |
| 40 | `/api` | experts.router @experts.py | experts | 13 | `/experts/published*` 等发布专家面（实测） |
| 41 | `/api` | teams.router @teams.py | teams | 6 | `/teams*`（F-536） |
| 42 | `/api` | workspace.router @workspace.py | workspace | 15 | `/agents/{agent_id}/workspace/*`（实测） |
| 43 | `/api` | agent_files.router @agent_files.py | agent_files | 5 | `/agents/{id}/heartbeat-config`、`/agents/{id}/memory/daily*`（实测） |
| 44 | `/api/memory` | memory.router @memory.py | memory | 22 + 5 add_api_route | 装饰器外另注册 5 个 terminal GET；docstring「The router itself contains no business logic」（F-527） |
| 45 | `/api/memory` | memory_portable.router @memory_portable.py | memory | 4 | `.hmpkg` 跨主机迁移（F-529） |
| 46 | `/api` | proactive_care.router @proactive_care.py | proactive-care | 2 | GET/PUT `/agents/{agent_id}/proactive-care`（实测） |
| 47 | `/api/usage` | usage.router（用户）@usage.py | usage | 4 合计 | 文件含用户 router 与 admin_router |
| 48 | `/api/admin` | usage.admin_router @usage.py | admin | （含#47） | 管理用量面 |
| 49 | `/api` | skill_packages.router @skill_packages.py | skill-packages | 15 | router 自带 `prefix="/skill-packages"`（F-524） |
| 50 | `/api` | skills.router @skills.py | skills | 18 | `/agents/{agent_id}/skills*` 等（实测） |
| 51 | `/api` | subagents.router @subagents.py | subagents | 5 | `/subagent-catalog*`、`/agents/{id}/subagents`（实测） |
| 52 | `/api` | terminal.router @terminal.py | terminal | 1 + 1 WS | GET context 需 require_permission("terminal")（F-546） |
| 53 | `/api` | uploads.router @uploads.py | chat | 1 | POST `/agents/{agent_id}/upload`（实测；tag=chat，非挂 `/api/chat`） |
| 54 | `/api` | update.router @update.py | update | 6 | router 自带 `prefix="/update"`；后 5 个 require_permission("update")（F-545） |
| 55 | `/api` | browser.router @routers/browser/（聚合 5 子 router） | browser | 12 + 1 WS | env/install 需 require_permission("browser")（F-554/F-555） |
| 56 | `/api` | desktop.router @routers/desktop/（聚合 5 子 router） | desktop | 5 + 1 WS | 5 个 HTTP 处理器全部 require_permission("desktop")（F-555） |
| 57 | `/api/ollama` | ollama_models.router @ollama_models.py | ollama | 7 | router 自带 `prefix="/ollama-models"`（F-524） |
| 58 | `/api/onnx` | onnx_models.router @onnx_models.py | onnx | 8 | 全部 require_permission("onnx_models")（F-543） |
| 59 | `/api/plugins` | plugins.router @plugins.py | plugins | 14 | router 自带 `prefix="/plugins"`（F-524） |
| 60 | `/api` | mobile.router @routers/mobile/（聚合 4 子 router） | mobile | 5 + 2 WS | **条件挂载**：仅 `cfg.capabilities.mobile.enabled` 为真（F-506/F-555） |

前缀对账说明（源码实测）：

- F-504/F-505 的分组表述中「`/api/chat`(uploads)」「`/api/skill-packages`」等系按业务路径归类；`app.py` 中 uploads、skill_packages、mbti、update、knowledge_bases、agent_tools、envs、search、ollama/onnx/plugins 等的**挂载前缀逐字为 `/api` 或专用父前缀**，完整路径由 router 自带 prefix（F-524）或装饰器路径拼接，本表以 `app.py` 为准。
- 60 条挂载共出现 44 个 tag 取值；`openapi_meta.py` 的 `OPENAPI_TAGS` 声明 40 个（Grep `"name":` = 40，F-511），其中挂载实际使用了全部 40 个；另有 4 个挂载 tag 未在 OPENAPI_TAGS 声明：`i18n`（#7）、`memory`（#44/#45）、`proactive-care`（#46）、`plugins`（#59）（源码实测逐项比对，FastAPI 对未声明 tag 容忍透传）。

## 3. 计数对账表

| 指标 | 数值 | 计数方式（2026-10-04 源码实测） | 信源 |
|---|---:|---|---|
| `_RouterMount(` 命中 | 60 | Grep `_RouterMount\(` 于 `api/app.py`：59 常挂 + mobile 条件块 1 | F-503 |
| `include_router` 字面值 | 1 | 仅 `_mount_routers` 循环体内 1 处 | F-503 |
| HTTP 路由装饰器 | **472** | Grep `@(router\|public_router\|admin_router\|user_router\|ws_router\|chat_router)\.(get\|post\|put\|delete\|patch\|head\|options\|trace)\(` 于 `api/routers/`：顶层 51 文件 430 + chat 20 + browser 12 + desktop 5 + mobile 5 | F-523 |
| WebSocket 装饰器 | **9** | Grep `\.websocket\(` 于 `api/routers/`：bridge 2、terminal 1、chat 2、mobile 2、browser 1、desktop 1 | F-523 |
| 端点合计 | 481 | 472 HTTP + 9 WS | F-523 |
| OpenAPI tag | 40 | Grep `"name":` 于 `openapi_meta.py` | F-511 |
| routers Python 文件 | 81 | Glob `api/routers/**/*.py`：顶层 54（含 `__init__`）+ chat 10 + browser 6 + desktop 6 + mobile 5 | F-523 |
| `APIRouter(` 行 | 79 | Grep 于 routers/（F-524） | F-524 |
| memory 额外 `add_api_route` | 5 | terminal/about_me、current_focus、things_you_told_me、recent_stories、entities（`memory.py:732-756`，实测，不计入 472） | F-527 |

### 3.1 9 个 WebSocket 端点清单

| WS 路径（装饰器逐字） | 文件:行 |
|---|---|
| `/bridge/connections/{connection_id}/browser-stream/ws` | bridge.py:417 |
| `/bridge/ws` | bridge.py:504 |
| `/agents/{agent_id}/terminal/ws` | terminal.py:500 |
| `/agents/{agent_id}/chat/ws` | chat/ws.py:33 |
| `/notifications/ws` | chat/notify_ws.py:23 |
| `/mobile/adb/shell/ws` | mobile/shell_ws.py:52 |
| `/mobile-stream/ws` | mobile/stream.py:501 |
| `/browser-stream/ws` | browser/stream.py:335 |
| `/desktop-stream/ws` | desktop/stream.py:235 |

### 3.2 顶层 51 个 router 文件装饰器分布（实测 430）

connectors 27、knowledge_bases 26、memory 22、channels 21、skills 18、bridge 17、providers 15、skill_packages 15、workspace 15、plugins 14、agents 13、experts 13、users 12、voice 12、acp 11、backup 11、setup 11、auth_oauth 9、auth 8、cron 8、filesystem 8、onnx_models 8、storage_backends 8、auth_oidc 7、mbti 7、ollama_models 7、security 7、user_roles 7、teams 6、update 6、agent_files 5、invites 5、settings 5、subagents 5、media_generation 4、memory_portable 4、usage 4、admin 3、agent_tools 3、envs 3、internal_mcp 3、observability 3、tls 3、i18n 2、preferences 2、proactive_care 2、health 1、search 1、slash 1、terminal 1、uploads 1。

## 4. 关键路由接口面

| router | 端点数 | 接口面（路径/鉴权逐字摘要） | 信源 |
|---|---:|---|---|
| bridge | 17 HTTP + 2 WS | POST `/bridge/probe`、`/bridge/connections/{id}/probe`；GET/POST `/bridge/connections`；GET `/bridge/connections/{id}`；POST `.../connect`、`.../disconnect`；PATCH/DELETE `.../{id}`；GET `.../agents`；隧道代理 GET `.../providers/resolved`、`.../providers/active-model`、`.../knowledge-bases`、`.../knowledge-bases/capability`、`.../browser/env-status`、`.../browser/harness-sessions`，POST `.../browser/sessions/{session_id}/handoff`；WS browser-stream（query token 缺失 close 4001，默认 1280x800）与 `/bridge/ws` | F-525、F-526 |
| memory | 22 + 5 | POST `/agents/{agent_id}/memory/{atoms,raw_events,entities,episodes,journal,candidates}/list`；GET 单资源；POST `candidates/{id}:promote`/`:reject`、`atoms/{id}:deprecate`、`/atoms`、`atoms/{id}:replace`；GET/PUT `/extract-config`；5 个 terminal GET 走 add_api_route；`_EXTRACT_DEFAULTS`（memory_enabled=True、idle 300s、interval 21600s），护栏 60s/300s/7d，PUT mode 仅 `idle`/`interval` | F-527、F-528 |
| memory_portable | 4 | GET `/memory/portable/sources`、POST `.../portable/pack`（`.hmpkg` 下载）、`.../portable/adopt`、`.../portable/doctor`；docstring「Portable pack/adopt is a SQLite-file mechanism; PostgreSQL memory has a…」 | F-529 |
| user_roles | 7 | GET/POST ``（创建 201）、PATCH/DELETE `/{user_role_id}`（DELETE 204）、POST/GET/DELETE `/{user_role_id}/avatar`；全 require_permission("users") | F-530 |
| invites | 3 + 2 | admin_router：GET ``、POST `` 201、POST `/{invite_id}/revoke`；public_router：POST `/validate`、`/redeem` | F-531 |
| voice | 6 + 6 | 用户：GET `/presets`、`/providers`、`/active`，PUT `/active`，POST `/stt`、`/tts`；admin：CRUD + `/{id}/test` + `/test-configuration` | F-532 |
| auth | 8 | GET `/captcha`（零用户抛 SETUP_REQUIRED）、POST `/login`、POST `/logout` 204、GET `/me`、POST `/change-password` 204、PATCH `/me`、POST/DELETE `/me/avatar`（201/204） | F-533 |
| auth_oidc / auth_oauth | 7 / 9 | oidc：status/start/callback/exchange + config GET/PUT/test；oauth：status/start/callback/exchange + bind/start、unbind、providers `{kind}` GET/PUT/test | F-534 |
| connectors | 27 | `/connectors/catalog`、`/connectors/weknora/detect-local`、`/connector-instances` CRUD + test/refresh、`/connectors/custom-mcp` GET/PUT + test、`/test-credentials`、`/connectors/auth/{kind}/info`、`/authorize-url`、`/exchange-code`、`/oauth/start`、legacy `/oauth/{kind}/start`、GET `/oauth/callback`（豁免）、`/oauth/pending/{state_id}` | F-535 |
| teams | 6 | GET/POST `/teams`、GET `/teams/template`、GET/PATCH/DELETE `/teams/{team_id}`（204） | F-536 |
| backup | 11 | list/status/auto GET、auto PUT、auto/run、create、files/{filename} GET(FileResponse)/restore/DELETE(204)、export（FileResponse）、import；全 require_permission("backup") | F-537 |
| tls | 3 | GET `/status`、POST `/preflight`、POST `/issue`（summary "Start Let's Encrypt HTTP-01 issuance"） | F-538 |
| cron | 8 | GET `/cron/settings`、GET `/agents/{agent_id}/cron/examples`、GET/POST `/agents/{agent_id}/cron`、GET/PATCH/DELETE `.../{cron_id}`、POST `.../run-now` 204 | F-539 |
| security | 7 | GET/PUT ``、GET `/tool-guard/rules`、GET/PUT `/tool-guard/rules/raw`、POST `/tool-guard/rules/reset`、GET `/defaults` | F-540 |
| settings | 5 | GET `/settings/timezone`、`/settings/upload`（max_upload_mb/max_upload_bytes）、`/settings/capabilities`（backend 字面 "physical, redroid, emulator, or none"）、GET/PUT `/settings/captcha`（active/available/providers/source/v3_min_score） | F-541 |
| setup | 11 | presets、validate-token、status、test-database、database、begin、verify-password、initial-admin(201)、resume-wizard、test-provider、finish；整前缀豁免 | F-542 |
| onnx_models | 8 | catalog、models/{model_name:path}/meta、status、PUT config、test、download、download-status、DELETE local/{model_name:path}；全 require_permission("onnx_models") | F-543 |
| mbti / health | 7 / 1 | mbti：current、types、types/{code}、preview/{code}、test/questions、test/submit、apply；health：GET `` | F-544 |
| update | 6 | GET `/status`（current_user）、POST `/check`、PATCH `/settings`、POST `/upgrade`、GET `/progress`、POST `/restart`；后 5 个 require_permission("update") | F-545 |
| terminal | 1 + 1 WS | GET `/agents/{agent_id}/terminal/context`（require_permission("terminal")）与 WS `/agents/{agent_id}/terminal/ws` | F-546 |
| acp | 11 | 全局 5 个（GET/PUT `/acp`、GET/PUT/DELETE `/acp/{runner_name}`，require_admin）；agent 面 6 个（`/agents/{agent_id}/acp*`） | F-547 |
| agents | 13 | GET ``、POST `` 201、POST `/{id}/read` 204、GET/PATCH/DELETE `/{id}`、avatar POST/GET/DELETE、start/stop/reload 204、GET `/{id}/status` | F-548 |

## 5. chat 子包与 browser/desktop/mobile 子包

### 5.1 chat 聚合包（10 文件，20 HTTP + 2 WS）

`chat/__init__.py` 用裸 APIRouter 依次 include 五个子 router：routes、history、trajectory、ws、notify_ws（F-549，源码实测）。模块分工：

| 文件 | 职责 | 信源 |
|---|---|---|
| `routes.py` | 3 HTTP：GET `/agents/{agent_id}/chat/welcome`、POST `/agents/{agent_id}/chat/hitl/resume`（summary "Resume HITL approval (SSE)"）、POST `/agents/{agent_id}/chat/polish` | F-550 |
| `sse.py` | `format_sse(event, data)` 输出 `event: {event}\ndata: {payload}\n\n`；resume 流发 event="chunk" 的 `{"type":"done"}` 与错误帧 | F-550 |
| `turn.py` | 轮次准备（docstring 逐字「Dashboard turn preparation (thread, MCP, skills, InboundMessage).」，构造 `build_dashboard_inbound`，源码实测） | 源码实测 |
| `ws.py` | WS `/agents/{agent_id}/chat/ws`；含本地与 bridge 两套处理路径（bridge 路径 cancel 回 "cancel not supported on bridge yet"） | F-551 |
| `models.py` | pydantic 帧/体模型（见下） | F-552 |
| `history.py` | 12 HTTP：threads 列表/创建/改名/删除、history、context-usage、read(204)、fork(201)、PATCH session、history/export、history-migration status/start | F-553 |
| `trajectory.py` | 5 HTTP（trajectory ledger 查询，239-366 行多行装饰器） | F-553 |
| `notify_ws.py` | WS `/notifications/ws`，回 pong 帧；承载 dashboard_push（cron 提醒/主动关怀，F-512） | F-553 |
| `serialize.py` | 线程历史加载与 LangGraph 消息序列化（docstring「Thread history loading and LangGraph message serialization.」，源码实测） | 源码实测 |

WS/SSE 事件类型面：入站 `user_turn`、`ping`、`subscribe`、`cancel`（subscribe/cancel 需带 thread_id，缺失回 error 帧）；出站 `pong`、`turn_status`、`error`、`done`（F-551）。`API_DESCRIPTION` 另声明入站帧 `{"type":"user_turn", ...}`、结束帧 `{"type":"done"}`/`{"type":"error",...}`、dashboard_push 走 `/api/notifications/ws`、HITL resume 走 `POST /api/agents/{agent_id}/chat/hitl/resume`（SSE）（F-512）。

`UserTurnWsFrame` 字段：type Literal["user_turn","ping"]、text、session_key、thread_id、model、default_model、reasoning_mode Literal["auto","enabled","disabled"]、reasoning_effort、conversation_mode Literal["ask","plan","craft"]、hitl_policy、mcp_servers、knowledge_base_ids、skills、messages、target_agent_ids；同文件另有 ChatTurnBody、PolishBody、RebindSessionBody、ForkThreadBody、RenameThreadBody、HitlResumeBody（decisions 例 approve/reject/respond）（F-552）。

### 5.2 browser / desktop / mobile 子包

| 子包 | 文件数 | 聚合子 router（实测 include 顺序） | 端点 |
|---|---:|---|---|
| browser | 6 | env → harness → record_replay → stream → uninstall（`__init__.py` 实测） | 12 HTTP + 1 WS（stream.py `/browser-stream/ws`）（F-555） |
| desktop | 6 | status → settings → install → uninstall → stream | 5 HTTP + 1 WS；5 个 HTTP 全 require_permission("desktop")（settings 2、install/status/uninstall 各 1）（F-555） |
| mobile | 5 | status → install → stream → shell_ws | 5 HTTP（status 4、install 1）+ 2 WS（shell_ws、stream）（F-555） |

browser/env 面（F-554）：

- GET `/browser/env-status`（current_user）返回键：playwright、browsers_ok、harness_browser、playwright_chromium、chrome_path、chrome_source（注释取值 `"system" | "playwright"`）、error。
- POST `/browser/install`（require_permission("browser")）返回 `text/event-stream`，事件行 `data: {"log":...}`、`{"done": true, "success": true}`，响应头含 `X-Accel-Buffering: no`。

## 6. JWT 豁免清单与 common/ 工具模块

### 6.1 JWT 豁免（`deps.py:66-89`，逐字转录）

5 个前缀（`_JWT_EXEMPT_PREFIXES`，按 startswith 判定）：

1. `/api/setup/`
2. `/api/health/`
3. `/api/i18n/`
4. `/api/connectors/oauth/callback`
5. `/api/internal/mcp/`

15 个精确路径（`_JWT_EXEMPT_EXACT`，逐字顺序）：

| # | 路径 | # | 路径 |
|---:|---|---:|---|
| 1 | `/api/health` | 9 | `/api/auth/oauth/start` |
| 2 | `/api/auth/login` | 10 | `/api/auth/oauth/callback` |
| 3 | `/api/auth/captcha` | 11 | `/api/auth/oauth/exchange` |
| 4 | `/api/auth/oidc/status` | 12 | `/api/auth/invite/validate` |
| 5 | `/api/auth/oidc/start` | 13 | `/api/auth/invite/redeem` |
| 6 | `/api/auth/oidc/callback` | 14 | `/api/docs` |
| 7 | `/api/auth/oidc/exchange` | 15 | `/api/openapi.json` |
| 8 | `/api/auth/oauth/status` | | |

`is_jwt_exempt_path(path)` 先精确匹配后前缀匹配（F-514，源码实测）。注意豁免仅作用于 JWT 中间件；setup lockdown 另有独立白名单（§1.4）。

### 6.2 `api/common/` 13 个模块

| 模块 | 实测面 | 信源 |
|---|---|---|
| `agent.py` | 7 个属主/存在性函数：`agent_is_shared`、`user_owns_agent`、`assert_agent_owner`、`assert_agent_access_row`、`require_agent_row`、`require_agent_owner_row`、`assert_agent_access` | F-520 |
| `agent_runtime.py` | 定义 `AgentRuntimeFields` | F-522 |
| `agent_workspace.py` | agent 工作区目录解析（chat/serialize.py 导入 `resolve_agent_workspace_dir`，实测） | F-522 |
| `attachments.py` | `StoredAttachment` dataclass、`save_attachment` | F-522 |
| `content_disposition.py` | RFC 5987 latin-1 安全头（`content_disposition` 函数 :23） | F-522 |
| `memory_client.py` | `call_memory_rpc`：进程内构造 `{"jsonrpc":"2.0","id":1,...}` 同步调 `bridge.handle(payload)`；错误码 -32010→NOT_FOUND、-32602→400、-32601→"unknown memory dashboard method"；维护态 backing_up/deduplicating/compacting 抛 AGENT_BUSY；`_MAX_CACHED = 16` 的 `_MemoryCache` 全局 `_CACHE` | F-521 |
| `public_base.py` | `resolve_public_base` 信任首值 `x-forwarded-proto`/`x-forwarded-host`，否则回当前 URL origin | F-518 |
| `sso_cookie.py` | `SSO_STATE_COOKIE="octop_sso_state"`、`SSO_COOKIE_PATH="/api/auth"`、`SSO_STATE_TTL_SECONDS=600`；httponly=True、samesite="lax"、secure 随 https | F-518 |
| `upload_limit.py` | `read_upload_capped`：`_DEFAULT_CHUNK=1024*1024`，超限抛 `_too_large`，错误码 `ATTACHMENT_TOO_LARGE`，报文 `f"file too large (max {max_mb}MB)"` | F-519 |
| `usage_xlsx.py` | `build_usage_xlsx`（:329）；颜色常量 `_COLOR_INPUT="4F6EF7"`、`_COLOR_OUTPUT="A06EF7"` | F-522 |
| `validators.py` | `assert_user_backend_root_dirs`、`validate_chat_mcp_servers`、`validate_chat_skills` | F-522 |
| `workspace.py` | 8 个 def：`require_running_agent`、`require_running_workspace`、`require_agent_workspace`、`workspace_api_path` 等 | F-522 |
| `__init__.py` | 包初始化（Glob 实测共 13 文件，F-517 记 12 个非 `__init__` 模块） | F-517 |

## 相关文档

- [/concepts/00-architecture.md](../concepts/00-architecture.md)
- [/concepts/01-server-lifecycle.md](../concepts/01-server-lifecycle.md)
- [/concepts/03-gateway-channels.md](../concepts/03-gateway-channels.md)
- [/concepts/05-acp-protocol.md](../concepts/05-acp-protocol.md)
- [/concepts/06-cli-commands.md](../concepts/06-cli-commands.md)
- [服务器启动与组合根](server-launch.md)
- [Octop v1.0.2b5 源码地图与构建清单](source-v1-map.md)
- [CLI 命令与 API 信源](cli-api.md)
- [Gateway 信源](gateway.md)
