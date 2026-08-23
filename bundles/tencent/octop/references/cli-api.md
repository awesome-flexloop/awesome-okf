---
type: Reference
title: "CLI 与 HTTP API：_LazyCLI、20 子命令、FastAPI 工厂"
description: "CLI 延迟加载机制、COMMANDS 注册表、20 个子命令、三层传输、octop run 选项、FastAPI build_app 工厂、50+ 路由挂载、异常处理与 Dashboard SPA。"
tags: [octop, cli, click, fastapi, api, uvicorn, spa]
generated: { by: "reference_agent/trae-cn", at: 2026-08-23T10:00:00+08:00 }
verified: { by: "process:grep-v", at: 2026-08-23T10:00:00+08:00 }
status: stable
stale_after: 2027-08-23
sources:
  - id: src
    resource: /spec/facts.md
    title: Octop 源码事实清单 F-108~F-120
---

# CLI 与 HTTP API

本信源登记 `src/octop/cli/` 和 `src/octop/api/app.py` 的全部可验证事实。

## CLI 入口（cli/main.py）

### _LazyCLI 延迟加载

```python
class _LazyCLI(click.Group):
    _registry: ClassVar[dict[str, tuple[str, str, str]]] = COMMANDS

    def list_commands(self, ctx):
        return sorted(self._registry)

    def get_command(self, ctx, name):
        module_path, attr, _help = self._registry[name]
        mod = importlib.import_module(module_path, package=__package__)
        return getattr(mod, attr)
```

关键设计（F-114）：
- 命令模块在**调用时**才通过 `importlib.import_module` 导入
- `list_commands` 和 `format_commands` 直接从 registry 元组读取，不导入模块
- `--help` 和 `--version` 几乎瞬时返回，不加载整个依赖树

### 根命令

```python
@click.group(cls=_LazyCLI)
@click.option("-v", "--version", is_flag=True, is_eager=True, callback=_print_version)
@click.option("--user", "as_user", envvar="OCTOP_USER")
@click.option("--agent", "agent_id", envvar="OCTOP_AGENT")
@click.option("--json", "json_out", is_flag=True)
@click.pass_context
def cli(ctx, as_user, agent_id, json_out): ...
```

全局选项（F-115）：
- `-v/--version`：打印版本并退出
- `--user`：默认操作用户（env `OCTOP_USER`）
- `--agent`：默认 Agent（env `OCTOP_AGENT`）
- `--json`：机器可读 JSON 输出

### UTF-8 强制

`_ensure_utf8_stdio()` 在非 UTF-8 环境（如 Windows GBK/cp936）下将 stdout/stderr 重配置为 UTF-8（`errors="replace"`），防止 emoji（✅/❌/QR art）导致 `UnicodeEncodeError`（F-117）。

## COMMANDS 注册表（cli/registry.py）

20 个子命令（F-116）：

| 命令 | 模块 | 属性 | 说明 |
|------|------|------|------|
| `init` | `.commands.init` | `init` | 引导安装 |
| `run` | `.commands.run` | `run` | 前台运行服务器 |
| `service` | `.commands.service` | `service` | 系统服务生命周期 |
| `config` | `.commands.config` | `config_group` | CLI 默认配置 |
| `user` | `.commands.user` | `user` | 用户管理 |
| `agent` | `.commands.agent` | `agent` | Agent 生命周期 |
| `chats` | `.commands.chats` | `chats` | 聊天 REPL 和会话管理 |
| `channel` | `.commands.channel` | `channel` | 通道管理 |
| `cron` | `.commands.cron` | `cron` | 定时任务管理 |
| `provider` | `.commands.provider` | `provider` | Provider 管理 |
| `models` | `.commands.models` | `models` | 模型目录和激活模型 |
| `skills` | `.commands.skills` | `skills` | 技能启用/禁用 |
| `admin` | `.commands.admin` | `admin` | 管理命令 |
| `version` | `.commands.version` | `version` | 显示版本 |
| `completion` | `.commands.completion` | `completion` | Shell 补全 |
| `update` | `.commands.update` | `update` | 检查更新 |
| `clean` | `.commands.clean` | `clean` | 清除 CLI 状态或擦除 ~/.octop |
| `backup` | `.commands.backup` | `backup` | 备份和恢复 |
| `acp` | `.commands.acp` | `acp` | ACP stdio 服务器 |
| `plugin` | `.commands.plugin` | `plugin` | 插件管理 |

每个条目的格式为 `(module_path, attr_name, short_help)`。

## octop run 命令（cli/commands/run.py）

### 选项

| 选项 | 类型 | 默认 | 说明 |
|------|------|------|------|
| `--host` | str | None | 覆盖绑定地址 |
| `--port` | int | None | 覆盖端口 |
| `--reload` | flag | False | uvicorn 自动重载（开发） |
| `--workers` | int | 1 | Worker 进程数 |
| `--log-level` | choice | None | critical/error/warning/info/debug/trace |
| `--ssl` | flag | False | 启用 HTTPS |
| `--ssl-certfile` | path | None | TLS 证书 |
| `--ssl-keyfile` | path | None | TLS 私钥 |

来源：F-118。

### Host/Port 优先级

```
CLI flags > ~/.octop/config.json > launch defaults
```

CLI 传入的 `--host`/`--port` 会**持久化**到 config.json（通过原子写入：temp file + `os.replace`）（F-118）。

### 自签名证书

`--ssl` 在无证书时自动生成（F-119）：
- RSA 2048 位密钥
- CN=`octop-self-signed`
- SAN=IP:127.0.0.1
- 有效期 365 天
- 存放于 `~/.octop/ssl/self_signed.crt` 和 `self_signed.key`

## CLI 三层传输

| 层 | 何时使用 | 需要登录 | 示例命令 |
|----|---------|---------|---------|
| **Offline** | 仅读写本地 ~/.octop SQLite | 否 | init, backup, plugin, agent list, chats CRUD, cron list, user *, admin overview, models presets/list/active |
| **Embedded** | 需要 harness/gateway 运行时；进程内启动 OctopServer | 否 | acp, chats repl, chats send, agent create/start/stop/reload, provider test, channel test, skills list |
| **External** | 直接与 OS/daemon 通信 | 否 | models ollama-*, channel QR bind, Feishu bot-creator |

来源：F-120。

## HTTP API（api/app.py）

### build_app 工厂

```python
def build_app(server: OctopServer) -> FastAPI:
    app = FastAPI(title="Octop API", version="0.1.0", ...)
    app.state.octop_server = server
    _install_exception_handlers(app)
    # CORS, JWT, setup lockdown middleware...
    # 50+ routers...
    # Dashboard SPA fallback...
    return app
```

关键设计（F-108）：
- `build_app` 接收已构造的 `OctopServer`，自身不做领域初始化
- `server` 挂载到 `app.state.octop_server`，路由通过 `Depends(get_server)` 获取
- API 版本固定为 "0.1.0"（与包版本 0.9.25 独立）

### 异常处理

| 异常 | 处理 |
|------|------|
| `OctopError` | 本地化 JSONResponse（5xx 记录原始英文日志到 ~/.octop/logs） |
| `Exception`（未处理） | 日志记录 + `INTERNAL_ERROR` 信封 |

来源：F-109。

### 中间件

1. **CORS**：仅当 `cors_origins` 非空时启用，暴露 `X-Octop-Access-Token` header
2. **JWT Auth**：`install_jwt_auth(app, server)`
3. **Setup Lockdown**：`install_setup_lockdown(app, server)` 在未完成 setup 时封锁非 setup 路由

### ACME Challenge

`GET /.well-known/acme-challenge/{token}` 端点支持 Let's Encrypt HTTP-01 验证（F-110）。

### 路由挂载（50+ 模块）

路由按功能分组挂载到 `/api` 前缀（F-111），主要分组：

| 前缀 | 路由模块 |
|------|---------|
| `/api` | setup, acp, slash, i18n, mbti, experts, workspace, search, update |
| `/api/auth` | auth, auth_oidc, invites (public) |
| `/api/users` | users, invites (admin) |
| `/api/agents` | agents, subagents, agent_files |
| `/api/health` | health |
| `/api/chat` | chat, uploads |
| `/api/channels` | channels |
| `/api/connectors` | connectors |
| `/api/cron` | cron |
| `/api/providers` | providers |
| `/api/admin` | admin, backup, observability, tls, security, providers admin, voice admin |
| `/api/knowledge` | knowledge_bases |
| `/api/memory` | memory, memory_portable |
| `/api/plugins` | plugins |
| `/api/browser` | browser |
| `/api/desktop` | desktop |
| `/api/ollama` | ollama_models |
| `/api/onnx` | onnx_models |
| `/api/voice` | voice |
| `/api/skill-packages` | skill_packages |
| `/api/skills` | skills |
| `/api/terminal` | terminal |
| `/api/filesystem` | filesystem |
| `/api/storage-backends` | storage_backends |
| `/api/proactive-care` | proactive_care |
| `/api/usage` | usage (+ admin) |
| `/api/settings` | settings |
| `/api/envs` | envs |
| `/api/internal-mcp` | internal_mcp |

### API 文档

使用 Scalar（`scalar-fastapi`）在 `enable_api_docs=True` 时挂载 `/api/docs`，OpenAPI schema 在 `/api/openapi.json`（F-112）。

### Dashboard SPA Fallback

`GET /{full_path:path}` catch-all 路由（F-113）：
- `/api/` 和 `/ws/` 开头返回 404
- 拒绝绝对路径和 `..` 遍历
- 静态文件从 `src/octop/dashboard/` 提供
- 缓存策略：
  - `assets/`（Vite content-hash）：`public, max-age=31536000, immutable`
  - `sw.js`、`manifest.json`、`index.html`：`no-cache`
  - 其他：不设置 Cache-Control

## 相关概念

- [/concepts/06-cli-commands.md](/concepts/06-cli-commands.md)
- [/concepts/05-acp-protocol.md](/concepts/05-acp-protocol.md)
- [/concepts/00-architecture.md](/concepts/00-architecture.md)
