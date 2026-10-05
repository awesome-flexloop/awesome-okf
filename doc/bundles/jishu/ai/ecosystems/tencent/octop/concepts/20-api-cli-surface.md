---
type: Concept
title: "API 装配面与 CLI 22 命令新口径"
description: "v1.0.2b5 的 build_app 装配序列、60 条 router 挂载与 40 个 OpenAPI tag、472 HTTP+9 WS 计数口径、JWT 豁免表与 common 工具层；CLI 22 键注册表新口径及 REPL/support 嵌入式支撑结构。"
tags: [octop, api, fastapi, openapi, jwt, cli, click, repl, embedded]
generated: { by: "reference_agent/trae-cn", at: 2026-10-04T10:00:00+08:00 }
verified: { by: "process:grep-v", at: 2026-10-04T10:00:00+08:00 }
status: stable
stale_after: 2027-10-04
sources:
  - id: facts
    resource: /spec/facts.md
    title: Octop 源码事实清单 F-503~F-522、F-556~F-565（v1.0.2b5，commit e473dd3c）
  - id: apisurface
    resource: /references/api-surface.md
    title: HTTP API 挂载总表与端点计数 v1.0.2b5
  - id: cli
    resource: /references/cli-api.md
    title: CLI 与 HTTP API 信源（20 命令旧口径）
---

# API 装配面与 CLI 22 命令新口径

[06-cli-commands.md](06-cli-commands.md) 记录了 CLI 的 `_LazyCLI` 延迟加载原理、根选项与 Offline/Embedded/External 三层传输模型，本文不再重复。本文聚焦两件 v1.0.2b5 口径的事实：HTTP 侧 `build_app` 实际装配出的 API 面（挂载、tag、端点计数、鉴权豁免、common 层），以及 CLI 侧从 20 命令扩展到 **22 命令**后的新注册表，与 REPL/support 两个此前未展开的嵌入式支撑目录。端点明细以信源 [/references/api-surface.md](../references/api-surface.md) 为准，本文只讲口径与结构，不逐端点复述。

## build_app：一个工厂的装配序列

`build_app(server: OctopServer) -> FastAPI` 自身不初始化任何领域服务，`server` 由组合根 `launch.py` 预先构造好挂到 `app.state.octop_server`（F-503、F-507）。装配顺序（F-507~F-510）：

```
FastAPI(title="Octop API", version="0.1.0",
        openapi_url="/api/openapi.json" if enable_api_docs else None,
        openapi_tags=OPENAPI_TAGS)
  │
  ├─ configure_openapi(app)        # 注入 BearAuth（http/bearer/JWT）与全局 security
  ├─ 异常处理器                     # OctopError → to_envelope；Exception → INTERNAL_ERROR
  ├─ CORS（仅 cfg.cors_origins 非空；expose X-Octop-Access-Token）
  ├─ install_bridge_proxy          # ┐ Starlette 后加先执行：
  ├─ install_jwt_auth              # ┘ 实际顺序 setup_lockdown → jwt → bridge
  ├─ install_setup_lockdown
  ├─ bridge_manager.bind_asgi_app  # 存在桥接管理器时
  ├─ GET /.well-known/acme-challenge/{token}
  ├─ _mount_routers(...)           # 59 常挂 + mobile 条件 1
  ├─ GET /api/docs                 # enable_api_docs 时，Scalar 引用页
  └─ SPA fallback                  # enable_dashboard 且 dashboard/index.html 存在时
```

中间件安装顺序是 `install_bridge_proxy → install_jwt_auth → install_setup_lockdown`，源码注释逐字说明原因：「Bridge proxy must sit inside JWT auth so `request.state.octop_user` is set (Starlette runs the last-added middleware first).」——即实际请求经过的顺序是 setup lockdown → JWT → bridge proxy，桥代理因此能复用 JWT 中间件写入的用户身份（F-508）。

其余装配要点：FastAPI 自报 `version="0.1.0"`（与发行版 1.0.2b5 独立）；`enable_dashboard` 默认 True、`enable_api_docs` 默认 False；文档页 `GET /api/docs`（`include_in_schema=False`）返回 Scalar 的 `get_scalar_api_reference`；ACME challenge 端点读内存 `challenge_store`，缺失回 404（F-507、F-508）。SPA 兜底为 `GET /{full_path:path}`：`api/`、`ws/` 前缀直接 404，绝对路径与含 `..` 段拒绝 join，dashboard 目录取 `Path(__file__).parent.parent/"dashboard"`，`sw.js`/`manifest.json`/`index.html` 给 no-cache、`assets/` 给一年 immutable（F-509）。

## 60 条挂载与 40 个声明 tag

路由挂载经 frozen dataclass `_RouterMount(router, prefix, tags)` 描述，`_mount_routers` 循环体里只有一处 `app.include_router(spec.router, prefix=spec.prefix, tags=list(spec.tags))`。Grep `_RouterMount(` 在 `app.py` 实测 **60 命中 = 59 条常挂 + 1 条 mobile 条件挂载**（F-503）：

```python
enable_mobile = cfg.capabilities.mobile.enabled if cfg and cfg.capabilities.mobile.enabled else False
# 真值时追加：_RouterMount(mobile.router, "/api", ["mobile"])
```

即 mobile 的 5 HTTP + 2 WS 端点只有在主机能力开启时才出现在路由表中（F-506）。59 条常挂挂载的前缀分两组逐行列于 `app.py:216-280`（从 `/api`、`/api/auth`、`/api/users` 到 `/api/plugins`，F-504、F-505），完整逐行总表见 [/references/api-surface.md](../references/api-surface.md) §2，本文不复述。

OpenAPI 元信息里 `OPENAPI_TAGS` 实测 **40 个**声明 tag（Grep `"name":` 于 `openapi_meta.py`），从 setup/auth/health/users 到 ollama/onnx（F-511）。把 60 条挂载实际携带的 tag 与声明表逐项比对，有 **4 个「使用但未声明」tag**：`i18n`、`memory`、`proactive-care`、`plugins`——FastAPI 对未声明 tag 容忍透传，文档里它们会成组出现但缺少描述（信源 api-surface §2）。`configure_openapi` 还会给所有以 `/api/` 起始且不在豁免表内的 operation 自动补 `security=[{"BearerAuth": []}]`，并在 `API_DESCRIPTION` 中写明 WS 以 `?token=` 传 JWT、滑动续期响应头与 HITL resume 的 SSE 约定（F-512）。

## 472 HTTP + 9 WS：计数口径

端点数不是「数文件」，而是统一计数装饰器（F-523）：

| 指标 | 数值 | 口径 |
|---|---:|---|
| HTTP 装饰器 | **472** | Grep `@(router\|public_router\|admin_router\|user_router\|ws_router\|chat_router).(get\|post\|put\|delete\|patch\|head\|options\|trace)(` 于 `api/routers/` |
| WebSocket | **9** | Grep `.websocket(`：bridge 2、terminal 1、chat 2（chat/ws、notify_ws）、mobile 2、browser 1、desktop 1 |
| 合计 | 481 | 472 + 9 |
| routers 文件 | 81 | 顶层 54（含 `__init__`）+ chat 10 + browser 6 + desktop 6 + mobile 5 |

两个易踩的口径细节：其一，`memory.py` 还用 `router.add_api_route` 额外注册了 **5 个** terminal GET（about_me、current_focus、things_you_told_me、recent_stories、entities），不计入 472；其二，472 的分布为顶层 51 文件 430 + chat 20 + browser 12 + desktop 5 + mobile 5（F-523、F-527）。9 个 WS 的逐路径清单见 [/references/api-surface.md](../references/api-surface.md) §3.1。

## JWT：5 前缀 + 15 精确路径豁免

JWT 中间件只拦 `/api/` 起始且非豁免的路径，认证结果缓存到 `request.state.octop_user`，失败时**直接返回 JSONResponse**（注释逐字「Middleware returns directly (skips FastAPI exception handlers).」），响应阶段做滑动续期（剩余寿命不足 1/3、阈值常量 `_SLIDING_RENEW_REMAINING_FRACTION = 1/3` 时换新并写 `X-Octop-Access-Token` 头；原始 token 可从 Bearer 头或 `access_token` query 提取），安装以 `_octop_jwt_auth_installed` 属性保证幂等（F-515、F-516）。令牌本身是 HS256：payload 键 `sub`（int 转 str，解码再转回）、`uname`、`role`、`iat`、`exp`，默认 TTL 86400 秒（F-513）。

豁免判定函数 `is_jwt_exempt_path` **先精确匹配、后前缀匹配**（F-514）。5 个前缀：

```
/api/setup/                         /api/health/
/api/i18n/                          /api/connectors/oauth/callback
/api/internal/mcp/
```

15 个精确路径：`/api/health`、`/api/auth/login`、`/api/auth/captcha`、OIDC 4（status/start/callback/exchange）、OAuth 4（status/start/callback/exchange）、邀请 2（`/api/auth/invite/validate`、`/redeem`）、`/api/docs`、`/api/openapi.json`（F-514）。注意 JWT 豁免与 setup-lockdown 白名单是两套独立机制：前者免登录，后者仅在零用户首启期间放行向导端点。

## common/：12 个业务支撑模块

`api/common/` 实测 13 个 `.py`（含 `__init__`，即 12 个业务模块），为薄 router 提供跨文件复用（F-517）：

| 模块 | 职责要点 |
|---|---|
| `agent.py` | 7 个属主/存在性函数：`agent_is_shared`、`user_owns_agent`、`assert_agent_owner`、`assert_agent_access_row`、`require_agent_row`、`require_agent_owner_row`、`assert_agent_access`（F-520） |
| `memory_client.py` | `call_memory_rpc` 进程内构造 JSON-RPC 2.0 包同步调 `bridge.handle`；错误码 -32010→NOT_FOUND、-32602→400、-32601→unknown method；维护态 backing_up/deduplicating/compacting 抛 AGENT_BUSY；16 条缓存（F-521） |
| `upload_limit.py` | `read_upload_capped` 分块（1MiB）读取，超限抛 ATTACHMENT_TOO_LARGE（F-519） |
| `sso_cookie.py` / `public_base.py` | state cookie 三常量；`resolve_public_base` 信任首值 x-forwarded-*（F-518） |
| `workspace.py` | 8 个 def：require_running_agent/workspace 等（F-522） |
| `validators.py` / `attachments.py` / `content_disposition.py` | MCP/skills 校验、StoredAttachment、RFC 5987 头（F-522） |
| `agent_runtime.py` / `agent_workspace.py` / `usage_xlsx.py` | 运行时字段集、工作区解析、用量导出 xlsx（F-522） |

## CLI：22 键注册表新口径

`cli/registry.py` 的 `COMMANDS` dict 实测 **22 键**，值三元组仍是「模块路径 / 属性名 / 短 help」（F-556）。与旧文 20 命令相比，新增 **`memory`** 与 **`captcha`** 两个 group，逐字清单（按源码顺序）：

```
memory  init  run  service  config  user  agent  chats  channel  cron
provider  models  skills  admin  captcha  version  completion  update
clean  backup  acp  plugin
```

- `memory`（`.commands.memory`，help 逐字 "Live memory maintenance (backup and slim)."）：子命令 `list` 与 `slim`；slim 的 `--agent` 与 `--all` 互斥，`--all` 顺序瘦身所有符合条件的运行中 Agent（F-556、F-559）。
- `captcha`（`.commands.captcha`，help 逐字 "Login captcha maintenance (lockout escape hatch)."）：只有 `reset` 一个子命令，经 `open_cli_services()` 开本地库后 `settings_repo.delete(SETTINGS_KEY)`；docstring 明确「离线逃生只有此命令或恢复备份，启动环境 `OCTOP_CAPTCHA_*` 不受影响」（F-559）。
- `acp` 的属性名特殊，为 `acp_cmd`（其余键与属性同名）（F-556）。

`commands/` 目录 Glob 实测 **23 个 `.py` = `__init__.py` + 22 个命令模块**，与 22 键一一对应（F-558）。其余新口径细节：`backup create` 默认不含聊天（需显式 `--include-chats`）并有 5 个 `--no-*` 排除开关；`init` 有 5 个选项含 `--force`/`--yes`；`run --port` 用 `click.IntRange(0, 65535)`，注释强调是 0-65535 而非 1-65535；`admin rotate-jwt-secret` 直接走本地 DB 与 SecretRepo（F-560~F-562）。

## REPL 7 文件：嵌入式聊天运行时

`octop chats repl` 不是 HTTP 客户端，而是进程内的聊天运行时。`cli/repl/` 实测 **7 个 `.py`**（F-563）：

| 文件 | 职责 |
|---|---|
| `runtime.py` | 模块 docstring 逐字「Embedded OctopServer chat runtime via the CLI gateway channel.」；含 `CliChatSession` 与 `run_chat_turn_async` |
| `embedded_session.py` | `embedded_runtime`/`embedded_chat_server`：同一事件循环内**引用计数**复用嵌入式 OctopServer |
| `session.py` | `ReplSession` 会话状态 |
| `turn.py` | `ChatTurnResult` 单轮结果 |
| `toolbar.py` | `format_repl_toolbar`，基于 prompt_toolkit |
| `render.py` | `ChatTheme`、`ChunkRenderer`、`print_slash_help`、`print_welcome` |
| `__init__.py` | 包导出 |

引用计数的嵌入式 server 意味着：一个 REPL 进程里多轮对话只启动一次 OctopServer，退出时按引用关闭，不必为每条消息付启动成本（F-563）。

## support 13 文件：三种传输的共享支撑

`cli/support/` 实测 **13 个 `.py`**，把 Offline/Embedded/External 的公共脚手架从命令模块里抽离（F-564、F-565）：

| 模块 | 作用 |
|---|---|
| `db.py` | docstring「Offline DB access for CLI commands that only need local SQLite.」；`open_cli_services` 开库前先 `apply_env_file`+`load_config`+`open_database`+`run_migrations` 再 build_shared_services |
| `offline_ops.py` | 「Direct infra/DB helpers for local CLI (no HTTP, no login).」 |
| `embedded_ops.py` | 「Embedded OctopServer helpers for CLI ops that need a live runtime.」 |
| `skills.py` | 「Offline CLI helpers for per-agent skills (no HTTP / login).」 |
| `feishu_creator.py` | 本地拉起飞书 bot-creator 子进程（no HTTP） |
| `ctx.py` | `resolve_user`/`resolve_agent`/`json_output_enabled`/`require_agent`，默认值取根 ctx obj |
| `state.py` | `CLIState`/load/save 与 `default_state_path`（pinned user/agent） |
| `acting.py` | `resolve_cli_acting_user_id` 代理身份解析 |
| `prompts.py` | select/checkbox/text/password/confirm/editor 6 个提问函数 |
| `qr.py` | `render_qrcode_terminal` 终端二维码，附 URL fallback |
| `stub.py` | `EXIT_NOT_APPLICABLE = 2`；`not_applicable(...)` 打印「❌ Not applicable for Octop: …」后退出码 2 |
| `errors.py` | CLI 错误归一 |
| `__init__.py` | 包导出 |

这一层解释了旧文里「同一领域核心被 HTTP/CLI/ACP 复用」在代码上的落点：命令模块只负责参数解析与输出，开库、起服务、提问、二维码与不适用退出全部委托给 `support/`，而真正的业务规则仍在 `infra/`。

## 相关概念

- [/concepts/06-cli-commands.md](06-cli-commands.md)（20 命令旧口径：懒加载原理与三层传输）
- [/concepts/00-architecture.md](00-architecture.md)
- [/concepts/01-server-lifecycle.md](01-server-lifecycle.md)
- [/concepts/17-users-auth-security.md](17-users-auth-security.md)
- [/references/api-surface.md](../references/api-surface.md)
