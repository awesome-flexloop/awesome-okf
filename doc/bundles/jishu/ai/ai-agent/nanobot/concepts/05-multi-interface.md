---
type: Concept
title: 多接口架构
description: nanobot 提供 CLI（Python）、TUI（Bun+TypeScript+OpenTUI）和 WebUI（React+Vite）三种用户接口，通过 WebSocket 协议与 Python 网关通信，共享同一 Agent 核心。
tags: [nanobot, cli, tui, webui, react, bun, typescript]
generated: { by: "reference_agent/trae-cn", at: 2026-08-23T10:00:00+08:00 }
status: stable
stale_after: 2027-08-23
sources:
  - id: src
    resource: /references/source.md
    title: nanobot 源码信源
---

# 多接口架构

nanobot 提供三种用户交互接口：经典 CLI（Python）、原生 TUI（Bun + TypeScript）和 WebUI（React + Vite）。它们共享同一个 Python Agent 核心，但通过不同的传输层和渲染技术提供差异化的用户体验。

## 接口对比

| 维度 | CLI（经典） | TUI（原生） | WebUI |
|------|-------------|-------------|-------|
| 启动命令 | `nanobot agent --classic` | `nanobot agent` | `nanobot webui` |
| 实现语言 | Python | TypeScript（Bun 运行） | TypeScript/TSX |
| UI 框架 | prompt-toolkit + Rich | @opentui/core 0.5.3 | React 18 + Radix UI |
| 与核心通信 | 进程内调用 / MessageBus | WebSocket | WebSocket + REST |
| 构建工具 | 无（解释执行） | Bun | Vite 5 |
| 适用场景 | 传统终端、脚本 | 现代终端体验 | 浏览器图形界面 |

## CLI 入口分层

### 入口分发

`nanobot/cli/entry.py` 实现了智能入口分发，根据命令行参数决定加载路径：

```python
def _native_tui_candidate(args: list[str]) -> bool:
    if not args or args[0] != "agent":
        return False
    for argument in args[1:]:
        if argument in {"--classic", "--no-tui", "-m", "--message"}:
            return False
        if argument.startswith("--message=") or (
            argument.startswith("-m") and not argument.startswith("--")
        ):
            return False
    return True

def main() -> None:
    _configure_windows_console()
    if _native_tui_candidate(sys.argv[1:]):
        import typer
        from nanobot.cli.agent import agent
        fast_app = typer.Typer(add_completion=False)
        fast_app.command()(agent)
        command = typer.main.get_command(fast_app)
        command.main(args=sys.argv[2:], prog_name="nanobot agent")
        return
    from nanobot.cli.commands import app
    app()
```

来源：`nanobot/cli/entry.py:10-51`

这种设计使得 `nanobot agent`（无参数）启动时不加载任何 LLM provider、工具注册表或 cron 服务代码。

### CLI Agent 命令

`nanobot/cli/agent.py` 的 `agent()` 函数使用 typer 定义选项：

```python
def agent(
    message: str | None = typer.Option(None, "--message", "-m"),
    session_id: str | None = typer.Option(None, "--session", "-s"),
    workspace: str | None = typer.Option(None, "--workspace", "-w"),
    config: str | None = typer.Option(None, "--config", "-c"),
    markdown: bool = typer.Option(True, "--markdown/--no-markdown"),
    logs: bool = typer.Option(False, "--logs/--no-logs"),
    classic: bool = typer.Option(False, "--classic", "--no-tui"),
    theme: str = typer.Option("auto", "--theme"),
):
```

来源：`nanobot/cli/agent.py:54-80`

TUI 模式要求交互式终端（`sys.stdin.isatty()`），不支持 `--no-markdown` 或 `--logs`。classic 模式支持单发消息（`-m`）和交互循环。

## TUI（终端 UI）

### 技术栈

TUI 是独立的 Bun/TypeScript 应用，包名 `@nanobot/tui`：

```json
{
  "name": "@nanobot/tui",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "start": "bun src/index.ts",
    "build": "bun scripts/build.ts",
    "check": "tsc --noEmit",
    "test": "bun test"
  },
  "dependencies": {
    "@opentui/core": "0.5.3"
  }
}
```

来源：`tui/package.json:1-14`

### NanobotTui 主类

`NanobotTui` 类位于 `tui/src/app.ts`，是终端 UI 的核心控制器。它组装了多个 UI 组件：

```typescript
export class NanobotTui {
  private readonly renderer: CliRenderer
  private readonly transcript: Transcript
  private readonly commandMenu: CommandMenu
  private readonly sessionMenu: SessionMenu
  private readonly mentionMenu: MentionMenu
  private readonly branchMenu: BranchMenu
  private readonly runtimeControls: RuntimeControls
  private readonly contextPanel: ContextPanel
  private readonly diffViewer: DiffViewer
  private readonly queuePreview: QueuePreview
  private readonly client: ChatClient
  // ...
}
```

来源：`tui/src/app.ts:372-391`

TUI 支持暗色和亮色主题，主色调为橙色：

```typescript
const DARK: Palette = {
  referenceBackground: "#0E0F11",
  text: "#ECEDEE",
  accent: "#EF8E30",
  // ...
}

const LIGHT: Palette = {
  referenceBackground: "#FAFAFA",
  text: "#18181B",
  accent: "#B94D0B",
  // ...
}
```

来源：`tui/src/app.ts:128-160`

### TUI 通信协议

TUI 通过 `tui/src/protocol.ts` 中定义的 `NanobotClient` 类与网关通信。协议定义了 17 种入站事件：

```typescript
export type InboundEvent =
  | { event: "ready"; chat_id: string; client_id: string }
  | { event: "attached"; chat_id: string; model_preset?: ...; usage?: ... }
  | { event: "message_accepted"; chat_id: string; turn_id: string; ... }
  | { event: "user_message"; chat_id: string; text: string; ... }
  | { event: "message"; chat_id: string; text: string; kind?: ...; ... }
  | { event: "file_edit"; chat_id: string; edits: FileEditEvent[]; ... }
  | { event: "delta"; chat_id: string; text: string; ... }
  | { event: "stream_end"; chat_id: string; ... }
  | { event: "reasoning_delta"; chat_id: string; text: string; ... }
  | { event: "reasoning_end"; chat_id: string; ... }
  | { event: "turn_end"; chat_id: string; ... }
  | { event: "goal_status"; chat_id: string; status: "running" | "idle"; ... }
  | { event: "goal_state"; chat_id: string; goal_state: ... }
  | { event: "session_updated"; chat_id: string; ... }
  | { event: "runtime_model_updated"; model_name: string; ... }
  | { event: "turn_model_updated"; chat_id: string; ... }
  | { event: "error"; chat_id?: string; ... }
```

来源：`tui/src/protocol.ts:57-135`

出站事件包括 `new_chat`、`fork_chat`、`attach`、`set_workspace_scope`、`message`：

```typescript
type OutboundEvent =
  | { type: "new_chat"; workspace_scope?: WorkspaceScopePayload }
  | { type: "fork_chat"; source_chat_id: string; before_user_index: number; title?: string }
  | { type: "attach"; chat_id: string }
  | { type: "set_workspace_scope"; chat_id: string; workspace_scope: WorkspaceScopePayload }
  | {
      type: "message"
      chat_id: string
      content: string
      turn_id: string
      webui: true
      cli_apps?: Array<{ name: string }>
      mcp_presets?: Array<{ name: string }>
      session_mentions?: SessionMention[]
    }
```

来源：`tui/src/protocol.ts:137-151`

`NanobotClient` 支持自动重连，采用指数退避策略（基础 500ms，最大 8 秒）：

```typescript
private scheduleReconnect(announce = true): void {
    const base = this.options.reconnectDelayMs ?? 500
    const maxDelay = this.connectedOnce ? 8_000 : ...
    const delay = Math.min(maxDelay, base * 2 ** Math.min(this.reconnectAttempt++, 4))
    this.reconnectTimer = setTimeout(() => {
        this.reconnectTimer = null
        void this.open()
    }, delay)
}
```

来源：`tui/src/protocol.ts:1007-1019`

### TUI Host 抽象

`tui/src/host.ts` 定义了 `TuiHost` 接口，支持两种运行环境：

```typescript
export interface TuiHost {
  readonly hosted: boolean
  reportState(state: HostAgentState, message?: string): void
  reportSession(sessionId: string): void
  reportMetadata(metadata: HostMetadata): void
  release(): void
}
```

- `StandaloneHost`：独立终端运行，所有报告方法为空操作
- `HerdrHost`：嵌入 Herdr 终端时，通过 CLI 命令报告代理状态、会话和元数据

`createTuiHost()` 工厂检查 `HERDR_ENV=1` 和 `HERDR_PANE_ID` 环境变量决定实现：

```typescript
export function createTuiHost(
  environment: Environment = process.env,
  run: CommandRunner = runCommand,
): TuiHost {
  const paneId = environment.HERDR_PANE_ID?.trim() || ""
  if (environment.HERDR_ENV !== "1" || !paneId) return new StandaloneHost()
  return new HerdrHost(paneId, environment.HERDR_BIN_PATH?.trim() || "herdr", run)
}
```

来源：`tui/src/host.ts:185-192`

### TUI 斜杠命令

TUI 内置本地斜杠命令：

| 命令 | 功能 |
|------|------|
| `/sessions` | 查找和切换对话 |
| `/new-chat` | 保存当前对话并开始新对话 |
| `/context` | 查看会话对下次提示的贡献 |
| `/diff` | 检查上一轮的文件变更 |
| `/branch` | 从之前的回复分叉 |
| `/detach` | 关闭 TUI 但保持代理运行 |
| `/exit` | 关闭 TUI |

来源：`tui/src/app.ts:167-210`

## WebUI

### 技术栈

WebUI 是基于 React 18 + Vite 5 的 SPA：

```json
{
  "name": "nanobot-webui",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "@radix-ui/react-*": "^1.1.x",
    "i18next": "^26.0.6",
    "react-i18next": "^17.0.4",
    "lucide-react": "^0.469.0",
    "streamdown": "2.5.0",
    "remark-gfm": "^4.0.0",
    "remark-math": "^6.0.0",
    "rehype-katex": "^7.0.1",
    "diff": "^9.0.0",
    "qrcode": "^1.5.4",
    "tailwind-merge": "^2.6.0"
  }
}
```

来源：`webui/package.json:1-38`

### App 状态机

`App.tsx` 的根组件管理四种启动状态：

```typescript
type BootState =
  | { status: "loading" }
  | { status: "error"; message: string }
  | { status: "auth"; failed?: boolean }
  | {
      status: "ready"
      client: NanobotClient
      token: string
      tokenExpiresAt: number | null
      modelName: string | null
      ingressLimits: BootstrapResponse["limits"] | null
      runtimeSurface: RuntimeSurface
    }
```

来源：`webui/src/App.tsx:90-102`

启动流程：
1. `loading`：调用 `fetchBootstrap()` 获取引导信息
2. `auth`：需要密钥时显示认证表单
3. `error`：引导失败时显示错误
4. `ready`：WebSocket 连接建立，渲染 Shell

引导成功后创建 `NanobotClient` 并连接：

```typescript
const client = new NanobotClient({
    url,
    maxFrameBytes: boot.limits?.transport.max_frame_bytes,
    socketFactory: runtimeHost.socketFactory,
    onReauth: async () => {
        const refreshed = await refreshReadyClient(client, runtimeSurface);
        return refreshed.url;
    },
});
client.connect();
```

来源：`webui/src/App.tsx:859-873`

### Shell 视图

WebUI Shell 支持五种主视图和 12 个设置分区：

```typescript
type ShellView = "chat" | "settings" | "apps" | "automations" | "skills"

const SETTINGS_SECTION_KEYS: SettingsSectionKey[] = [
  "overview", "appearance", "models", "image", "voice", "browser",
  "channels", "apps", "automations", "skills", "runtime", "advanced",
]
```

来源：`webui/src/App.tsx:118,159-172`

路由通过 URL hash 管理，支持 `/chat/<key>`、`/settings?section=`、`/apps`、`/automations`、`/skills`、`/temporary/<chatId>` 等路径。

### REST API 客户端

`webui/src/lib/api.ts` 提供完整的 REST API 客户端，所有请求使用 Bearer token 认证：

```typescript
async function request<T>(
  url: string,
  token: string,
  init?: RequestInit,
  timeoutMs: number = 0,
): Promise<T> {
  const res = await fetchWithTimeout(url, {
    ...(init ?? {}),
    headers: {
      ...(init?.headers ?? {}),
      Authorization: `Bearer ${token}`,
    },
    credentials: "same-origin",
  }, timeoutMs);
  if (!res.ok) {
    throw new ApiError(res.status, message || `HTTP ${res.status}`);
  }
  return (await res.json()) as T;
}
```

来源：`webui/src/lib/api.ts:82-128`

API 覆盖的功能域包括：

- 会话管理：`listSessions`、`deleteSession`、`fetchWebuiThread`、`fetchFilePreview`
- 设置：`fetchSettings`、`updateSettings`、`fetchWorkspaces`
- 模型配置：`createModelConfiguration`、`updateModelConfiguration`、`deleteModelConfiguration`
- 提供商：`updateProviderSettings`、`loginProviderOAuth`、`fetchProviderModels`
- 频道：`configureChannel`、`validateChannel`、`startChannelConnect`
- MCP：`fetchMcpPresets`、`saveCustomMcpServer`、`startMcpOAuth`
- 技能：`fetchSkills`、`installMarketplaceSkill`、`searchMarketplaceSkills`
- 自动化：`fetchAutomations`、`updateAutomation`、`runAutomationAction`
- 配对：`fetchPairingRequests`、`runPairingAction`
- 侧边栏状态：`fetchSidebarState`、`updateSidebarState`

来源：`webui/src/lib/api.ts:183-1099`

### 令牌刷新

WebUI 在令牌到期前自动刷新，使用 30 秒边距和最小 5 秒延迟：

```typescript
const TOKEN_REFRESH_MARGIN_MS = 30_000;
const TOKEN_REFRESH_MIN_DELAY_MS = 5_000;

function tokenRefreshDelayMs(expiresAt: number): number {
  const remaining = Math.max(0, expiresAt - Date.now());
  const margin = Math.min(
    TOKEN_REFRESH_MARGIN_MS,
    Math.max(1_000, remaining / 2),
  );
  return Math.max(TOKEN_REFRESH_MIN_DELAY_MS, remaining - margin);
}
```

来源：`webui/src/App.tsx:113-114,322-329`

## 共享网关模型

TUI 和 WebUI 共享一个按需本地网关：

- 任一启动器可启动网关
- 每个启动器仅释放自己的客户端租约
- 最后一个退出的交互式启动器停止网关
- `nanobot gateway --background` 将网关提升为持久后台模式

WebUI CLI 通过 `GatewayClientLease` 管理此生命周期：

```python
lease = GatewayClientLease(runtime, kind="webui")
lease.acquire()
try:
    ensure_shared_gateway(client_lease=lease)
    # ... 打开浏览器、附加到网关
finally:
    lease.release(wait_for_stop=False)
```

来源：`nanobot/cli/webui.py:232-329`

## WebUI 开发服务器

开发时，Vite dev server 在 `127.0.0.1:5173` 运行，代理 API/WS 流量到网关：

```python
WEBUI_DEV_HOST = "127.0.0.1"
WEBUI_DEV_PORT = 5173

def start_webui_dev_server(*, target_url, browser_url, ...):
    # ...
    child_env["NANOBOT_API_URL"] = target_url
    process = popen(command, cwd=resolved_source, env=child_env)
```

来源：`nanobot/webui/dev.py:19-20,161-167`

构建运行器优先使用 `bun`，不可用时回退到 `npm`。

## 相关概念

- [nanobot 简介](00-introduction.md)
- [整体架构](01-architecture.md)
- [消息总线与事件驱动](03-bus-messaging.md)
- [SDK 类型系统](04-sdk-types.md)
