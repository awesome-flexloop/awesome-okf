---
type: Concept
title: "CLI 命令体系：_LazyCLI、20 子命令与三层传输"
description: "Click CLI 延迟加载机制、COMMANDS 注册表 20 个子命令、Offline/Embedded/External 三层传输模型、octop run 启动选项、CLI 状态文件。"
tags: [octop, cli, click, lazy-loading, commands, transport]
generated: { by: "reference_agent/trae-cn", at: 2026-08-23T10:00:00+08:00 }
verified: { by: "process:grep-v", at: 2026-08-23T10:00:00+08:00 }
status: stable
stale_after: 2027-08-23
sources:
  - id: src
    resource: /references/cli-api.md
    title: CLI 与 HTTP API 信源
---

# CLI 命令体系

Octop 的 CLI 基于 Click 构建，采用延迟加载（lazy loading）机制，注册了 20 个子命令，并根据操作语义选择三种传输层之一。

## _LazyCLI 延迟加载

```python
class _LazyCLI(click.Group):
    _registry: ClassVar[dict[str, tuple[str, str, str]]] = COMMANDS

    def list_commands(self, ctx):
        return sorted(self._registry)

    def get_command(self, ctx, name):
        module_path, attr, _help = self._registry[name]
        mod = importlib.import_module(module_path, package=__package__)
        return getattr(mod, attr)

    def format_commands(self, ctx, formatter):
        rows = [(name, self._registry[name][2]) for name in self.list_commands(ctx)]
        with formatter.section("Commands"):
            formatter.write_dl(rows)
```

关键设计（F-114、I-04）：

1. **命令模块在调用时才导入**：`get_command` 通过 `importlib.import_module` 按需加载，`octop --help` 和 `octop version` 几乎瞬时返回
2. **帮助文本不触发导入**：`format_commands` 直接从 registry 元组的第三个元素读取短帮助，不需要导入命令模块
3. **registry 是类变量**：`_registry` 类型为 `ClassVar`，所有实例共享同一份命令表

每个 registry 条目格式为 `(module_path, attr_name, short_help)`。

## 全局选项

```bash
octop [OPTIONS] COMMAND [ARGS]...
```

| 选项 | 环境变量 | 用途 |
|------|---------|------|
| `-v, --version` | — | 打印版本并退出 |
| `--user NAME` | `OCTOP_USER` | 默认操作用户（admin 代理用户） |
| `--agent ID` | `OCTOP_AGENT` | 默认 Agent |
| `--json` | — | 列表类命令输出机器可读 JSON |
| `-h, --help` | — | 显示帮助 |

来源：F-115。

这些选项存储在 `ctx.obj` 字典中，子命令通过 `click.pass_context` 访问。

## Windows UTF-8 兼容

`_ensure_utf8_stdio()` 在 CLI 启动时执行（F-117）：

- Windows 的 ANSI 代码页通常是 GBK（cp936），Python 用它编码管道/重定向的 stdout/stderr
- 非 GBK 字符（如 ✅/❌/QR art）会引发 `UnicodeEncodeError` 并在工作完成后杀死进程
- 解决方案：将 stdout/stderr 重配置为 UTF-8（`errors="replace"` 作为最后手段）
- 已是 UTF-8 的流跳过

## 20 个子命令

| # | 命令 | 模块 | 说明 | 传输层 |
|---|------|------|------|--------|
| 1 | `init` | `.commands.init` | 引导安装（DB 迁移、JWT 密钥、首个 admin） | Offline |
| 2 | `run` | `.commands.run` | 前台运行服务器（uvicorn） | External |
| 3 | `service` | `.commands.service` | 系统服务生命周期（start/stop/restart/status） | External |
| 4 | `config` | `.commands.config` | CLI 默认配置（pinned user/agent） | Offline |
| 5 | `user` | `.commands.user` | 用户管理（create/list/passwd/role/disable/delete/login） | Offline/Attach |
| 6 | `agent` | `.commands.agent` | Agent 生命周期（create/from-expert/list/use/start/stop/reload/delete/experts） | Offline/Embedded |
| 7 | `chats` | `.commands.chats` | 聊天 REPL 和会话管理 | Offline/Embedded |
| 8 | `channel` | `.commands.channel` | 通道管理（list/get/create/patch/delete/test/config/feishu-setup/bind） | Offline/Attach/External |
| 9 | `cron` | `.commands.cron` | 定时任务管理（list/create/delete/run-now） | Offline/Embedded |
| 10 | `provider` | `.commands.provider` | Provider 管理（list/create/delete/test） | Offline/Attach |
| 11 | `models` | `.commands.models` | 模型目录和激活模型（presets/list/active/config/ollama-*） | Offline/Attach/External |
| 12 | `skills` | `.commands.skills` | 技能启用/禁用（list/enable/disable/config） | Attach |
| 13 | `admin` | `.commands.admin` | 管理命令（overview/audit/providers/rotate-jwt-secret） | Offline |
| 14 | `version` | `.commands.version` | 显示版本 | Offline |
| 15 | `completion` | `.commands.completion` | Shell 补全（show/install） | Offline |
| 16 | `update` | `.commands.update` | 检查并安装新版本 | External |
| 17 | `clean` | `.commands.clean` | 清除 CLI 状态或擦除 ~/.octop | Offline |
| 18 | `backup` | `.commands.backup` | 备份和恢复（create/restore/auto） | Offline |
| 19 | `acp` | `.commands.acp` | ACP stdio 服务器 | Embedded |
| 20 | `plugin` | `.commands.plugin` | 插件管理（list/install/uninstall/reload） | Offline |

来源：F-116。

## 三层传输模型

CLI 命令根据操作需求选择三种传输层之一（F-120、I-04）：

### Offline（本地 DB 直读）

- **何时使用**：只需读写本地 `~/.octop` SQLite，无需运行中的服务器
- **需要登录**：否
- **示例**：`init`、`backup`、`plugin`、`agent list`、`chats list/get/create/update/delete`、`cron list/create/delete`、`user *`（除 login）、`admin overview/audit`、`models presets/list/active`、`provider list/create/delete`、`channel list/get/create/patch/delete/config`
- **实现**：通过 `cli/support/db.py` 的 `open_cli_services()` 直接打开 SQLite

### Embedded（进程内启动 OctopServer）

- **何时使用**：需要 harness/gateway 运行时，但不想启动完整 HTTP 服务器
- **需要登录**：否（本地文件系统信任）
- **示例**：`octop acp`、`octop chats repl`、`octop chats send`（默认）、`octop agent create/from-expert/start/stop/reload`、`cron run-now`、`provider test`、`channel test`、`skills list`
- **实现**：通过 `cli/support/embedded_ops.py` 在进程内构造 `OctopServer` 并 `start()`，命令完成后 `stop()`

### External（直接 OS/daemon 通信）

- **何时使用**：需要与操作系统或外部 daemon 直接交互
- **需要登录**：否
- **示例**：`models ollama-list/pull/rm`（直接 HTTP 调用本地 Ollama）、`channel bind`（QR 码登录 WeCom/WeChat）、`channel feishu-setup`（飞书 bot-creator 子进程）、`octop run`（uvicorn）、`octop service`（systemd/launchd）、`octop update`（pip）

### Attach（HTTP/WS，文档中也称 Attach）

CLI docs 中提到的 "Attach" 层需要运行中的 `octop run` 并通过 `octop user login` 获取 JWT：
- `chats send/repl`（某些模式）
- `channel test/probe`
- `models ollama-*`
- `skills enable/disable`
- `provider test`

## octop run 详解

### 选项

| 选项 | 默认 | 说明 |
|------|------|------|
| `--host` | config 或 127.0.0.1 | 绑定地址 |
| `--port` | config 或 8088 | 端口 |
| `--reload` | False | uvicorn 自动重载（开发模式） |
| `--workers` | 1 | Worker 进程数 |
| `--log-level` | config 或 info | critical/error/warning/info/debug/trace |
| `--ssl` | False | 启用 HTTPS |
| `--ssl-certfile` | None | TLS 证书文件 |
| `--ssl-keyfile` | None | TLS 私钥文件 |

来源：F-118。

### Host/Port 优先级

```
CLI flags > ~/.octop/config.json > launch 默认值
```

使用 `is not None`（而非 `or`）判断，以支持 falsy 但合法的值（如 port=0 随机端口、host="0"）。

当 CLI 传入 `--host` 或 `--port` 时，该覆盖会**持久化**到 config.json（原子写入：temp file + `os.replace`）（F-118）。

### SSL/TLS

`--ssl` 启用 HTTPS。若未提供 cert/key，自动生成自签名证书（F-119）：
- RSA 2048 位
- CN=`octop-self-signed`
- SAN=IP:127.0.0.1
- 有效期 365 天
- 存放于 `~/.octop/ssl/self_signed.crt` 和 `self_signed.key`

TLS 双端口模式（在 `launch.py` 中）同时监听 HTTPS 和 HTTP companion（ACME challenge + redirect），此时强制 `workers=1` 并禁用 reload。

## CLI 状态文件

`~/.octop/cli_state.json` 存储 CLI 状态（不与 Dashboard/HTTP 调用者共享）：

```json
{
  "base_url": "http://127.0.0.1:8088",
  "token": null,
  "default_user": null,
  "default_agent": null
}
```

- `base_url`：Attach 模式的服务器地址
- `token`：JWT 令牌（`octop user login` 获取）
- `default_user`：`octop config set-user` 固定的默认用户
- `default_agent`：`octop agent use` 固定的默认 Agent

路径可通过 `OCTOP_HOME` 覆盖。删除该文件可在不访问服务器的情况下登出 CLI。

## 模块边界

CLI 层不得导入 `api/`（F-129）。需要启动服务器时通过 `launch.run_foreground_blocking()` 间接使用 FastAPI。CLI 命令中的领域逻辑应委托给 `infra/`，而非在 CLI 中重复实现。

## 相关概念

- [/concepts/00-architecture.md](00-architecture.md)
- [/concepts/05-acp-protocol.md](05-acp-protocol.md)
- [/concepts/01-server-lifecycle.md](01-server-lifecycle.md)
